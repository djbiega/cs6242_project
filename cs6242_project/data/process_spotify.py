import argparse
import json
import logging
import os
import time
from pathlib import Path
from requests.exceptions import ReadTimeout
from typing import List, TypedDict, Tuple, Union, Optional, Dict

import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fileHandler = logging.FileHandler("process_spotify.log")
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

class Track(TypedDict):
    pos: int
    artist_name: str
    track_uri: str
    artist_uri: str
    track_name: str
    album_uri: str
    duration: int
    album_name: str

class Playlist(TypedDict):
    name: str
    collaborative: str
    pid: int
    modified_at: int
    num_tracks: int
    num_albums: int
    num_followers: int
    tracks: List[Track]
    num_edits: int
    duration_ms: int
    num_artists: int

class TrackFeatures(TypedDict):
    popularity: Optional[float]
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    time_signature: int

def get_client() -> spotipy.Spotify:
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(
	auth_manager=auth_manager, 
	requests_timeout=10,
	retries=10,
	backoff_factor=3,
    )
    return sp

def get_tracks_and_features(
        playlists: List[Playlist]
    ) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
    track_uris = []
    spotify_features = {}
    for playlist in playlists:
        for song in playlist['tracks']:
            track_uri = song["track_uri"]
            track_uris.append(track_uri)
            spotify_features[track_uri] = {
                "artist_name": song["artist_name"],
                "track_name": song["track_name"],
                "album_name": song["album_name"],
            }
    return track_uris, spotify_features

def chunk_unique_tracks(track_uris: List[str]) -> List[np.ndarray]:
    MAX_TRACKS_IN_API_CALL=50

    # We only care about the unique track_uris
    track_uris = list(set(track_uris))

    # - spotipy tracks() api call has a max. of 50 track_uris that can be 
    # requested per API call 
    # - spotipy audio_features() api call has a max. of 100 track_uris that 
    # can be requested per API call
    num_chunks = np.ceil(len(track_uris) / MAX_TRACKS_IN_API_CALL)
    chunked_track_uris = np.array_split(track_uris, num_chunks)
    return chunked_track_uris

def add_features(
        spotify_client: spotipy.Spotify,
        track_uris: List[str], 
        track_features: Dict[str, TrackFeatures],
    ) -> Dict[str, TrackFeatures]:
    try:
        audio_features = spotify_client.audio_features(track_uris)
        track_response = spotify_client.tracks(track_uris)
        # Sometimes the track response returns a None type
        if 'tracks' not in track_response.keys():
            return track_features
        else:
            tracks = track_response['tracks']
        for idx, track_uri in enumerate(track_uris):
            # If there are no audio features, skip
            if not audio_features[idx]:
                continue
            # If there is no track info, set popularity to None
            track_features[track_uri] = {
                'popularity': tracks[idx]['popularity'] if tracks[idx] else None,
                'danceability': audio_features[idx]['danceability'],
                'energy': audio_features[idx]['energy'],
                'key': audio_features[idx]['key'],
                'loudness': audio_features[idx]['loudness'],
                'mode': audio_features[idx]['mode'],
                'speechiness': audio_features[idx]['speechiness'],
                'acousticness': audio_features[idx]['acousticness'],
                'instrumentalness': audio_features[idx]['instrumentalness'],
                'liveness': audio_features[idx]['liveness'],
                'valence': audio_features[idx]['valence'],
                'tempo': audio_features[idx]['tempo'],
                'duration_ms': audio_features[idx]['duration_ms'],
                'time_signature': audio_features[idx]['time_signature'],
            }
        return track_features
    # This is pretty hacky but feels safe enough since it's only catching on ReadTimeout
    except ReadTimeout:
        return add_features(spotify_client, track_uris, track_features)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str,
        help="Path to directory containing all mpd json files to iterate through"
    )
    parser.add_argument("output_path", type=str,
        help="Path to write output files to"
    )

    if "SPOTIPY_CLIENT_ID" not in os.environ:
        raise OSError("You must have your `SPOTIPY_CLIENT_ID` environment"
            " variable set to connect to the Spotify Client")

    if "SPOTIPY_CLIENT_SECRET" not in os.environ:
        raise OSError("You must have your `SPOTIPY_CLIENT_SECRET` environment"
            " variable set to connect to the Spotify Client")

    args = parser.parse_args()

    for f in os.listdir(args.input_path):
        if not f.startswith("mpd") or not f.endswith(".json"):
            logger.info("Skipping %s", f)
            continue

        input_file = Path(args.input_path)/f
        with open(input_file, "r") as mpd_file:
            data = json.load(mpd_file)  

        playlists = data['playlists']
        client = get_client()
        track_uris, spotify_features = get_tracks_and_features(playlists)
        chunked_track_uris = chunk_unique_tracks(track_uris)

        track_features = {}
        for chunk in chunked_track_uris:
            track_features = add_features(client, chunk, track_features)

        df = pd.DataFrame.from_dict(track_features, orient='index')
        spotify_df = pd.DataFrame.from_dict(spotify_features, orient='index')
        combined_df = spotify_df.join(df)
        combined_dict = combined_df.T.to_dict()

        output_file = Path(args.output_path)/f
        with open(output_file, "w") as outfile:
            json.dump(combined_dict, outfile, indent=4)
            logger.info("Processed %s", output_file)

if __name__ == '__main__':
   main() 

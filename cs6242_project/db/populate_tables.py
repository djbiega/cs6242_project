import json
import os

import psycopg2
from google.cloud import storage

from cs6242_project.db.config import config

CLIENT = storage.Client(project="CSE6242")
BUCKET = "cs6242_spotify"

def get_blobs_in_bucket():
    client = storage.Client(project="CSE6242")
    blobs = [blob for blob in client.list_blobs("cs6242_spotify")]
    return blobs

def load_blob(blob):
    # Appears to be some form of weird stochastic bug that happens randomly 
    for i in range(10):
        try:
            data = json.loads(blob.download_as_string())
        except:
            import time
            time.sleep(1)
            continue
        break
    return data

def insert_playlist(cur, playlists):
    cur.execute("INSERT INTO tracks VALUES " + playlists)

def insert_track(cur, all_tracks):
    cur.execute("INSERT INTO tracks VALUES " + all_tracks + " ON CONFLICT(track_uri) DO NOTHING")

def populate_tables():
    """ Insert data into tables """
    
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()

        blobs = get_blobs_in_bucket()
        for idx, blob in enumerate(blobs):
            print(f"Playlist number: {idx}")
            print(f"Inserting data from {blob.name}...")
            data = load_blob(blob)
            playlists = list(data['pid'])
            playlists_ints = [(i,) for i in list(map(int, data['pid']))]
            playlists_mogrified=','.join([cur.mogrify("(%s)", x).decode("utf-8") for x in playlists_ints])
            insert_playlist(cur, playlists_mogrified)
            all_tracks = []
            for p in playlists:
                tracks = data['pid'][p]
                for t, values in tracks.items():
                    ordered_vals = [
                        values["artist_name"],
                        values["track_name"],
                        values["album_name"],
                        values["popularity"],
                        values["danceability"],
                        values["energy"],
                        values["key"],
                        values["loudness"],
                        values["mode"],
                        values["speechiness"],
                        values["acousticness"],
                        values["instrumentalness"],
                        values["liveness"],
                        values["valence"],
                        values["tempo"],
                        values["duration_ms"],
                        values["time_signature"],
                    ]
                    if (t, *ordered_vals) not in all_tracks:
                        all_tracks.append((t, *ordered_vals))
            args_str = ','.join(
                cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x).decode("utf-8") for x in all_tracks
            )
            insert_track(cur, args_str)

        # close the communication with the PostgreSQL
        cur.close()
        # commit the chnages
        conn.commit()
        print("Data inserted successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

def populate_playlist_tracks():
    """ Insert data into tables """
    
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()

        all_tracks = []
        files = os.listdir("/opt/data/junction")
        for idx, fname in enumerate(files):
            print(f"Playlist number: {idx}")
            print(f"Inserting data from {fname}...")
            with open("/opt/data/junction/"+fname, "r") as f:
                data = json.load(f)
            playlists = list(data)
            for p in playlists:
                tracks = data[p]
                track_tuple = [(p, t) for t in tracks]
                all_tracks.extend(track_tuple)
            if idx % 50==0 and idx != 0:
                args_str = ','.join(
                    cur.mogrify("(%s,%s)", x).decode("utf-8") for x in all_tracks
                )
                cur.execute("INSERT INTO playlist_tracks VALUES " + args_str)
                all_tracks=[]

        args_str = ','.join(
            cur.mogrify("(%s,%s)", x).decode("utf-8") for x in all_tracks
        )
        cur.execute("INSERT INTO playlist_tracks VALUES " + args_str)

        # close the communication with the PostgreSQL
        cur.close()
        # commit the chnages
        conn.commit()
        print("Data inserted successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")


if __name__=="__main__":
    #populate_tables()
    populate_playlist_tracks()

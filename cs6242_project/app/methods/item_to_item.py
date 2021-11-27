"""
Item to item content based filtering
"""
from textwrap import dedent

import pandas as pd

def get_random_songs(engine):
    query = """
        SELECT
        t1.track_uri,
        t1.artist_name,
        t1.album_name,
        t1.popularity,
        t1.danceability,
        t1.energy,
        t1.loudness,
        t1.speechiness,
        t1.acousticness,
        t1.instrumentalness,
        t1.liveness,
        t1.valence,
        t1.tempo
    FROM tracks t1
    LIMIT 21;
    """
    recommendations = pd.read_sql(query, con=engine)
    recommendations["score"] = 1e-6
    recommendations["is_recommended"]=True
    return recommendations


def item_to_item(track, engine, cache):
    if track not in cache['tracks']:
        return get_random_songs(engine)
        
    
    query = """
        SELECT
            t1.track_uri,
            t1.artist_name,
            t1.album_name,
            t1.popularity,
            t1.danceability,
            t1.energy,
            t1.loudness,
            t1.speechiness,
            t1.acousticness,
            t1.instrumentalness,
            t1.liveness,
            t1.valence,
            t1.tempo,
            t2.score
        FROM tracks t1
        JOIN (
            SELECT track_uri, COUNT(junc.pid)*1.00 / pid_count AS score
            FROM playlist_tracks AS junc
            JOIN (
                SELECT junc_temp.pid, COUNT(pid) over () AS pid_count
                FROM playlist_tracks AS junc_temp
                WHERE track_uri='{}'
            ) temp_junc2 ON temp_junc2.pid = junc.pid AND junc.track_uri<>'{}'
            GROUP BY temp_junc2.pid_count, junc.track_uri
        ) t2 on t2.track_uri=t1.track_uri                                                                       
        ORDER BY t2.score DESC
        LIMIT 100;
    """.format(track, track)

    recommendations = pd.read_sql(query, con=engine)
    recommendations["is_recommended"]=True
    return recommendations


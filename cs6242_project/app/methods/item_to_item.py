"""
Item to item content based filtering
"""
import pandas as pd
from sklearn.decomposition import PCA

def item_to_item(track, engine):

    #params = config()
    #engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**params))

    pid_query = f"SELECT pid FROM playlist_tracks WHERE track_uri='{track['uri']}'"
    #TODO: what to do when pids is empty
    pids = pd.read_sql(pid_query, con=engine)["pid"].tolist()

    output_query = f"SELECT track_uri FROM playlist_tracks WHERE pid in {(*pids,)}"
    output_df = pd.read_sql(output_query, con=engine)
    track_counts = output_df["track_uri"].value_counts()
    jaccard = {i: track_counts[i]/sum(track_counts.tolist()) for i in track_counts.index}

    #top_uris = sorted(jaccard, key=jaccard.get, reverse=True)

    recommendation_query = f"SELECT * FROM tracks WHERE track_uri in {(*jaccard,)}"
    #recommendations = pd.read_sql(recommendation_query, con=engine).T.to_dict()
    recommendations = pd.read_sql(recommendation_query, con=engine)
    recommendations["score"] = recommendations["track_uri"].map(jaccard)
    return recommendations

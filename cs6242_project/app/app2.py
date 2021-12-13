import pandas as pd
pd.options.mode.chained_assignment = None
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from joblib import load
from random import sample
from cs6242_project.app.methods.distance_based import distance_based_recommendation
from cs6242_project.db.config import config

app2 = Flask(__name__)
app2.config["DEBUG"] = True

# import pre-trained kmeans and fitted pca
kmeans = load("model_cluster.joblib")
pca = load("database_pca.joblib")

# connect to the PostgreSQL database
params = config()
engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**params))
# load entire database into memory
query = "SELECT * FROM tracks"
track_df = pd.read_sql(query, con=engine).set_index("track_uri", drop=True)

# slice database frame based on significant features in first two components of pca
pca_cols = ["danceability", "energy", "acousticness", "instrumentalness", "tempo", "duration_ms"]
db_features = track_df[pca_cols]

# fit scaler to features frame and transform features
scaler = StandardScaler().fit(db_features)
db_features_scaled = pd.DataFrame(data=scaler.transform(db_features[db_features.columns]),
                                  index=db_features.index, columns=db_features.columns)

# cluster features dataframe
db_features_scaled["cluster_number"] = kmeans.predict(db_features_scaled.values).astype("uint8")

dummy_input = [
    {
        'track_uri': 'spotify:track:2lny7NHrxAIpEhiQVjIkPB',
        'artist_name': 'H.G. Wells',
        'track_name': 'Chapter 15',
        'album_name': 'Time Machine',
        'popularity': 13.0,
        'danceability': 0.668,
        'energy': 0.189,
        'key': 5.0,
        'loudness': -28.807,
        'mode': 1.0,
        'speechiness': 0.947,
        'acousticness': 0.756,
        'instrumentalness': 0.0,
        'liveness': 0.415,
        'valence': 0.542,
        'tempo': 87.951,
        'duration_ms': 313812.0,
        'time_signature': 3.0
    }
]

dummy_input_frame = pd.DataFrame(dummy_input).set_index("track_uri")
dummy_input_features = dummy_input_frame[pca_cols]
dummy_input_features_scaled = pd.DataFrame(data=scaler.transform(dummy_input_features[dummy_input_features.columns]),
                                           index=dummy_input_features.index, columns=dummy_input_features.columns)
x_input = dummy_input_features_scaled.values


@app2.route("/distance_based", methods=["GET"])
def distance_based_method():
    TOP_K = 20
    result = set()
    for x in x_input:
        # assign input to its cluster
        label = kmeans.predict(x.reshape(1, -1))
        # find cluster members of the input
        cluster_members = db_features_scaled[db_features_scaled["cluster_number"] == label[0]].iloc[:, :-1]
        # select closest to input from its cluster members
        res = distance_based_recommendation(cluster_members, x.reshape(1, -1))
        result.update(res)
    if len(result) > TOP_K:
        playlist_track_ids = sample(list(result), TOP_K)

    playlist_sorted = sorted(playlist_track_ids, key=lambda ele: ele[1], reverse=True)
    playlist_tracks_uri = [ele[0] for ele in playlist_sorted]
    playlist_tracks_score = [ele[1] for ele in playlist_sorted]

    recommendations = track_df.loc[playlist_tracks_uri].reset_index().rename(
        columns={"artist_name": "artist", "track_name": "track", "album_name": "album"})
    recommendations.loc[:, "x"] = pca.transform(db_features_scaled.loc[playlist_tracks_uri].iloc[:, :-1].values)[:, 0]
    recommendations.loc[:, "y"] = pca.transform(db_features_scaled.loc[playlist_tracks_uri].iloc[:, :-1].values)[:, 1]
    recommendations.loc[:, "score"] = playlist_tracks_score
    recommendations.loc[:, "is_recommended"] = True
    dummy_input_frame.reset_index(inplace=True).rename(
        columns={"artist_name": "artist", "track_name": "track", "album_name": "album"}, inplace=True)
    dummy_input_frame.loc[:, "x"] = pca.transform(dummy_input_features_scaled.values)[:, 0]
    dummy_input_frame.loc[:, "y"] = pca.transform(dummy_input_features_scaled.values)[:, 1]
    dummy_input_frame.loc[:, "is_recommended"] = False
    dummy_input_frame.loc[:, "similarity_score"] = 1.0
    return pd.concat((dummy_input_frame, recommendations)).to_dict('records')


@app2.route("/", methods=["GET"])
def hello_world():
    return jsonify({"Output": "Hello from the otherside"})

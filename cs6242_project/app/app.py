import pandas as pd
pd.options.mode.chained_assignment = None
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from joblib import load
from random import sample
from cs6242_project.app.methods.item_to_item import item_to_item
from cs6242_project.app.methods.distance_based import distance_based_recommendation
from cs6242_project.db.config import config

app = Flask(__name__)
app.config["DEBUG"]=True
CORS(app)

# import pre-trained kmeans and fitted pca
kmeans = load("model_cluster.joblib")
pca = load("database_pca.joblib")

# connect to the PostgreSQL database
params = config()
engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**params))

#TODO: This should be a proper Cache using Flask-Caching and/or Redis
cache_query = "SELECT track_uri FROM tracks"
CACHE = {"tracks": pd.read_sql(cache_query, con=engine)['track_uri'].to_list()}

# load entire database into memory
query = "SELECT * FROM tracks"
track_df = pd.read_sql(query, con=engine).set_index("track_uri", drop=True)

dummy_inputs = [
    {
        "acousticness": 0.101,
        "album": "The Best In The World Pack",
        "analysis_url": "https://api.spotify.com/v1/audio-analysis/5ry2OE6R2zPQFDO85XkgRb",
        "artist": "Drake",
        "danceability": 0.831,
        "duration_ms": 205427,
        "energy": 0.502,
        "id": "5ry2OE6R2zPQFDO85XkgRb",
        "instrumentalness": 0,
        "key": 10,
        "liveness": 0.122,
        "loudness": -4.045,
        "mode": 0,
        "name": "Money In The Grave (Drake ft. Rick Ross)",
        "speechiness": 0.046,
        "tempo": 100.541,
        "time_signature": 4,
        "track_href": "https://api.spotify.com/v1/tracks/5ry2OE6R2zPQFDO85XkgRb",
        "track_uri": "spotify:track:5ry2OE6R2zPQFDO85XkgRb",
        "type": "audio_features",
        "valence": 0.101,
    },
    {
        "acousticness": 0.0206,
        "album": "Run It (feat. Rick Ross & Rich Brian)",
        "analysis_url": "https://api.spotify.com/v1/audio-analysis/282R6Lvm9nLtpx8AzUwJe0",
        "artist": "DJ Snake",
        "danceability": 0.688,
        "duration_ms": 163390,
        "energy": 0.725,
        "id": "282R6Lvm9nLtpx8AzUwJe0",
        "instrumentalness": 0.00000918,
        "key": 2,
        "liveness": 0.0859,
        "loudness": -7.831,
        "mode": 1,
        "name": "Run It (feat. Rick Ross & Rich Brian)",
        "speechiness": 0.0456,
        "tempo": 104.018,
        "time_signature": 4,
        "track_href": "https://api.spotify.com/v1/tracks/282R6Lvm9nLtpx8AzUwJe0",
        "track_uri": "spotify:track:282R6Lvm9nLtpx8AzUwJe0",
        "type": "audio_features",
        "valence": 0.224,
    }
]


DF_COLUMNS = [
    "track_uri",
    "track_name",
    "name",
    "artist",
    "album",
    "popularity",
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "score",
]

# slice database frame based on significant features in first two components of pca
PCA_COLUMNS = [
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "tempo",
    "duration_ms"
]

db_features = track_df[PCA_COLUMNS]
# fit scaler to features frame and transform features
scaler = StandardScaler().fit(db_features)
db_features_scaled = pd.DataFrame(data=scaler.transform(db_features[db_features.columns]),
                                  index=db_features.index, columns=db_features.columns)

# cluster features dataframe
db_features_scaled["cluster_number"] = kmeans.predict(db_features_scaled.values).astype("uint8")

dummy_input_frame = pd.DataFrame(dummy_inputs).set_index("track_uri")
dummy_input_features = dummy_input_frame[PCA_COLUMNS]
dummy_input_features_scaled = pd.DataFrame(data=scaler.transform(dummy_input_features[dummy_input_features.columns]),
                                           index=dummy_input_features.index, columns=dummy_input_features.columns)
x_input = dummy_input_features_scaled.values

NUMERIC_COLUMNS = [*PCA_COLUMNS, "score"]


@app.route("/item_to_item", methods=["GET", "POST"])
def item_to_item_method():
    #TODO: What should this be?
    TOP_K=20 
    pca = PCA(n_components=2)

    input_data = request.json["songs"]
    
    filtered_input = []
    for req in input_data:
        filtered_input.append({k:v for k,v in req.items() if k in DF_COLUMNS})

    input_df = pd.DataFrame.from_records(filtered_input)
    input_df = input_df.set_index("track_uri")
    input_df["is_recommended"] = False
    input_df["popularity"] = 0 #FIXME: Input data doesn't include popularity
    
    outputs = []
    outputs_df = pd.DataFrame(columns=DF_COLUMNS)

    for message in filtered_input:
        track = message.get("track_uri")
        outputs.append(item_to_item(track, engine, CACHE))
    outputs_df = pd.concat(outputs)
    outputs_df = outputs_df.rename(
            columns={"album_name": "album", "artist_name": "artist", "track_name": "name"}
    )
    temp_df = outputs_df[outputs_df.columns[~outputs_df.columns.isin(NUMERIC_COLUMNS)]].set_index("track_uri")
    temp_df = temp_df.drop_duplicates()
    outputs_df = outputs_df.groupby("track_uri")[NUMERIC_COLUMNS].mean()
    outputs_df = temp_df.join(outputs_df)
    combined_df = pd.concat([input_df, outputs_df])

    pca_df = combined_df[PCA_COLUMNS]
    pca.fit(pca_df)
    pca_outputs = pca.transform(pca_df)
    combined_df["x"] = pca_outputs[:,0]
    combined_df["y"] = pca_outputs[:,1]

    original_df = combined_df.loc[combined_df["is_recommended"]==False]
    original_df["score"] = 0
    combined_df = combined_df.sort_values(by=["score"], ascending=False).head(TOP_K)
    final_df = pd.concat([combined_df, original_df])

    # If there are any NoNs for whatever reason, convert to None so jsonify can convert to valid json
    final_df = final_df.where(pd.notnull(final_df), None)
    final_df = final_df.reset_index()
    
    response = jsonify(final_df.T.to_dict())
    return response


@app.route("/distance_based", methods=["GET", "POST"])
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


@app.route("/", methods=["GET", "POST"])
def hello_world():
    response = jsonify({"Output": "Hello from the otherside"})
    return response
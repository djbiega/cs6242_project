import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine
from sklearn.decomposition import PCA

from cs6242_project.app.methods.item_to_item import item_to_item
from cs6242_project.db.config import config

app = Flask(__name__)
app.config["DEBUG"]=True
CORS(app)

# connect to the PostgreSQL database
params = config()
engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**params))

#TODO: This should be a proper Cache using Flask-Caching and/or Redis
cache_query = "SELECT track_uri FROM tracks"
CACHE = {"tracks": pd.read_sql(cache_query, con=engine)['track_uri'].to_list()}

dummy_inputs=[
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

PCA_COLUMNS = [
    #"popularity", #FIXME: Include only if it is sent in th einput data
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]

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
    

@app.route("/", methods=["GET", "POST"])
def hello_world():
    response = jsonify({"Output": "Hello from the otherside"})
    return response

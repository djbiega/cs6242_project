import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import create_engine

from cs6242_project.app.methods.item_to_item import item_to_item
from cs6242_project.db.config import config

app = Flask(__name__)
app.config["DEBUG"]=True

# connect to the PostgreSQL database
params = config()
engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**params))


dummy_inputs = [
    {
        "0": {
            "acousticness": 0.0209,
            "album": "Do It To It",
            "analysis_url": "https://api.spotify.com/v1/audio-analysis/20on25jryn53hWghthWW3",
            "artist": "ACRAZE",
            "danceability": 0.854,
            "duration_ms": 157890,
            "energy": 0.806,
            "id": "20on25jryn53hWghthWW3",
            "instrumentalness": 0.0542,
            "key": 11,
            "liveness": 0.0703,
            "loudness": -8.262,
            "mode": 0,
            "name": "Do It To It",
            "speechiness": 0.0886,
            "tempo": 124.927,
            "time_signature": 4,
            "track_href": "https://api.spotify.com/v1/tracks/20on25jryn53hWghthWW3",
            "type": "audio_feaures",
            "uri": "spotify:track:6l9HDwqU46DHCuNyvbmFdP",
            "valence": 0.637,
        }
    }
]
#        "1": {
#            "acousticness": 0.0509,
#            "album": "Temp Do It To It",
#            "analysis_url": "https://api.spotify.com/v1/audio-analysis/20on25jryn53hWghthWW3Temp",
#            "artist": "ACRAZE",
#            "danceability": 0.824,
#            "duration_ms": 157309,
#            "energy": 0.384,
#            "id": "20on25jnon57hWghthWW3",
#            "instrumentalness": 0.0893,
#            "key": 10,
#            "liveness": 0.0993,
#            "loudness": -4.382,
#            "mode": 0,
#            "name": "Temp Do It To It",
#            "speechiness": 0.0294,
#            "tempo": 122.398,
#            "time_signature": 4,
#            "track_href": "https://api.spotify.com/v1/tracks/20on25jryn53hWghthWW3Temp",
#            "type": "audio_feaures",
#            "uri": "spotify:track:20on25jryn53hWghthWW3",
#            "valence": 0.384,
#        }
#    },
#]

@app.route("/item_to_item", methods=["GET"])
def item_to_item_method():
    #TODO: What should this be?
    TOP_K=20 

    outputs = []
    pca_df = pd.DataFrame(dummy_inputs[0].values())
    for k, track in dummy_inputs[0].items():
        outputs.append(item_to_item(track, engine))
    top_k_outputs = sorted(outputs, key=lambda d: d["score"], reverse=True)[:TOP_K]
    #TODO: PCA stuff
    return jsonify(top_k_outputs[0].T.to_dict())

@app.route("/", methods=["GET"])
def hello_world():
    return jsonify({"Output": "Hello from the otherside"})

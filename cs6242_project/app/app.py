from flask import Flask, request, jsonify

from cs6242_project.app.methods.item_to_item import item_to_item

app = Flask(__name__)
app.config["DEBUG"]=True

recommendations = [
    {
        "track_uri": "spotify:track:abc123",
        "metric1": "MetricOne",
        "metric2": "MetricTwo",
    },
    {
        "track_uri": "spotify:track:def456",
        "metric1": "metric_one",
        "metric2": "metric_two",
    },
]

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
            "uri": "spotify:track:20on25jryn53hWghthWW3",
            "valence": 0.637,
        }
    },
]

@app.route("/", methods=["GET"])
def hello_world():
    print(item_to_item([]))
    return jsonify(recommendations)

import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sklearn.decomposition import PCA

from cs6242_project.app.methods.item_to_item import item_to_item
from cs6242_project.db.config import config

app = Flask(__name__)
app.config["DEBUG"]=True

# connect to the PostgreSQL database
params = config()
engine = create_engine("postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(**params))


dummy_inputs = [
    {
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
        "track_uri": "spotify:track:6l9HDwqU46DHCuNyvbmFdP",
        "valence": 0.637,
    },
    {
        'track_uri': 'spotify:track:6I9VzXrHxO9rA9A5euc8Ak',
        'artist_name': 'Britney Spears',
        'track_name': 'Toxic',
        'album_name': 'In The Zone',
        'popularity': 82.0,
        'danceability': 0.774,
        'energy': 0.838,
        'key': 5.0,
        'loudness': -3.914,
        'mode': 0.0,
        'speechiness': 0.114,
        'acousticness': 0.0249,
        'instrumentalness': 0.025,
        'liveness': 0.242,
        'valence': 0.924,
        'tempo': 143.04,
        'duration_ms': 198800.0,
        'time_signature': 4.0
    },
    {
        'track_uri': 'spotify:track:0WqIKmW4BTrj3eJFmnCKMv',
        'artist_name': 'Beyoncé',
        'track_name': 'Crazy In Love',
        'album_name': 'Dangerously In Love (Alben für die Ewigkeit)',
        'popularity': 24.0,
        'danceability': 0.664,
        'energy': 0.758,
        'key': 2.0,
        'loudness': -6.583,
        'mode': 0.0,
        'speechiness': 0.21,
        'acousticness': 0.00238,
        'instrumentalness': 0.0,
        'liveness': 0.0598,
        'valence': 0.701,
        'tempo': 99.259,
        'duration_ms': 235933.0,
        'time_signature': 4.0
    },
    {
        'track_uri': 'spotify:track:1AWQoqb9bSvzTjaLralEkT',
        'artist_name': 'Justin Timberlake',
        'track_name': 'Rock Your Body',
        'album_name': 'Justified',
        'popularity': 76.0,
        'danceability': 0.892,
        'energy': 0.714,
        'key': 4.0,
        'loudness': -6.055,
        'mode': 0.0,
        'speechiness': 0.141,
        'acousticness': 0.201,
        'instrumentalness': 0.000234,
        'liveness': 0.0521,
        'valence': 0.817,
        'tempo': 100.972,
        'duration_ms': 267267.0,
        'time_signature': 4.0
    },
    {
        'track_uri': 'spotify:track:1lzr43nnXAijIGYnCT8M8H',
        'artist_name': 'Shaggy',
        'track_name': "It Wasn't Me",
        'album_name': 'Hot Shot',
        'popularity': 3.0,
        'danceability': 0.853,
        'energy': 0.606,
        'key': 0.0,
        'loudness': -4.596,
        'mode': 1.0,
        'speechiness': 0.0713,
        'acousticness': 0.0561,
        'instrumentalness': 0.0,
        'liveness': 0.313,
        'valence': 0.654,
        'tempo': 94.759,
        'duration_ms': 227600.0,
        'time_signature': 4.0
    }
]


DF_COLUMNS = [
    "track_uri",
    "artist_name",
    "album_name",
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
]

NUMERIC_COLUMNS = [*PCA_COLUMNS, "score"]

@app.route("/item_to_item", methods=["GET", "POST"])
def item_to_item_method():
    #TODO: What should this be?
    TOP_K=20 
    pca = PCA(n_components=2)

    #request_data = request.args #FIXME make me work
    #input_df = pd.DataFrame(request_data) #FIXME make me work
    
    filtered_input = []
    #for req in request_data:
    for req in dummy_inputs:#FIXME replace with real data 
        filtered_input.append({k:v for k,v in req.items() if k in DF_COLUMNS})

    input_df = pd.DataFrame.from_records(filtered_input)
    input_df = input_df.set_index("track_uri")
    input_df["is_recommended"] = False
    
    outputs = []
    outputs_df = pd.DataFrame(columns=DF_COLUMNS)

    #FIXME: This may not work - need to figure out data structure of received request
    #for message in request_data: 
    for message in filtered_input: #FIXME replace with real data 
        track = message.get("track_uri")
        outputs.append(item_to_item(track, engine))
    outputs_df = pd.concat(outputs)
    temp_df = outputs_df[outputs_df.columns[~outputs_df.columns.isin(NUMERIC_COLUMNS)]].set_index("track_uri")
    outputs_df = outputs_df.groupby("track_uri")[NUMERIC_COLUMNS].mean()
    outputs_df = outputs_df.join(temp_df)
    combined_df = pd.concat([input_df, outputs_df])

    # Drop where popularity is none bc for some dumb reason I didn't excluse those in the database
    combined_df = combined_df[combined_df['popularity'].notna()]

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
    
    return jsonify(final_df.T.to_dict())
    

@app.route("/", methods=["GET", "POST"])
def hello_world():
    response = jsonify({"Output": "Hello from the otherside"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

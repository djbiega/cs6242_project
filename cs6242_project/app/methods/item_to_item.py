"""
Item to item content based filtering
"""
import pandas as pd
import psycopg2
from sklearn.decomposition import PCA

from cs6242_project.db.config import config

def item_to_item(message):
    # read connection parameters
    params = config()

    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
            
    # create a cursor
    cur = conn.cursor()
    query = "SELECT * FROM tracks LIMIT 1"
    df = pd.read_sql(query, conn)
    print(df)


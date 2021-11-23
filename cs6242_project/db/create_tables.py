import psycopg2

from cs6242_project.db.config import config

def create_tables():
    """ Create tables for spotify database """

    commands = (
        """
        CREATE TABLE playlists (
            pid INTEGER PRIMARY KEY
        )
        """,
        """
        CREATE TABLE tracks (
            track_uri VARCHAR(500) PRIMARY KEY,
            artist_name VARCHAR(500),
            track_name VARCHAR(500),
            album_name VARCHAR(500),
            popularity NUMERIC,
            danceability NUMERIC,
            energy NUMERIC,
            key NUMERIC,
            loudness NUMERIC,
            mode NUMERIC,
            speechiness NUMERIC,
            acousticness NUMERIC,
            instrumentalness NUMERIC,
            liveness NUMERIC,
            valence NUMERIC,
            tempo NUMERIC,
            duration_ms NUMERIC,
            time_signature NUMERIC
        )
        """,
        """
        CREATE TABLE playlist_tracks (
            pid INTEGER NOT NULL,
            track_uri VARCHAR(500) NOT NULL,
            PRIMARY KEY (pid, track_uri),
            FOREIGN KEY (pid)
                REFERENCES playlists (pid)
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (track_uri)
                REFERENCES tracks (track_uri)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
    )

    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        print("Creating tables...")
        for command in commands:
            cur.execute(command)


        # close the communication with the PostgreSQL
        cur.close()
        # commit the chnages
        conn.commit()
        print("Tables created successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__=="__main__":
    create_tables()

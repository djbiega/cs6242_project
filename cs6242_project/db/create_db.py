import psycopg2

from cs6242_project.db.config import config

def create_db():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Creating the spotify database...')
        params["database"] = "postgres" # hard-code since the database doesn't exist yet
        conn = psycopg2.connect(**params)
        conn.autocommit = True
		
        # create a cursor
        cur = conn.cursor()
        
	# execute a statement
        sql = '''CREATE database spotify''';
        cur.execute(sql)
        print("Database created successfully ...")

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")

if __name__=="__main__":
    create_db()

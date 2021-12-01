# cs6242_project


# Getting Started

### Submodules
First you need to pull down all the submodules of this repo. Run the command `git submodule update --init --recursive`

### Docker
There are currently three Dockerfile's in the project: 1 that was used for pulling
the data from spotify, another for running the Flask server, and a third for 
running the postgres database. To orchestrate how these are built, we're using 
docker-compose. You will probably need to download this. To run both services, 
you can run `docker-compose up`. After running this, if you want to enter an 
interactive shell to run the data  collection stuff, run 
`docker-compose run data_collection bash`

### Jupyter Notebooks
Jupyter notebooks can be accessed from within the docker container by running
* `jupyter-notebook --ip=0.0.0.0`

### Database
Our infrastructure uses docker-compose to build isolated containers. If you don't
have it, then download it. With docker-compose first run `docker-compose build`
to build all the images initially. This may take awhile the first time you run this.

To create the database, just run `docker-compose up -d db`, which will start
a docker container which hosts the database in the background. You should see it 
if you type `docker ps`. The first time you create the database, you'll need to 
populate the database. To do this, download the .sql script from 
https://drive.google.com/file/d/1K_3bWS93Gmv_-idEaKHOXbU6djsq8pKk/view?usp=sharing and
then run `cat /path/to/spotify_backup.sql | docker exec -i cs6242_project_db_1 psql -U postgres`.
This will populate the database and set things up such that the data will persist even when you stop and start the container

#### Debugging
To enter into `psql` within the container, run `docker exec -i cs6242_project_db_1 psql -U postgres`.
If you type `\l` you should see a `spotify` database. Connect to it with `\c spotify`. 
To list the tables, type `\dt`. Verify that the tables have data in them with 
`select count(*) from playlist;`. This table should have 1000 rows.

To enter into the running Flask server, run `docker exec -it cs6242_project_app_1 bash` to enter the container within a bash shell. If you would like to enter start up a jupyter notebook within this container, enter a bash shell and then `pip install notebook`. You can access the container with `jupyter-notebook --ip=0.0.0.0` at `localhost:8888`.

# Running the app
Once all servics at started with `docker-compose up`, you can access the web application at `localhost:3000`
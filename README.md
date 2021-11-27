# cs6242_project


## Getting Started

### Submodules
First you need to pull down all the submodules of this repo. Run the command `git submodule update --init --recursive`

### Docker
There is a Dockerfile with pulls from the ubuntu:20.04 image that should be 
flexible enough for our needs. There is a supplementary Makefile provided to 
provide easy access to common docker commands:
* `$ make build-docker`:
    * Build the docker image
* `$ make start-docker`:
    * Start a docker container from a previously built image
* `$ make log-into-docker`:
    * Log into the previously started docker container
* `$ make stop-docker`:
    * Stop the docker container

There are currently two Dockerfile's in the project: 1 that was used for pulling
the data from spotify and another than is meant to run the postgres database. To
orchestrate how these are built, I'm using docker-compose. You will probably
need to download this. To run both services, you can run `docker-compose up`.
After running this, if you want to enter an interactive shell to run the data 
collection stuff, run `docker-compose run data_collection bash`

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
https://drive.google.com/file/d/1pB1hmjan_K_hQaWWZCm-3fnIC2nHpfr2/view?usp=sharing and
then run `cat /path/to/spotify_backup.sql | docker exec -i cs6242_project_db_1 psql -U postgres`.
This should populate the database and the docker-compose should have things set up 
such that the data will persist even when you sotp and start the container (Not tested
but I think this will persist).

To enter into `psql` within the container, run `docker exec -i cs6242_project_db_1 psql -U postgres`.
If you type `\l` you should see a `spotify` database. Connect to it with `\c spotify`. 
To list the tables, type `\dt`. Verify that the tables have data in them with 
`select count(*) from playlist;`. This table should have 1000 rows.


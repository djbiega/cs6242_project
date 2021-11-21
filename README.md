# cs6242_project


## Getting Started

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
To create the database, just run `docker-compose up -d db`, which will start
a docker container which hosts the database in the backgroun. To enter into 
`psql` within the container, run `psql -h localhost -p 5432 -U postgres`


* Create the database with `CREATE DATABASE spotify;` 
* Add `database.ini` file as shown below:
```
[postgresql]
host=localhost
database=suppliers
user=postgres
password=SecurePas$1 
```

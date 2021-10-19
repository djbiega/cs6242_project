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

### Jupyter Notebooks
Jupyter notebooks can be accessed from within the docker container by running
* `jupyter-notebook --ip=0.0.0.0`
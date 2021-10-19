IMAGE_NAME := cs6242_image
CONTAINER_NAME := cs6242_container
CODE_HOME := /opt/cs6242_home

.PHONY: build-docker start-docker log-into-docker stop-docker

build-docker:
	@echo "Building docker image"
	@DOCKER_BUILDKIT=1 docker build . -f docker/Dockerfile -t $(IMAGE_NAME)

start-docker:
	@echo "Running docker image as a container"
	@docker run -di -p 8888:8888 -p 6006:6006 \
		--rm \
		--mount type=bind,source=$(PWD),target=$(CODE_HOME) \
		--hostname $(CONTAINER_NAME) \
		--name $(CONTAINER_NAME) $(IMAGE_NAME)
	@docker exec -w $(CODE_HOME) -it $(CONTAINER_NAME) bash -c 'pip install --user -e .; exit $$?'
	@echo "Successfully created docker container. Access the shell with 'make log-into-docker'"

log-into-docker:
	@docker exec -w $(CODE_HOME) -it $(CONTAINER_NAME) /bin/bash

stop-docker:
	@docker stop -t 5 $(CONTAINER_NAME)

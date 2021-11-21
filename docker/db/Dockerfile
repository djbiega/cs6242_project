# syntax=docker/dockerfile:experimental
FROM postgres
COPY init.sql /docker-entrypoint-initdb.d/

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \ 
        curl \
        ca-certificates \ 
        build-essential \ 
        git \
        sudo \
        python3 \
        python3-dev \
        python3-distutils \
        python3-tk \
        libboost-all-dev \ 
        libgl1-mesa-glx \ 
        libpq-dev && \
    rm -rf /var/lib/apt/lists*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \ 
    curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \ 
    rm get-pip.py

RUN pip install --upgrade pip 

RUN pip uninstall psycopg2 && \ 
    pip install --upgrade wheel && \
    pip install --upgrade setuptools && \
    pip install psycopg2

ENV PATH=$PATH:/home/docker/.local/bin

RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER docker

RUN sudo apt-get update

EXPOSE 5432

WORKDIR /opt/cs6242_home


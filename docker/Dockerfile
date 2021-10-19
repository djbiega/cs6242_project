# syntax=docker/dockerfile:experimental
FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \ 
        curl \
        ca-certificates \ 
        build-essential \ 
        git \
        sudo \
        python3.8 \
        python3.8-dev \
        python3.8-distutils \
        python3.8-tk \
        libboost-all-dev \ 
        libgl1-mesa-glx \ 
        vim && \ 
    rm -rf /var/lib/apt/lists*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \ 
    curl -fSsL -O https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \ 
    rm get-pip.py

ENV PATH=$PATH:/home/docker/.local/bin

RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER docker

RUN sudo apt-get update 

WORKDIR /opt/cs6242_home

RUN pip install --upgrade pip 

CMD /bin/bash

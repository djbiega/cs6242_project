#!/bin/sh

cd /opt/cs6242_home

pip install --user -e .[data_collection] 

exec "$@"


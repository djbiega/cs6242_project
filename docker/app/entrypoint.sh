#!/bin/sh

cd /opt/cs6242_home

pip install --user -e .[app] 

export FLASK_APP=/opt/cs6242_home/cs6242_project/app/app.py

flask run -h 0.0.0.0

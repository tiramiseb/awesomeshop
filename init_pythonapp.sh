#!/bin/sh

sudo apt-get install libjpeg-dev libpng-dev
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt

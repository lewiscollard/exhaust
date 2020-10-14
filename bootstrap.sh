#!/bin/sh
# Quickstart initialisation.
rm -rf .venv
rm -rf node_modules
virtualenv -p python3.6 .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
yarn
./manage.py generate_secret_key

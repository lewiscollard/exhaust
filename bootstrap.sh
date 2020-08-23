#!/bin/sh
# Quickstart initialisation.
rm -rf .venv
rm -rf node_modules
virtualenv -p python3.6 .venv
. .venv/bin/activate
pip install -r requirements.txt
yarn
dd if=/dev/urandom of=/dev/stdout bs=50 count=1 | base64 > .secret_key

#!/bin/sh
# Quickstart for a fresh machine. Requires a modernish Python and nvm.
set -e
rm -rf .venv
rm -rf node_modules
virtualenv -p python3 .venv
# shellcheck disable=1091
. .venv/bin/activate
pip install -r requirements-dev.txt
# shellcheck disable=1090
. ~/.nvm/nvm.sh
nvm install "$(cat .nvmrc)"
npm install -g yarn
yarn
# We have `manage.py generate_secret_key`, but that loads Django settings,
# which depends on the existence of `.secret_key`!
openssl rand -hex 64 > .secret_key

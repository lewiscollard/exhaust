#!/bin/sh

set -e

python -Werror ./manage.py check
coverage run --source=exhaust/ ./manage.py check --deploy --settings=exhaust.settings.production --fail-level=WARNING
coverage run --append --source=exhaust/ ./manage.py test
# Ensure there are no model changes that should have a migration.
./manage.py makemigrations --check --dry-run
flake8 exhaust/
pylint --rcfile=tox.ini exhaust/
isort --check-only --diff exhaust/
coverage report --show-missing --fail-under=100

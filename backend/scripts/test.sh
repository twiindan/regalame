#!/usr/bin/env bash

set -e
set -x

source .venv/bin/activate

coverage run --source=app -m pytest
coverage report --show-missing
coverage html --title "${@-coverage}"

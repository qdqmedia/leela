#!/bin/bash

CURRENT_PATH=$(dirname "${BASH_SOURCE[0]}")
PYTHON_BIN=/home/qdqmedia/leela/bin/python
COMPOSER_FILE=$CURRENT_PATH/../docker-compose.yml

echo "*********************************************************"
echo "Running tests..."
echo "*********************************************************"

docker-compose -f $COMPOSER_FILE run --rm --service-ports leela $PYTHON_BIN manage.py test

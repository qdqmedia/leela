#!/bin/bash

CURRENT_PATH=$(dirname "${BASH_SOURCE[0]}")
PYTHON_BIN=/home/qdqmedia/leela/bin/python
COMPOSER_FILE=$CURRENT_PATH/../docker-compose.yml

echo "*********************************************************"
echo "Starting email scheduler. Send jobs to 127.0.0.1:5672"
echo "Check RabbitMQ service at http://127.0.0.1:15672/"
echo "*********************************************************"

docker-compose -f $COMPOSER_FILE run --rm --service-ports leela $PYTHON_BIN manage.py scheduler

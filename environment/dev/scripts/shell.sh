#!/bin/bash

CURRENT_PATH=$(dirname "${BASH_SOURCE[0]}")
COMPOSER_FILE=$CURRENT_PATH/../docker-compose.yml

echo "***********************************"
echo "Starting shell inside the container"
echo "***********************************"

docker-compose -f $COMPOSER_FILE run --rm leela /bin/bash

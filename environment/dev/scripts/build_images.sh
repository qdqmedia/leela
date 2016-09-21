#!/bin/bash

CURRENT_PATH=$(dirname "${BASH_SOURCE[0]}")
DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed "s/\..,//")

# Build postgres images
# ...

docker build -t qdqmedia/leela -f $CURRENT_PATH/../Dockerfile $CURRENT_PATH/../../../

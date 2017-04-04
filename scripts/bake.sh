#!/bin/bash
set -o allexport

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

if [ -e .env ]; then
	source .env
fi
echo $SCRUFFY_DOCKER_IMAGE_LOCAL

docker build -t $SCRUFFY_DOCKER_IMAGE_LOCAL:$SCRUFFY_IMAGE_VERSION . 

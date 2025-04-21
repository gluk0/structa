#!/bin/bash
set -e

# Get the version from meta.yaml file, this is a global 

VERSION="0.1" 

if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from meta.yaml"
    exit 1
fi

echo "Building structa image version $VERSION"

docker build -t structa:$VERSION -t structa:latest ..

echo "Tagging structa:$VERSION for DockerHub"
docker tag structa:$VERSION glukae/structa:$VERSION
docker tag structa:latest glukae/structa:latest

echo "Pushing structa:$VERSION to DockerHub"
docker push glukae/structa:$VERSION
docker push glukae/structa:latest

echo "Successfully deployed structa:$VERSION to DockerHub"
#!/bin/bash

set -e  # Bricht bei Fehlern ab

# 🔧 Konfiguration
IMAGE_NAME="aliyanraf/flink-python-example"
TAG="latest"
FLINK_DEPLOYMENT_NAME="python-example"
YAML_FILE="python-example.yaml"

echo "🔧 Baue Docker-Image: $IMAGE_NAME:$TAG"
docker build . -t "$IMAGE_NAME:$TAG"

echo "📤 Pushe Image zu Docker Hub"
docker push "$IMAGE_NAME:$TAG"

echo "🗑️  Lösche vorhandenes FlinkDeployment (falls vorhanden): $FLINK_DEPLOYMENT_NAME"
kubectl delete FlinkDeployment "$FLINK_DEPLOYMENT_NAME" --ignore-not-found

echo "🚀 Wende neue FlinkDeployment-Konfiguration an: $YAML_FILE"
kubectl apply -f "$YAML_FILE"

echo "✅ FlinkDeployment erfolgreich aktualisiert."

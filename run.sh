#!/bin/bash
# Demo of the chopping mate. 
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}Starting k3s...${NC}"

if ! command -v k3s &> /dev/null || ! systemctl is-active --quiet k3s; then
    echo "Error: k3s is not installed or not running. Please install and start k3s first."
    exit 1
fi 

echo -e "${GREEN}K3s is running. Deploying the demo microservice with Structa sidecar...${NC}"
# Check if the deploy script exists
if [ ! -f "/structa-helm-chart/deploy.sh" ]; then
    echo "Error: /structa-helm-chart/deploy.sh not found!"
    exit 1
fi

# Run the isolated helm chart deployment script. 
/structa-helm-chart/deploy.sh

echo -e "${GREEN}Deployment initiated. Waiting for pods to be ready...${NC}"
# Wait for the pods to be in Running state
kubectl wait --for=condition=ready pod -l app=structa --timeout=300s

echo -e "${BLUE}Showing logs from the Structa app while parsing:${NC}"
echo -e "${BLUE}(Press Ctrl+C to stop the log stream)${NC}"

STRUCTA_POD=$(kubectl get pods -l app=structa -o jsonpath="{.items[0].metadata.name}")

kubectl logs -f $STRUCTA_POD -c structa
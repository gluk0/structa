#!/bin/bash
set -e

function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Deploy the Structa Sidecar Helm Chart to a K3s cluster."
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE  Deploy to specified namespace (default: default)"
    echo "  -r, --release-name NAME    Set the Helm release name (default: structa-app)"
    echo "  -v, --values FILE          Use custom values file (default: values.yaml)"
    echo "  -d, --debug                Enable Helm debug output"
    echo "  -h, --help                 Show this help message"
    echo ""
    exit 0
}

NAMESPACE="default"
RELEASE_NAME="structa-app"
VALUES_FILE="values.yaml"
DEBUG=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -n|--namespace)
            NAMESPACE="$2"
            shift
            shift
            ;;
        -r|--release-name)
            RELEASE_NAME="$2"
            shift
            shift
            ;;
        -v|--values)
            VALUES_FILE="$2"
            shift
            shift
            ;;
        -d|--debug)
            DEBUG="--debug"
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check if namespace exists, create if not
if ! kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
    echo "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
fi

# Deploy with Helm
echo "Deploying Structa Sidecar to K3s cluster..."
echo "  Namespace:    $NAMESPACE"
echo "  Release name: $RELEASE_NAME"
echo "  Values file:  $VALUES_FILE"
echo ""

# Execute Helm install/upgrade
helm upgrade --install $RELEASE_NAME . \
    --namespace $NAMESPACE \
    --values $VALUES_FILE \
    $DEBUG

echo ""
echo "Deployment complete!"
echo ""
echo "To check the status, run:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "To view the logs of the Structa sidecar, run:"
echo "  kubectl logs -n $NAMESPACE \$(kubectl get pods -n $NAMESPACE -l app=$RELEASE_NAME -o jsonpath='{.items[0].metadata.name}') -c structa-sidecar"

# Example usage of the deploy.sh script
echo "  kubectl logs -n $NAMESPACE \$(kubectl get pods -n $NAMESPACE -l app=$RELEASE_NAME -o jsonpath='{.items[0].metadata.name}') -c structa-sidecar" 
#!/bin/bash
set -e

# Display help
function show_help {
    echo "Usage: $0 [options]"
    echo ""
    echo "Clean up Structa Sidecar Helm Chart resources from a K3s cluster."
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE  Namespace where the release is deployed (default: default)"
    echo "  -r, --release-name NAME    The Helm release name to delete (default: structa-app)"
    echo "  -d, --debug                Enable Helm debug output"
    echo "  -f, --force                Force deletion of resources"
    echo "  -h, --help                 Show this help message"
    echo "  --delete-namespace         Also delete the namespace (use with caution)"
    echo ""
    exit 0
}

# Default values
NAMESPACE="default"
RELEASE_NAME="structa-app"
DEBUG=""
FORCE=""
DELETE_NAMESPACE=false

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
        -d|--debug)
            DEBUG="--debug"
            shift
            ;;
        -f|--force)
            FORCE="--force"
            shift
            ;;
        --delete-namespace)
            DELETE_NAMESPACE=true
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

# Check if the namespace exists
if ! kubectl get namespace "$NAMESPACE" > /dev/null 2>&1; then
    echo "Error: Namespace '$NAMESPACE' does not exist."
    exit 1
fi

# Check if the Helm release exists
if ! helm status --namespace "$NAMESPACE" "$RELEASE_NAME" > /dev/null 2>&1; then
    echo "Error: Helm release '$RELEASE_NAME' not found in namespace '$NAMESPACE'."
    exit 1
fi

# Confirm deletion
echo "This will delete the Helm release '$RELEASE_NAME' from namespace '$NAMESPACE'."
if [[ "$FORCE" != "--force" ]]; then
    read -p "Are you sure you want to proceed? (y/n): " -n 1 -r
    echo    # Move to a new line
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operation canceled."
        exit 0
    fi
fi

echo "Deleting Helm release '$RELEASE_NAME' from namespace '$NAMESPACE'..."
helm uninstall $DEBUG $RELEASE_NAME --namespace $NAMESPACE

# Wait for resources to be deleted
echo "Waiting for resources to be deleted..."
kubectl wait --for=delete pods --selector=app=$RELEASE_NAME --namespace $NAMESPACE --timeout=60s 2>/dev/null || true

# Optionally delete the namespace
if $DELETE_NAMESPACE; then
    echo "Deleting namespace '$NAMESPACE'..."
    kubectl delete namespace $NAMESPACE
fi

echo ""
echo "Cleanup complete!"
echo ""
echo "To verify all resources are gone, run:"
echo "  kubectl get all -n $NAMESPACE -l app=$RELEASE_NAME" 
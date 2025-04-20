#!/bin/bash

TEST_TYPE="all"
COVERAGE=false

for arg in "$@"; do
    case $arg in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit        Run only unit tests"
            echo "  --integration Run only integration tests"
            echo "  --all         Run all tests (default)"
            echo "  --coverage    Generate coverage report"
            echo "  --help        Show this help message"
            exit 0
            ;;
    esac
done

CMD="uv run pytest -v"

case $TEST_TYPE in
    unit)
        CMD="$CMD -m unit"
        echo "Running unit tests..."
        ;;
    integration)
        CMD="$CMD -m integration"
        echo "Running integration tests..."
        ;;
    all)
        echo "Running all tests..."
        ;;
esac

if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=structa --cov-report=term --cov-report=html"
    echo "Generating coverage report..."
fi

$CMD

if [ $? -eq 0 ]; then
    echo "Tests completed successfully!"
    
    if [ "$COVERAGE" = true ]; then
        echo "Coverage report available in htmlcov/index.html"
    fi
else
    echo "Tests failed!"
    exit 1
fi 
#!/bin/bash
# bump-version.sh - Automatically bumps version for PyPI releases in GitHub Actions

set -e

VERSION_FILE="pyproject.toml" 
COMMIT_USER="GitHub Actions"
COMMIT_EMAIL="github-actions@github.com"

# Is it Github acitons? 
if [ -z "$GITHUB_REF" ]; then
    echo "Error: This script is intended to run within GitHub Actions"
    exit 1
fi

# Bump 
bump_version() {
    local version_type=$1
    
    if [ -f "$VERSION_FILE" ]; then
        if grep -q 'version\s*=' "$VERSION_FILE"; then
            # Get current version
            current_version=$(grep 'version\s*=' "$VERSION_FILE" | sed 's/.*version\s*=\s*"\([^"]*\)".*/\1/')
            
            # Parse version components
            IFS='.' read -r major minor patch <<< "$current_version"
            
            # Bump appropriate part
            case "$version_type" in
                major)
                    major=$((major + 1))
                    minor=0
                    patch=0
                    ;;
                minor)
                    minor=$((minor + 1))
                    patch=0
                    ;;
                patch|*)
                    patch=$((patch + 1))
                    ;;
            esac
            new_version="${major}.${minor}.${patch}"
            sed -i "s/version\s*=\s*\"$current_version\"/version = \"$new_version\"/" "$VERSION_FILE"
            echo "Version bumped from $current_version to $new_version"
            return 0
        else
            echo "Error: Version pattern not found in $VERSION_FILE"
            exit 1
        fi
    else
        echo "Error: Version file $VERSION_FILE not found"
        exit 1
    fi
}

git config user.name "$COMMIT_USER"
git config user.email "$COMMIT_EMAIL"

BUMP_TYPE="patch"

if git log -1 --pretty=%B | grep -i -q '\[major\]'; then
    BUMP_TYPE="major"
elif git log -1 --pretty=%B | grep -i -q '\[minor\]'; then
    BUMP_TYPE="minor"
fi

bump_version "$BUMP_TYPE"
git add "$VERSION_FILE"
git commit -m "Bump version to $(grep 'version\s*=' "$VERSION_FILE" | sed 's/.*version\s*=\s*"\([^"]*\)".*/\1/') [skip ci]"
git pull --rebase origin "${GITHUB_REF#refs/heads/}" 
git push origin HEAD:"${GITHUB_REF#refs/heads/}"
echo "Version bump complete and pushed to repository"
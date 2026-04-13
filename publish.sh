#!/bin/bash
set -e

# Requires: pip install build twine
# Set TWINE_USERNAME and TWINE_PASSWORD (or use a .pypirc / keyring).
# For API token auth: TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-...

echo "Cleaning old dist..."
rm -rf dist/

echo "Building..."
python -m build

echo "Checking..."
python -m twine check dist/*

echo "Uploading to PyPI..."
python -m twine upload dist/*

echo "Done."

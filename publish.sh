#!/bin/bash
set -e

# Requires: pip install build twine
# Set TWINE_USERNAME and TWINE_PASSWORD (or use a .pypirc / keyring).
# For API token auth: TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-...

echo "Installing build tools..."
python3 -m pip install --quiet build 'twine' 'urllib3<2.0'

echo "Cleaning old dist..."
rm -rf dist/

echo "Building..."
python3 -m build

echo "Checking..."
python3 -m twine check dist/*

echo "Uploading to PyPI..."
python3 -m twine upload dist/*

echo "Done."

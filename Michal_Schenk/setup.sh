#!/bin/bash
echo "Setting up the environment"

# Create venv
python3 -m venv .venv

# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Environment setup complete"
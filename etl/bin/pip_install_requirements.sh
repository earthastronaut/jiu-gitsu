#!/bin/bash

set -e 

# Usage: 
# 	pip_install_requirements requirements_dir

requirements_filepath="$1"

# ########################################################################### #
# Install Requirements
# ########################################################################### #

echo "---------------------------"
echo "Install Python Requirements"
echo "---------------------------"
echo "SERVICE_ENVIRONMENT=$SERVICE_ENVIRONMENT"
echo "requirements=$requirements_filepath"
echo "---------------------------"

pip install -U --no-warn-script-location pip setuptools wheel
pip install --no-cache-dir -r $requirements_filepath

# ########################################################################### #
# Check for Update to Requirements
# ########################################################################### #

echo "---------------------------"
echo "Check Python Requirements"
echo "---------------------------"
pip list --outdated

# ########################################################################### #
# Print out current pip freeze
# ########################################################################### #

echo "---------------------------"
echo "Current pip freeze"
echo "---------------------------"
pip freeze
echo "---------------------------"

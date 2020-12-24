#!/usr/bin/env sh

echo $NODE_NAME
echo $PIPELINE_NODE
echo $NODE_LABELS
echo $RESERVE
echo $PWD
set -ex
echo "$BRANCH_NAME"


pip install pip==20.2.3
make build

NAME=quartic_notebook
VERSION=$(awk '$1 == "__version__" {print $NF}' ./notebook/_version.py | sed "s/'//g")

bash ./jenkins-scripts/publish_package.sh "$NAME" "$VERSION"

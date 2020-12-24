#!/usr/bin/env sh
set -ex

OS=none
CPU_ARCH=any

NAME=$1
VERSION=$2

if [[ -z "$NAME" ]] || [[ -z "$VERSION" ]]; then
  echo 'Name and version values are missing'
  exit 1
else
  WHEEL_FILENAME="$NAME-$VERSION-py3-$OS-$CPU_ARCH.whl"
  CODE=$(curl -sS -w '%{http_code}' -F package="@dist/$WHEEL_FILENAME" -o output.txt "https://$GEMFURY_AUTH_TOKEN@push.fury.io/quartic-ai/")
  cat output.txt && rm -rf output.txt
  if [[ "$CODE" =~ ^2 ]]; then
      echo "$WHEEL_FILENAME Package published successfully"
  else
      echo "ERROR: server returned HTTP code $CODE"
      exit 1
  fi
fi

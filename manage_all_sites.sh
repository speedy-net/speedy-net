#!/usr/bin/env bash
script="$(dirname $0)"
echo $0
SCRIPT_DIR="$(cd $(dirname  "$SCRIPT" ) && pwd -P)"
VENV_DIR=${VENV_DIR:-"$SCRIPT_DIR/.venv"}
SITES="net match composer mail core"

for site in $SITES
do
    cd "$SCRIPT_DIR/speedy/$site"
    $VENV_DIR/bin/python manage.py $@
done

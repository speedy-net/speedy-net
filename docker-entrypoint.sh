#!/bin/bash
set -e
./wait-for-it.sh db:5432

SITES="net match composer mail core"

case "$1" in
    all)

        for site in $SITES
        do
            cd /app/speedy/$site
            python manage.py "${@:2}"
        done
    ;;
    *)
        cd /app/speedy/$CURRENT_SITE
        python manage.py "$@"
    ;;
esac

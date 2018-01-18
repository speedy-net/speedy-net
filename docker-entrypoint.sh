#!/bin/bash
set -e
./wait-for-it.sh db:5432

SITES="net match composer mail"

case "$1" in
    all)

        for site in $SITES
        do
            echo
            echo "@@@ speedy-$site @@@"

            cd /app/speedy/$site
            python manage.py "${@:2}"
        done
    ;;
    python)
        echo
        echo "@@@ speedy-$CURRENT_SITE @@@"
        cd /app/speedy/$CURRENT_SITE
        "$@"
    ;;
    *)
        echo
        echo "@@@ speedy-$CURRENT_SITE @@@"
        cd /app/speedy/$CURRENT_SITE
        python manage.py "$@"
    ;;
esac

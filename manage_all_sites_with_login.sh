#!/usr/bin/env bash

SITES="net match"
cd "speedy/net"
python --version

exitcode=0

for site in ${SITES}
do
    cd "../${site}"
    python manage.py ${@}

    tmp=$?
    if [[ $tmp -ne 0 ]]
    then
        exitcode=$tmp
    fi
done

exit $exitcode

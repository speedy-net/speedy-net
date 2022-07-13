#!/usr/bin/env bash

SITES="net match composer mail core"
cd "speedy/net"
python --version

exitcode=0

for site in ${SITES}
do
    cd "../${site}"
    python -W error manage.py ${@}

    tmp=$?
    if [[ $tmp -ne 0 ]]
    then
        exitcode=$tmp
    fi
done

exit $exitcode

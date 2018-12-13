#!/usr/bin/env bash

SITES="net match composer mail"
cd "speedy/net"

for site in $SITES
do
    cd "../$site"
    python manage.py $@
done

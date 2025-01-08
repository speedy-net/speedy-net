#!/bin/sh

DIR="/home/ubuntu/speedy-net"
PY="${DIR}/env/bin/python"
PIP="${DIR}/env/bin/pip"
SITES="net match composer mail"

cd ${DIR}
git pull
${PY} -m pip install --upgrade pip
${PIP} install --upgrade -r requirements.txt
${PIP} uninstall django-debug-toolbar # django-debug-toolbar should never be installed in production or staging.
${PIP} uninstall factory-boy # factory-boy should never be installed in production or staging.
${PIP} uninstall Faker # Faker should never be installed in production or staging.

for site in ${SITES}
do
    cd "${DIR}/speedy/${site}"
    ${PY} manage.py migrate
    ${PY} manage.py collect_static --no-input
    touch "/run/uwsgi/app/speedy_${site}/reload"
done

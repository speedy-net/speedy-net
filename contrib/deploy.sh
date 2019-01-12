#!/bin/sh

DIR=/home/ubuntu/speedy-net
PY=${DIR}/env/bin/python
PIP=${DIR}/env/bin/pip
SITES="net match composer mail"

cd ${DIR}
git pull
${PIP} install -r requirements.txt
${PIP} uninstall django-debug-toolbar

for site in ${SITES}
do
    cd "${DIR}/speedy/${site}"
    ${PY} manage.py migrate
    ${PY} manage.py collectstatic --no-input
    touch "/run/uwsgi/app/speedy_${site}/reload"
done

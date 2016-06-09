#!/bin/sh

DIR=/home/ubuntu/speedy-net
PY=$DIR/env/bin/python
PIP=$DIR/env/bin/pip

cd $DIR
git pull
$PIP install -r requirements.txt

cd $DIR/speedy/net
$PY manage.py migrate
$PY manage.py collectstatic --no-input
touch /run/uwsgi/app/speedy_net/reload

cd $DIR/speedy/match
$PY manage.py migrate
$PY manage.py collectstatic --no-input
touch /run/uwsgi/app/speedy_match/reload

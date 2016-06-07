# Speedy Net / Speedy Match

## How to setup the project and run locally

First make sure that you're using Python 3.4 or later.

    pip install -r requirements.txt
    cp env.ini.example env.ini
    
You may want to edit `env.ini` to specify database settings, secret keys for third party services or other stuff.

Then you can run migrations:
  
    ./manage.py migrate

To run Speedy Net server:

    cd speedy/net
    ./manage.py runserver

To run Speedy Match server:

    cd speedy/match
    ./manage.py runserver

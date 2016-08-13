# Speedy Net / Speedy Match

## How to setup the project and run locally

First make sure that you're using Python 3.4 or later.

Then, you'll want to create a virtualenv and activate. You create virtualenv once and activate it each time you start to work on the project.

    python -m venv .venv
    .venv\Scripts\activate.bat  # Windows
    source .venv/bin/activate   # *.nix

Next:

    pip install -r requirements.txt
    cp env.ini.example env.ini
    
You may want to edit [**env.ini**](#envini) to specify database settings, secret keys for third party services or other stuff.

Then you can run migrations:
  
    ./manage.py migrate
    ./manage.py loaddata ../../default_sites.json

To run Speedy Net server:

    cd speedy/net
    ./manage.py runserver

To run Speedy Match server:

    cd speedy/match
    ./manage.py runserver

## How to setup a server (Ubuntu 16.04)

Install all dependencies using **apt-get**:
 
    sudo apt-get install python3 python3-pip python3-venv  # common python stuff
    sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev  # pillow dependencies
    sudo apt-get install postgresql postgresql-server-dev-all nginx uwsgi uwsgi-plugin-python3 postfix
    
    
Clone the project, create a venv, activate it and install required modules using **pip**:
    
    git clone https://github.com/urievenchen/speedy-net.git
    cd speedy-net/
    python3 -m venv env
    source env/bin/activate
    pip install --upgrade wheel  # resolves "invalid command 'bdist_wheel'"
    pip install -r requirements.txt
    pip install psycopg2

Setup a database:

    sudo -i -u postgres
    createuser speedy_net
    createdb -O speedy_net speedy_net
    exit
    
In **/etc/postgresql/9.5/main/pg_hba.conf** change the line:

    host    all             all             127.0.0.1/32            md5

to

    host    all             all             127.0.0.1/32            trust

Restart **postgresql**:

    sudo service postgresql restart

Copy **env.ini.example** to **env.ini**:

    cp env.ini.example env.ini
    
Change **env.ini** appropriately. Refer to [**env.ini** section](#envini) of this document. `DATABASE_URL` should be like `postgres://speedy_net@127.0.0.1:5432/speedy_net`

Run migrations and collect static:

    cd speedy/net
    ./manage.py migrate
    ./manage.py collectstatic
    cd ../match
    ./manage.py migrate
    ./manage.py collectstatic

Copy sample **nginx** and **uwsgi** configs:
 
    cd ~/speedy-net/
    sudo cp contrib/uwsgi/*.ini /etc/uwsgi/apps-enabled/
    sudo cp contrib/nginx/*.conf /etc/nginx/sites-enabled/
    
Review and edit these config files, restart servers:

    sudo service uwsgi restart
    sudo service nginx restart


## env.ini

**env.ini** file is where you should store all your credentials and secret keys. It must not to be checked into VCS.

Available settings:

* `ENVIRONMENT` defines which of settings files should be used. They are located in `speedy/net/settings` and `speedy/match/settings`. *Example*: `staging`
* `SECRET_KEY` is a random string. [More on Django docs](https://docs.djangoproject.com/en/1.9/ref/settings/#secret-key). *Example*: `s3cr37k3Y***`
* `DATABASE_URL` contains the settings for default database. *Examples*: look [dj-database-url docs](https://github.com/kennethreitz/dj-database-url#url-schema)
* `SPEEDY_NET_SITE_ID` and `SPEEDY_MATCH_SITE_ID` — just leave these as its.

Refer to [django-environ documentation](https://django-environ.readthedocs.io/en/latest/) for more information.

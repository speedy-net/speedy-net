# Speedy Net / Speedy Match

Speedy Net is a new social network which will have apps, such as Speedy Match (a dating/matching app for singles) and Speedy Composer and Speedy Mail (later). Speedy Net is open to all ages - vegan, vegetarian or carnists, men, women or other. Speedy Net will be vegan-friendly and friendly to human rights, peace and animal rights.

 - Requirements for alpha step 1 - Speedy Net: -

* support English and Hebrew
* registration
* activating profile by validating email address
* login (with username or email, and password)
* profile picture
* public profile / profile for friends
* first name/last name must be language-specific
* friendship requests
* approving friendship requests (up to 800 friends per person)
* password reset
* Sending/receiving private messages
* Any email address, phone and link (Facebook, Twitter, blog etc.) - visible to anyone/friends/only me
* website must be mobile- and desktop-friendly
* import all users from PHP/MySQL
* Users of PHP/MySQL Speedy Net will be able to login with their current username or email, and password

 - Requirements for alpha step 1 - Speedy Match: -

* support English and Hebrew
* registration to Speedy Net
* profile in Speedy Match - vegan/vegetarian/carnist, smoking or not, single/married, have children (how many)/doesn't have children etc.
* Looking for men, women or both
* Writing some text about yourself - who you are, what you prefer etc.
* Which personal attributes are valid (from 0 to 5. 0 - invalid (no match). 5 - 5 stars match)
* Searching for matching people (who use Speedy Match in the same language)
* Sending/receiving private messages (Speedy Net)
* friendship requests (Speedy Net)
* website must be mobile- and desktop-friendly
* Every text you type in Speedy Match will be language - specific. If you use Speedy Match in more than one language, you can type different text in different languages. But everything else will be the same.


 - Requirements for alpha step 2 - Speedy Net: -

* Uploading albums and photos.
* Creating pages, groups and causes (with or without a username)
* Liking posts, photos, albums etc.

 - Requirements for alpha step 2 - Speedy Match: -

* Search for matches by geographic location (optional)


You can find more details in the specifications.

[![Build Status](https://travis-ci.org/urievenchen/speedy-net.svg?branch=master)](https://travis-ci.org/urievenchen/speedy-net)

## How to setup the project and run locally

First make sure that you're using Python 3.4 or later.

Then, you'll want to create a virtualenv and activate. You create virtualenv once and activate it each time you start to work on the project.

    python -m venv .venv
    .venv\Scripts\activate.bat  # Windows
    source .venv/bin/activate   # *.nix

Next:
    python -m pip install -U pip
    pip install -r requirements.txt
    cp env.ini.example env.ini

You may want to edit [**env.ini**](#envini) to specify database settings, secret keys for third party services or other stuff.

Then you can run migrations:

    cd speedy/net
    ./manage.py migrate
    cd speedy/match
    ./manage.py migrate
    cd speedy/net
    ./manage.py loaddata ../../default_sites_local.json

To run Speedy Net server:

    cd speedy/net
    ./manage.py runserver

To run Speedy Match server:

    cd speedy/match
    ./manage.py runserver

To run Speedy Net tests:

     cd speedy/net
    ./manage.py test

To run Speedy Match tests:

     cd speedy/match
    ./manage.py test


## How to setup a server (Ubuntu 16.04)

Install all dependencies using **apt-get**:

    sudo apt-get install python3 python3-pip python3-venv  # common python stuff
    sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev  # pillow dependencies
    sudo apt-get install postgresql postgresql-server-dev-all nginx uwsgi uwsgi-plugin-python3 postfix memcached


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
    cd ../composer
    ./manage.py migrate
    ./manage.py collectstatic
    cd ../mail
    ./manage.py migrate
    ./manage.py collectstatic

Copy sample **nginx** and **uwsgi** configs:

    cd ~/speedy-net/
    sudo cp contrib/uwsgi/*.ini /etc/uwsgi/apps-enabled/
    sudo cp contrib/nginx/*.conf /etc/nginx/sites-enabled/

Remove default **nginx** config:
 
     sudo rm /etc/nginx/sites-enabled/default

Review and edit these config files, restart servers:

    sudo service uwsgi restart
    sudo service nginx restart


## env.ini

**env.ini** file is where you should store all your credentials and secret keys. It must not to be checked into VCS.

Available settings:

* `ENVIRONMENT` defines which of settings files should be used. They are located in `speedy/net/settings` and `speedy/match/settings`. *Example*: `staging`
* `SECRET_KEY` is a random string. [More on Django docs](https://docs.djangoproject.com/en/1.9/ref/settings/#secret-key). *Example*: `s3cr37k3Y***`
* `DATABASE_URL` contains the settings for default database. *Examples*: look [dj-database-url docs](https://github.com/kennethreitz/dj-database-url#url-schema)
* `CACHE_URL` contains the settings for default caching backend. *Examples*: look [django-cache-url docs](https://github.com/ghickman/django-cache-url#supported-caches)
* `SPEEDY_*_SITE_ID` — just leave these as its.

Refer to [django-environ documentation](https://django-environ.readthedocs.io/en/latest/) for more information.

![GitHub Actions](https://github.com/speedy-net/speedy-net/actions/workflows/main.yml/badge.svg)

# Speedy Net / Speedy Match

[Speedy Net](https://www.speedy.net/) is a new social network which will have apps, such as [Speedy Match](https://www.speedymatch.com/) (a dating/matching app for singles) and [Speedy Composer](https://www.speedycomposer.com/) and [Speedy Mail](https://www.speedy-mail-software.com/) (later). Speedy Net is open to all ages - vegan, vegetarian or carnists, men, women or other. Speedy Net will be vegan-friendly and friendly to human rights, peace and animal rights.

 - Requirements for alpha step 1 - Speedy Net:

    * Support English and Hebrew
    * Registration
    * Activating profile by validating email address
    * Login (with username or email, and password)
    * Profile picture
    * Public profile / profile for friends
    * First name/last name must be language-specific
    * Friendship requests
    * Approving friendship requests (up to 800 friends per person)
    * Password reset
    * Sending/receiving private messages
    * Any email address, phone and link (Facebook, Twitter, blog etc.) - visible to anyone/friends/only me
    * Website must be mobile- and desktop-friendly
    * Import all users from PHP/MySQL
    * Users of PHP/MySQL Speedy Net will be able to login with their current username or email, and password

 - Requirements for alpha step 1 - Speedy Match:

    * Support English and Hebrew
    * Registration to Speedy Net
    * Profile in Speedy Match - vegan/vegetarian/carnist, smoking or not, single/married, have children (how many)/doesn't have children etc.
    * Looking for men, women or both
    * Writing some text about yourself - who you are, what you prefer etc.
    * Which personal attributes are valid (from 0 to 5. 0 - invalid (no match). 5 - 5 hearts match)
    * Searching for matching people (who use Speedy Match in the same language)
    * Sending/receiving private messages (Speedy Net)
    * Friendship requests (Speedy Net)
    * Website must be mobile- and desktop-friendly
    * Every text you type in Speedy Match will be language - specific. If you use Speedy Match in more than one language, you can type different text in different languages. But everything else will be the same.


 - Requirements for alpha step 2 - Speedy Net:

    * Uploading albums and photos.
    * Creating pages, groups and causes (with or without a username)
    * Liking posts, photos, albums etc.

 - Requirements for alpha step 2 - Speedy Match:

    * Search for matches by geographic location (optional)


You can find more details in the specifications.

## How to setup the project and run locally

First make sure that you're using Python 3.8 or later (we recommend the latest Python version).

Then, you'll want to create a virtualenv and activate. You create virtualenv once and activate it each time you start to work on the project.

    pip install virtualenv # (as administrator)
    virtualenv .venv
    source .venv/Scripts/activate  # Windows Git Bash (MINGW64)
    source .venv/bin/activate   # *.nix

Next:

    python -m pip install --upgrade pip
    pip install --upgrade setuptools wheel
    pip install --upgrade -r requirements.txt
    cp env.ini.example env.ini

You may want to edit [**env.ini**](#envini) to specify database settings, secret keys for third party services or other stuff.

Then you can run migrations:

    cd speedy/net
    ./manage.py migrate
    cd speedy/match
    ./manage.py migrate
    cd speedy/core
    ./manage.py load_data fixtures/default_sites_local.json

To run Speedy Net server:

    cd speedy/net
    ./manage.py run_server 8010

To run Speedy Match server:

    cd speedy/match
    ./manage.py run_server 8020

To run Speedy Net tests:

    cd speedy/net
    ./tests_manage.py test

To run Speedy Match tests:

    cd speedy/match
    ./tests_manage.py test

To run tests with deprecation warnings (in any directory):

    python -W error::DeprecationWarning tests_manage.py test

You need to run both Speedy Net and Speedy Match in parallel in separate console tabs.

Use the following URLs to access the websites:

    http://www.speedy.net.localhost:8010/
    http://www.speedy.match.localhost:8020/
    http://www.speedy.composer.localhost:8030/
    http://www.speedy.mail.software.localhost:8040/

### Build frontend

The project uses Bootstrap 4 with [gulp.js](https://gulpjs.com). `css` are compiled from `scss`.

You need to setup [Node](https://nodejs.org/en/) with [npm](https://www.npmjs.com). To install build tools run:

    npm install

Then:

    gulp

Will compile static files.

**Please notice** - gulp doesn't work if you have spaces in folder names in your directory tree. All file and folder names cannot contain spaces.

## How to setup the project and run locally (with docker-compose)

    docker-compose up
    docker-compose run --rm match all migrate
    docker-compose run --rm net load_data speedy/core/fixtures/default_sites_local.json


## How to setup a server (Ubuntu 18.04)

Install all dependencies using **apt-get**:

    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo add-apt-repository -y "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main"
    sudo apt update
    sudo apt-get install python3.8 python3-pip python3.8-venv python3.8-dev  # common python stuff
    sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev  # pillow dependencies
    sudo apt-get install postgresql-13 postgresql-client-13 postgresql-server-dev-all nginx uwsgi uwsgi-src postfix memcached

Build **uwsgi** plugin:

    PYTHON=python3.8 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python38"
    mv python38_plugin.so /usr/lib/uwsgi/plugins

Clone the project, create a venv, activate it and install required modules using **pip**:

    git clone https://github.com/speedy-net/speedy-net.git
    cd speedy-net/
    python3.8 -m venv env
    source env/bin/activate
    python -m pip install --upgrade pip
    pip install --upgrade setuptools wheel
    pip install --upgrade -r requirements.txt

You must run the following commands, according to https://stackoverflow.com/a/54253374/57952:

    /home/ubuntu/speedy-net/env/bin/pip uninstall psycopg2
    /home/ubuntu/speedy-net/env/bin/pip install --no-binary :all: psycopg2==2.9.2

Setup a database:

    sudo -i -u postgres
    createuser speedy_net
    createdb -O speedy_net speedy_net
    exit

In **/etc/postgresql/13/main/pg_hba.conf** change the line:

    host    all             all             127.0.0.1/32            md5

to

    host    all             all             127.0.0.1/32            trust

Restart **postgresql**:

    sudo service postgresql restart

Copy **env.ini.example** to **env.ini**:

    cp env.ini.example env.ini

Change **env.ini** appropriately. Refer to [**env.ini** section](#envini) of this document. `DATABASE_URL` should be like `postgres://speedy_net@127.0.0.1:5432/speedy_net`

Run migrations and collect static:

    contrib/deploy.sh

Copy sample **nginx** and **uwsgi** configs:

    cd ~/speedy-net/
    sudo cp contrib/uwsgi/*.ini /etc/uwsgi/apps-enabled/
    sudo cp contrib/nginx/*.conf /etc/nginx/sites-enabled/

Copy **logrotate** config:

    sudo cp contrib/logrotate.d/speedy /etc/logrotate.d/
    sudo chmod 644 /etc/logrotate.d/speedy

Remove default **nginx** config:

     sudo rm /etc/nginx/sites-enabled/default

Install **systemd** service to create required directories on boot:

    sudo cp contrib/prepare-uwsgi.service /lib/systemd/system/
    sudo systemctl enable prepare-uwsgi

Review and edit these config files, restart servers:

    sudo service uwsgi restart
    sudo service nginx restart


## How to create an admin user

    from speedy.net.accounts.models import User
    from django.utils.timezone import now
    u = User()
    u.username = 'admin'
    u.slug = 'admin'
    u.date_of_birth = now()
    u.gender = User.GENDER_OTHER
    u.first_name = 'admin'
    u.last_name = 'admin'
    u.is_staff = True
    u.is_superuser = True
    u.special_username = True
    u.set_password('<PASSWORD>')
    u.save()


## env.ini

**env.ini** file is where you should store all your credentials and secret keys. It must not to be checked into VCS.

Available settings:

* `ENVIRONMENT` defines which of the settings files should be used. They are located in `speedy/net/settings` and `speedy/match/settings`. *Examples*: `development`, `staging` or `production`.
* `TESTS_ENVIRONMENT` defines which of the settings files should be used for tests. *Example*: `tests`.
* `SECRET_KEY` is a random string. [More on Django docs](https://docs.djangoproject.com/en/2.1/ref/settings/#secret-key). *Example*: `s3cr37k3Y***`
* `IPAPI_API_ACCESS_KEY` - access key for https://api.ipapi.com/
* `DATABASE_URL` contains the settings for default database. *Examples*: look [dj-database-url docs](https://github.com/kennethreitz/dj-database-url#url-schema)
* `CACHE_URL` contains the settings for default caching backend. *Examples*: look [django-cache-url docs](https://github.com/ghickman/django-cache-url#supported-caches)
* `SPEEDY_*_SITE_ID` — just leave these as it is.

Refer to [django-environ documentation](https://django-environ.readthedocs.io/en/latest/) for more information.


## How to upgrade required packages

To upgrade all the requirements (with Django>=3.2,<3.3), run:

    pip install --upgrade -r requirements-pip-upgrade.txt

To upgrade all the requirements (including Django), run:

    pip install --upgrade -r requirements-without-versions.txt

## How to make migrations and migrate

To make all migrations, run:

    ./manage_all_sites.sh make_migrations

To migrate all sites, run:

    ./manage_all_sites.sh migrate

## How to run all tests locally:

To run all tests locally, run:

    ./run_all_tests.sh

To run all tests locally with deprecation warnings, run:

    ./run_all_tests_with_deprecation_warnings.sh

## How to make and compile all messages for translation (To Hebrew):

To make all messages (in both languages), run:

    ./make_all_messages.sh

Edit \*.po files in speedy/\*/locale/he/LC_MESSAGES directories (No need to translate to English, leave all the files in speedy/\*/locale/en as they are).

To compile all messages (in both languages) after you've done editing all the \*.po files, run:

    ./compile_all_messages.sh


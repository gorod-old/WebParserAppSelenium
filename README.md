# WebServiceApp

Service application providing data parsing services

## Quick Start

Run the following commands to bootstrap the environment:

    sudo apt-get install git python3-venv python3-pip vim
    git clone https://.../proj_name
    cd proj_name

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements/dev.txt

Copy env template file to .env

    cp .env.template .env

and fill it with values ...

Run the app locally:

    python manage.py runserver 0.0.0.0:8000
    
Run the app with gunicorn:
    
    gunicorn --bind 0.0.0.0:8000 webparserapp.wsgi

or

    gunicorn webparserapp.wsgi -b 0.0.0.0:8001 
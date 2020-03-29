#!/bin/bash
. ./python-virtualenv/bin/activate
python manage.py runserver --settings=brexit.settings.production
#!/bin/sh

sudo rm -rf account/migrations/* chatroom/migrations/* lesson/migrations/* && touch account/migrations/__init__.py chatroom/migrations/__init__.py lesson/migrations/__init__.py && python3 manage.py makemigrations && python3 manage.py migrate
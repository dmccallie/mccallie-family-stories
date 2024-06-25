#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

#python manage.py makemigrations
python manage.py migrate

# tailwindcss to expand the css (installed by pytailwindcss in requirements.txt)
tailwindcss -i static/src/input.css -o static/src/output.css

# collects all static files in our app and puts it in the STATIC_ROOT
# make sure nginx points /static to this directory
python manage.py collectstatic --noinput

# Execute the command passed to the script
# can be overriden from docker-compose.yml or called from Dockerfile
exec "$@"

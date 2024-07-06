# These run only when the image is built, docker-compose --build

FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends

# Copy the current directory contents into the container at /app
# COPY . /web

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt

# copy entrypoint script and set executable
COPY ./scripts/start.sh /usr/src/app/scripts/
RUN chmod +x /usr/src/app/scripts/start.sh

# copy project
COPY . .

# Define environment variable
ENV DJANGO_SETTINGS_MODULE=config.settings

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mysite.wsgi:application"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT [ "/usr/src/app/scripts/start.sh" ]

# Default command - can be overridden by docker-compose "command" instruction
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "--log-level", "info"]
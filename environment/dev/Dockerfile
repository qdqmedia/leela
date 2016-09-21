FROM ubuntu:14.04
MAINTAINER Jaime Forcada Balaguer <jforcada@qdqmedia.com>

ENV PYTHONUNBUFFERED 1

# System dependencies
COPY requirements.apt /tmp/requirements.apt
RUN apt-get update && \
  cat /tmp/requirements.apt | xargs apt-get -y install

# Prepare paths
RUN mkdir -p /qdq/static
RUN mkdir -p /qdq/media
RUN mkdir /code

# Create the user/group for the running stuff
RUN groupadd -g 1000 qdqmedia
RUN useradd -m -u 1000 -g 1000 qdqmedia
RUN echo "qdqmedia ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/qdqmedia

# Set permissions
RUN chown qdqmedia:qdqmedia -R /qdq/
RUN chown qdqmedia:qdqmedia /code

# Copy python requirements
COPY requirements /tmp/leela_requirements

# Virtualenv
COPY environment/dev/scripts/create_venv.sh /home/qdqmedia/create_venv.sh
RUN chown qdqmedia:qdqmedia /home/qdqmedia/create_venv.sh
USER qdqmedia
WORKDIR /home/qdqmedia
RUN ./create_venv.sh leela
RUN /bin/bash -c "source leela/bin/activate && pip install pudb && pip install -r /tmp/leela_requirements/dev.txt"

# Default settings
WORKDIR /code
ENV DJANGO_SETTINGS_MODULE="leela.settings.dev"

# Django development server port
EXPOSE 8000

CMD ["/home/qdqmedia/leela/bin/python", "./manage.py", "runserver", "0.0.0.0:8000"]

# Use the official Python image from the DockerHub
FROM python:3.11.4-slim-buster

# Set the working directory in docker
WORKDIR /app

# set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN apt-get update && \
	apt-get install -y postgresql-client openssl && \
	pip install --no-cache-dir -r requirements.txt

# Copy the script to the working directory and make it executable
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

# COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["/usr/bin/supervisord"]

ENTRYPOINT [ "/entrypoint.sh" ]

# copy project
COPY . .

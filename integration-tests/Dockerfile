FROM ubuntu:18.04

ENV USERNAME=user

# Let's start with some basic stuff.
RUN apt-get update -qq && apt-get install -qqy \
    curl \
    python3-pip
# Install Docker from Docker Inc. repositories.
RUN curl -fsSL get.docker.com | sh

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

RUN useradd -m $USERNAME

WORKDIR /home/$USERNAME

# Copy over source code
COPY ./tests/ ./tests/
COPY run-tests.sh ./
COPY swagger.yml ./

RUN chown -R $USERNAME:$USERNAME ./

USER $USERNAME

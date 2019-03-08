#!/usr/bin/env bash
cd ..
docker build . -t nf-server
cd integration-tests
docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d

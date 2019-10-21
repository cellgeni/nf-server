# NF-server

This project helps to submit [Nextflow](https://nextflow.io) pipelines programmatically to a remote server 
as opposed to running them directly from a command line. 

## Overview

The application consists of three parts:
1. Flask server for workflow submission and tracking
2. Celery worker to start Nextflow pipelines
3. Redis message broker

## Installation


```bash
git clone https://github.com/cellgeni/nf-server
```

## Usage


### API
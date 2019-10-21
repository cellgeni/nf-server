#!/usr/bin/env bash

pushd `dirname $0`

export SWAGGER_SCHEMA=./swagger.yml
export NF_SERVER_HOST=http://127.0.0.1:9005

# Setup tests results directory
RESULTS_DIR=test_results/
mkdir -p $RESULTS_DIR

TEST_DIR=$PWD/tests

export PATH=$TEST_DIR:$PATH
pytest $TEST_DIR --junitxml=${RESULTS_DIR}junit.xml $@
rc=$?

popd

exit $rc

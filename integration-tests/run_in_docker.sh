#!/usr/bin/env bash


export NF_AUTH_TOKEN=test-authtoken
export NF_SERVER_HOST=http://nf-server:8000

pushd `dirname $0`

IMAGE_NAME=nf_server_test_runner
CONTAINER_NAME=nf_server_test_runner

cp ../src/nf_server/swagger.yml .
docker rm $CONTAINER_NAME || echo "Ignore error - no container to remove"
docker build -t $IMAGE_NAME:latest .
rm swagger.yml

docker run \
--name $CONTAINER_NAME \
--network host \
--user root \
-e NF_AUTH_TOKEN \
-e NF_SERVER_HOST \
-v /var/run/docker.sock:/var/run/docker.sock \
$IMAGE_NAME ./run-tests.sh $@

rc=$?
mkdir -p test_results/
docker cp $CONTAINER_NAME:/home/user/test_results/junit.xml test_results/

popd

exit $rc

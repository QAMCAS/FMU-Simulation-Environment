#!/bin/bash
docker rmi fmu_docker_env
docker build --no-cache=true ../fmu_docker_server/. -t fmu_docker_env --platform linux/amd64

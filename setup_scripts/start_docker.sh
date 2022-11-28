#!/bin/bash
printf ">>> \n \n"
for name in "$@"
do
    if [[ $name == *":"* ]]
    then
        IFS=":" read -r str port <<< "${name}"
        printf "> docker name  : ${str} \n"
        printf "> docker port  : $port \n"
        printf "> start docker :"
        docker run -d -p $port:5000 --name ${str} fmu_docker_env
        printf "\n"
    else
        printf "> docker name  : $name \n"
        printf "> port auto selection ... \n"
        printf "> start docker :"
        docker run -d -p 0:5000 --name $name fmu_docker_env
        printf "\n"
    fi
done

printf "> running docker  :\n"
docker ps -a
printf "\n"
printf "<<< \n"
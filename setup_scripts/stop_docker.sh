#!/bin/bash
printf ">>> \n \n"
for name in "$@" 
do
    printf "> stop docker   : ";
    docker stop $name
    printf "> remove docker : ";
    docker rm $name
    printf "\n"
done
printf "<<< \n"
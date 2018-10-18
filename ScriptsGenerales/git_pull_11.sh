#!/bin/bash

USERNAME="isis"
declare -a HOSTS=(
 "172.24.101.207"
 "172.24.101.208"
 "172.24.101.209"
 "172.24.101.210"
 "172.24.101.211"
 "172.24.101.212"
 "172.24.101.213"
 "172.24.101.214"
 "172.24.101.215"
 "172.24.101.216"
)
cd  ~/Taller4y5InfracomTephaDomain/ && git reset --hard && git pull -f
SCRIPT="cd  Taller4y5InfracomTephaDomain/ && git reset --hard && git pull -f"
for HOSTNAME in ${HOSTS[@]};
do
    ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}" &
done
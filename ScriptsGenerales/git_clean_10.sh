#!/bin/bash

#
#
#
#
#  Solo usar en caso extremo.
#
#
#
#


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
SCRIPT="cd  Taller4y5InfracomTephaDomain/ && git reset --hard && git clean -fd :/"
for HOSTNAME in ${HOSTS[@]};
do
    ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}" &
done

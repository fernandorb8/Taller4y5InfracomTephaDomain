#!/bin/bash

# 1 clients
USERNAME = "isis"
PASS = "labredesML340"
HOST = ("172.23.66.31")
SCRIPT="git clone https://github.com/fernandorb8/Taller4y5InfracomTephaDomain"
for HOSTNAME in ${HOSTS} ; do
    ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}"
done
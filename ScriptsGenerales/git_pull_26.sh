#!/bin/bash

USERNAME="isis"
declare -a HOSTS=(
	"172.23.66.31"
	"172.23.66.32"
	"172.23.66.33"
	"172.23.66.34"
	"172.23.66.35"
	"172.23.66.36"
	"172.23.66.37"
	"172.23.66.38"
	"172.23.66.39"
	"172.23.66.40"
	"172.23.66.41"
	"172.23.66.42"
	"172.23.66.43"
	"172.23.66.44"
	"172.23.66.45"
	"172.23.66.46"
	"172.23.66.47"
	"172.23.66.48"
	"172.23.66.49"
	"172.23.66.50"
	"172.23.66.52"
	"172.23.66.54"
	"172.23.66.55"
	"172.24.101.215"
	"172.24.101.216"
)
cd  ~/Taller4y5InfracomTephaDomain/ && git reset --hard && git pull -f
SCRIPT="cd  ~/Taller4y5InfracomTephaDomain/ && git reset --hard && git pull -f"
for HOSTNAME in ${HOSTS[@]};
do
    ssh -l ${USERNAME} ${HOSTNAME} "${SCRIPT}" &
done

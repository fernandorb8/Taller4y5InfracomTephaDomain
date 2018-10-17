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
)
# SCRIPT="ls | grep Taller4y5InfracomTephaDomain"
# SCRIPT="df | grep /dev/sda1"
# SCRIPT="df | grep /dev/sda1"
# SCRIPT="du ~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_25_1_250"

# use for loop to read all values and indexes
for (( i=1; i<${#HOSTS[@]}+1; i++ ));
do
	
# 	SCRIPT="grep -n \"el tiempo de descarga fue\" ~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_25_1_250/client_${i}.log"
	echo "==========" ${HOSTS[$i-1]} "=========="
#     ssh -l ${USERNAME} ${HOSTS[$i-1]} "${SCRIPT}" 
	ssh -l ${USERNAME} ${HOSTS[$i-1]} grep -n "descarga" "~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_25_1_250/client_${i}.log"
done

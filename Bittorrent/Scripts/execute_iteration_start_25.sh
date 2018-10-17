#!/bin/bash


NUMCLIENTS=23
NUMITER=5
TORFILE=500
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


# use for loop to read all values and indexes
for (( i=2; i<${NUMCLIENTS}+1; i++ ));
do
	if [ $i -lt 10 ] 
	then PREFIX="000"
	else PREFIX="00"
	fi		
	SCRIPT="cd ~/Taller4y5InfracomTephaDomain/Bittorrent/ && python3 client.py --torrent myfile_${TORFILE}.torrent --host ${HOSTS[$i-1]} --out client_${i}.log --out_folder Clients_${NUMCLIENTS}_${NUMITER}_${TORFILE} --cliversion ${PREFIX}${i} --port 688${NUMITER}"

    ssh -l ${USERNAME} ${HOSTS[$i-1]} "${SCRIPT}" &
done

tail -f Bittorrent/Clients_${NUMCLIENTS}_${NUMITER}_${TORFILE}/tracker.log
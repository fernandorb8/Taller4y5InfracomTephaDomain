#!/bin/bash


NUMCLIENTS=3
NUMITER=2
TORFILE=250
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

cd ~/Taller4y5InfracomTephaDomain/Bittorrent/ && python3.7 tracker.py --host 157.253.205.65 --out tracker.log --out_folder Clients_${NUMCLIENTS}_${NUMITER}_${TORFILE}&

# use for loop to read all values and indexes
for (( i=1; i<${NUMCLIENTS}+1; i++ ));
do
	if [ $i -lt 10 ] 
	then PREFIX="000"
	else PREFIX="00"
	fi		
	SCRIPT="cd ~/Taller4y5InfracomTephaDomain/Bittorrent/ && python3 client.py --torrent myfile_${TORFILE}.torrent --host ${HOSTS[$i-1]} --out client_${i}.log --out_folder Clients_${NUMCLIENTS}_${NUMITER}_${TORFILE} --cliversion ${PREFIX}${i} --port 688${NUMITER}"
	
	if [ $i -eq 1 ] 
	then SCRIPT="${SCRIPT} --seed"
	fi

    ssh -l ${USERNAME} ${HOSTS[$i-1]} "${SCRIPT}" &
done

tail -f Bittorrent/Clients_${NUMCLIENTS}_${NUMITER}_${TORFILE}/tracker.log
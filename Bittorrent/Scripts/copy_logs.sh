#!/bin/bash
declare -a NUMCLIENTS=(2 3 4) 
declare -a NUMITER=(1 2 3 4 5) 
declare -a TORFILE=(250)
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
for i in ${NUMCLIENTS[@]};
do
	for j in ${TORFILE[@]};
	do
		for k in ${NUMITER[@]};
		do
			for (( l=1; l<${i}+1; l++ ));
			do	
				#mkdir ~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_${i}_${k}_${j} 			
				#echo SCRIPT="${USERNAME}@${HOSTS[$l-1]}:~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_${i}_${k}_${j}/client_${l}.log   ~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_${i}_${k}_${j}/client_${l}.log"		
			    scp ${USERNAME}@${HOSTS[$l-1]}:~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_${i}_${k}_${j}/client_${l}.log   ~/Taller4y5InfracomTephaDomain/Bittorrent/Clients_${i}_${k}_${j}/client_${l}.log
			done
		done
	done
done
#!/bin/bash
declare -a NUMCLIENTS=(23) 
declare -a NUMITER=(1 2 3 4 5) 
declare -a TORFILE=(250 500)
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
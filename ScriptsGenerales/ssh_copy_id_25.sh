#!/bin/bash
#ssh-keygen -t rsa -b 2048 must have been generated phraseless. https://serverfault.com/questions/241588/how-to-automate-ssh-login-with-password
USERNAME="isis"
PASSWORD="labredesML340"
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
	"172.23.66.51"
	"172.23.66.52"
	"172.23.66.53"
	"172.23.66.54"
	"172.23.66.55"
)
for HOSTNAME in ${HOSTS[@]};
do
    ssh-copy-id ${USERNAME}@${HOSTNAME}
done

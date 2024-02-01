#!/bin/bash

# Make directories
mkdir $1/$2 
mkdir $1/$2/nmap
mkdir $1/$2/enum
mkdir $1/$2/exploit
mkdir $1/$2/privesc

echo "[*] Made directories!"

# Fill out README file
echo "# $2" >> $1/$2/README.md
echo "" >> $1/$2/README.md


# Sign
echo "> Gustav Lundgren | $(date +"%y-%m-%d")" >> $1/$2/README.md
echo "" >> $1/$2/README.md
echo "---" >> $1/$2/README.md
echo "" >> $1/$2/README.md

# Template
echo '```bash' >> $1/$2/README.md
echo "export IP=$3" >> $1/$2/README.md
echo '```' >> $1/$2/README.md

echo "" >> $1/$2/README.md
echo "## Nmap" >> $1/$2/README.md

echo "[*] Starting nmap scan..."

# Run Nmap
ports=$(nmap -p- --min-rate=1000 -T4 $3 | grep ^[0-9] | cut -d '/' -f 1 | tr '\n' ',' | sed s/,$//)

echo "[*] Found open ports $ports"
echo "[*] Running scripts and checking services..."

IFS=',' read -ra array <<< "$ports"

for port in "${array[@]}"; do

	echo "[*] Current port is $port..."

	nmap_output=$(nmap -p$port -sC -sV $3)
	echo "$nmap_output" >> $1/$2/nmap/port_$port

	start_line=$(echo "$nmap_output" | grep -n "Host" | cut -d: -f1)
	end_line=$(echo "$nmap_output" | grep -n "Service detection performed" | cut -d: -f1)

	echo "" >> $1/$2/README.md
	echo '```bash' >> $1/$2/README.md
	echo "$nmap_output" | sed -n "$((start_line+2)),$((end_line-2))p" >> $1/$2/README.md
	echo '```' >> $1/$2/README.md
done

echo "[*] Scan complete!"

# Template
echo "" >> $1/$2/README.md
echo "## Enum" >> $1/$2/README.md

echo "" >> $1/$2/README.md
echo "## Exploit" >> $1/$2/README.md

echo "" >> $1/$2/README.md
echo "## Submit user flag" >> $1/$2/README.md

echo "" >> $1/$2/README.md
echo "## Privesc" >> $1/$2/README.md

echo "" >> $1/$2/README.md
echo "## Submit root flag" >> $1/$2/README.md

echo "" >> $1/$2/README.md
echo "## Länkar" >> $1/$2/README.md

echo "[*] Everythong is Done!"
echo "[*] Run cd $2"

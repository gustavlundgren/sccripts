#!/usr/bin/python3

import argparse
import subprocess
import os
from datetime import datetime 
import re
import shlex

parser = argparse.ArgumentParser(description="Enum script for a new box")
parser.add_argument("--path")
parser.add_argument("--name")
parser.add_argument("-i", "--ip")
parser.add_argument("--web", action=argparse.BooleanOptionalAction, default=False)
parser.add_argument("-v", "--verbose", action=argparse.BooleanOptionalAction, default=False)

def initial_enumeration():
    # Skapa Alla Mappar
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.makedirs(f"{folder_path}/nmap")
        os.makedirs(f"{folder_path}/enum")
        os.makedirs(f"{folder_path}/exploit")
        os.makedirs(f"{folder_path}/privesc")
    
    # Fill out README
    f = open(f"{folder_path}/README.md", "a")
    f.write(f'# {name}\n\n> Gustav Lundgren | {datetime.now().strftime("%Y-%m-%d")}\n\n## Nmap\n\n')


    # Hittar alla öppna portar
    if verbose:
        print("[i] Starting nmap scan...")

    inital_scan_command = shlex.split(f'nmap -oN {folder_path}/nmap/open_ports {ip}')
    nmap_result = subprocess.run(inital_scan_command, capture_output=True, text=True)

    if nmap_result.returncode == 0:
        open_ports = re.findall(r'(\d+)/tcp\s+open', nmap_result.stdout)

        if verbose:
            print(f'[*] Found open ports {", ".join(open_ports)}')
    else:
        if verbose:
            print("[!] Initial nmap scan failed")
        exit(0)

    # Gör en djupare scan på alla öppna portar
    for port in open_ports:  

        if verbose:
            print(f"[i] Now scanning port {port}...")

        port_command = shlex.split(f'nmap -p{port} -sC -sV -oN {folder_path}/nmap/port_{port} {ip}')
        port_scan = subprocess.run(port_command, capture_output=True, text=True)

        if port_scan.returncode == 0:
            pattern = re.compile(r"Host is up.*?\n(.*?)\nService detection performed", re.DOTALL)
            matches = re.search(pattern, port_scan.stdout)

            if matches:
                scan_result = matches.group(1)
        
            f.write(f'```{scan_result}```\n')
        else:
            if verbose:
                print(f"[!] Failed to enumerate port {port}")
            exit(1)

    f.write(f'## Enum\n\n## Exploit\n\n## Submit user flag\n\n## Privesc\n\n## Submit root flag\n\n## Länkar')

    if verbose:
        print("[*] Scan completed successfully")


def enumerate_http():
    if verbose:
        print("[i] Starting web enumeration...")
        
    ports_file = open(f"{folder_path}/nmap/open_ports")
    ports = ports_file.read()

    pattern = re.compile(r"(\d+)/tcp\s+\w+\s+(\w+)", re.MULTILINE)
    matches = re.findall(pattern, ports)

    for match in matches:
        port, service = match

        if service == "http":

            if verbose:
                print(f"[i] Enumerating port {port}")

            # Gobuster
            gobuster_command = shlex.split(f"gobuster dir -u http://{ip}:{port}/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt")
            gobuster_scan = subprocess.run(gobuster_command, capture_output=True, text=True)

            # Nikto
            nikto_command = shlex.split(f'nikto --host {ip} -p {port}')
            nikto_scan = subprocess.run(nikto_command, capture_output=True, text=True)

            # Write to files
            gobuster_file = open(f"{folder_path}/enum/gobuster.log", "a")
            gobuster_file.write(gobuster_scan.stdout)

            nikto_file = open(f"{folder_path}/enum/nikto.log", "a")
            nikto_file.write(nikto_scan.stdout)


if __name__ == '__main__':
    args = parser.parse_args()
    path = args.path
    name = args.name
    ip = args.ip
    web = args.web
    verbose = args.verbose

    folder_path = f"{path}/{name}"

    if verbose: 
        print("[i] Making initial README template...")

    initial_enumeration()
    
    if verbose:
        print(f"[*] README file completed at {folder_path}/README.md")

    if web:
        enumerate_http()
    
    print("[*] Everything is done!")




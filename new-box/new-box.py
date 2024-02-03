#!/usr/bin/python3

import argparse
import subprocess
import os
import re
import shlex
from datetime import datetime 
from progress.bar import Bar
from tqdm import tqdm


parser = argparse.ArgumentParser(description="Enum script for a new box")
parser.add_argument("--author", help="Your name. (Firstname Lastname)")
parser.add_argument("--path", help="The path to put the folders for the box")
parser.add_argument("--name", help="The name of the box. (Will also be the name of the folder)")
parser.add_argument("-i", "--ip", help="The ip adress of the box")
parser.add_argument("-V", "--verbose", action=argparse.BooleanOptionalAction, default=False, help="Add this if you want the program to write out it's progress to the console")

def announce(type, msg, bar =None):
    announcement = ""
    match type:
        case "i":
            if verbose:
                announcement = f"[i] {msg}"
        case "e":
            announcement = f"[!] {msg}"
        case "a":
            if verbose:
                announcement = f"[*] {msg}" 

    if announcement != "":
        if bar is not None:
            bar.write(announcement)
        else:
            print(announcement)

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
    f.write(f'# {name}\n\n> {author} | {datetime.now().strftime("%Y-%m-%d")}\n\n---\n\n```bash\nexport IP={ip}\n```\n\n## Nmap\n\n')


    # Hittar alla öppna portar
    announce("i", "Starting nmap scan...")

    inital_scan_command = shlex.split(f'nmap -sV -oN {folder_path}/nmap/open_ports {ip}')
    nmap_result = subprocess.run(inital_scan_command, capture_output=True, text=True)

    if nmap_result.returncode == 0:
        open_ports = re.findall(r'(\d+)/tcp\s+open', nmap_result.stdout)
        
        announce("a", f'Found open ports {", ".join(open_ports)}')
    else:
        announce("e", "Initial nmap scan failed")
        exit(0)

    # Gör en djupare scan på alla öppna portar
    with tqdm(total=len(open_ports), desc=f"Scanning ports...", unit="port") as pbar:
        for port in open_ports:  
            
            announce("i", f'Now scanning port {port}...', bar=pbar)

            port_command = shlex.split(f'nmap -p{port} -sC -sV -oN {folder_path}/nmap/port_{port} {ip}')
            port_scan = subprocess.run(port_command, capture_output=True, text=True)

            if port_scan.returncode == 0:
                pattern = re.compile(r"Host is up.*?\n(.*?)\nService detection performed", re.DOTALL)
                matches = re.search(pattern, port_scan.stdout)

                if matches:
                    scan_result = matches.group(1)
            
                f.write(f'```{scan_result}```\n')
            else:
                announce("e", f'Failed to enumerate port {port}', bar=pbar)
                exit(1)

            pbar.update(1)

    f.write(f'## Enum\n\n## Exploit\n\n## Submit user flag\n\n## Privesc\n\n## Submit root flag\n\n## Länkar')
    
    announce("a", "Scan completed successfully")


def enumerate_http():
    announce("i", "Starting web enumeration...")
        
    ports_file = open(f"{folder_path}/nmap/open_ports")
    ports = ports_file.read()

    pattern = re.compile(r"(\d+)/tcp\s+\w+\s+(\w+)", re.MULTILINE)
    matches = re.findall(pattern, ports)
    
    with tqdm(total=len(matches)*2, desc=f"Enumerationg web service...", unit="port") as pbar:
        for match in matches:
            port, service = match

            if service == "http" or service == 'https':
                
                announce("i", f'Port {port} is running {service}', bar=pbar)

                # Gobuster
                if service == 'http':
                    gobuster_command = shlex.split(f"gobuster dir -u {service}://{ip}:{port}/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt")
                else:
                    gobuster_command = shlex.split(f"gobuster dir -u {service}://{ip}:{port}/ -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -k")
                gobuster_scan = subprocess.run(gobuster_command, capture_output=True, text=True)
                
                pbar.update(1)


                # Nikto
                nikto_command = shlex.split(f'nikto --host {ip} -p {port}')
                nikto_scan = subprocess.run(nikto_command, capture_output=True, text=True)
                
                pbar.update(1)

                # Write to files
                gobuster_file = open(f"{folder_path}/enum/gobuster.log", "a")
                gobuster_file.write(gobuster_scan.stdout)

                nikto_file = open(f"{folder_path}/enum/nikto.log", "a")
                nikto_file.write(nikto_scan.stdout)
        

if __name__ == '__main__':
    args = parser.parse_args()
    author = args.author
    path = args.path
    name = args.name
    ip = args.ip
    verbose = args.verbose

    folder_path = f"{path}/{name}"

    announce("i", "Making initial README template...")

    initial_enumeration()
    
    announce("a", f'README file completed at {folder_path}/README.md')

    enumerate_http()
    
    announce("a", "Everything is done!")
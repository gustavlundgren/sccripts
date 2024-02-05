#!/usr/bin/python3

import argparse
import logging
from scapy.all import IP, TCP, sr1 
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import randint

# Set scapy logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

parser = argparse.ArgumentParser(description="Scan a target for open ports")
parser.add_argument("-i", "--ip", help="Target ip adress")
parser.add_argument("-p", "--port",type=int, default=0, help="Target port")
parser.add_argument("-t", "--threads",type=int, default=4, help="Number of threads to use")


def scan_port(ip, port):
    try:
        response = sr1(IP(dst=ip)/TCP(sport=randint(1024,65535), dport=port, flags="S"), timeout=1, verbose=0)
        
        if response is not None and response[TCP].flags == "SA":
            print(response.show())
            return port
        
        return None
    
    except Exception as e:
        print(f'Error {e}')


def scan_all_ports(ip, threads):
    ports = range(1, 65000)
    open_ports = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in ports}

        with tqdm(total=len(ports), desc="Finding live ports...", unit="ports") as pbar:
            for future in as_completed(futures):
                port = futures[future]
                result = future.result()

                if result is not None:
                    pbar.write(f"[*] Port {port} is up")
                    open_ports.append(port)
                
                pbar.update(1)
    
    return open_ports


if __name__ == '__main__':
    args = parser.parse_args()
    ip = args.ip
    port = args.port
    threads = args.threads 

    if port != 0:
        result = scan_port(ip, port)

        if result is not None:
            print(f'[*] Port {port} is up')
    else:
        print("[i] Starting scan...")
        scan_all_ports(ip, threads)

    print("[i] Scan is done")
    
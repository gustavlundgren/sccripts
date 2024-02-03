#!/usr/bin/python3

import os
import argparse
from ipaddress import ip_network
from scapy.all import sr1,IP,ICMP
from progress.bar import Bar
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser(description="Ping a host")
parser.add_argument("--network", help="Subnet to scan")
parser.add_argument("--netmask", help="Netmask to find range")
parser.add_argument("--interface", default="eth0", help="Interface to send packets on. Will be eth0 by default")

# Instansiate lock
lock = Lock()

def ping(ip, interface):
    try:
        response = sr1(IP(dst=str(ip))/ICMP(), timeout=1, iface=interface, verbose=0)
        
        return response
                     
    except Exception as e:
        print(f"[!] Failed to scan ip {ip} whith error {e}")
        exit(0)


def ping_sweep(network, netmask, interface):
    live_hosts = []
    hosts = list(ip_network(f'{network}/{netmask}', strict=False).hosts())
    num_threads = os.cpu_count()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(lambda h: ping(h, interface), host): host for host in hosts}

        for i, future in enumerate(as_completed(futures), start=1):
            host = futures[future]
            result = future.result()

            with lock:
                if result is not None:
                    print(f"[*] Host {host} is online")
                    live_hosts.append(result)

        with Bar("Scanning...",suffix='%(percent).1f%% - %(eta)ds', max=len(hosts)) as bar:
            for i, future in enumerate(as_completed(futures), start=1):
                bar.next()   
    
    return live_hosts



if __name__ == "__main__":
    args = parser.parse_args()
    network = args.network
    netmask = args.netmask
    interface = args.interface


    if network is None or netmask is None:
        print("[!] Both network and netmask needs to be supplied")
        exit(1)

    result = ping_sweep(network, netmask, interface)

    print("[*] Found the following live hosts:")

    for host in result:
        print(f'[*] {host}')
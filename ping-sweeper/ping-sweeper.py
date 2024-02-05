#!/usr/bin/python3

import sys
import os
import logging
import argparse
from ipaddress import ip_network
from scapy.all import sr1,IP,ICMP
from tqdm import tqdm
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import my own modules
sys.path.append(f'/home/{os.getlogin()}/scripts/announcer')
from Announcer import Announcer

parser = argparse.ArgumentParser(description="Ping a host")
parser.add_argument("--network", help="Subnet to scan")
parser.add_argument("--netmask", help="Netmask to find range")
parser.add_argument("-t", "--threads", type=int, default=4, help="Amount of threads to use")
parser.add_argument("--interface", default="eth0", help="Interface to send packets on. Will be eth0 by default")
parser.add_argument("-V", "--verbose",action=argparse.BooleanOptionalAction, default=False, help="Use this flag if you want the program to output status")

lock = Lock()

# Set scapy logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def ping(ip, interface, announcer):
    try:
        response = sr1(IP(dst=str(ip))/ICMP(), timeout=1, iface=interface, verbose=False)

        return response
                     
    except Exception as e:
        announcer.announce("e", f"Failed to scan ip {ip} whith error {e}")
        exit(0)


def ping_sweep(network, netmask, threads, interface, announcer):
    live_hosts = []
    hosts = list(ip_network(f'{network}/{netmask}', strict=False).hosts())
    num_threads = threads

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(lambda h: ping(h, interface, announcer), host): host for host in hosts}

        with tqdm(total=len(hosts), desc="Finding live hosts...", unit="host") as pbar:
            for i, future in enumerate(as_completed(futures), start=1):
                host = futures[future]
                result = future.result()

                    
                if result is not None:
                    announcer.announce("a", f"Host {host} is online", bar=pbar)
                    live_hosts.append(result) 

                pbar.update(1) 
                
    return live_hosts



if __name__ == "__main__":
    args = parser.parse_args()
    network = args.network
    netmask = args.netmask
    threads = args.threads
    interface = args.interface
    verbose = args.verbose

    announcer = Announcer(verbose)

    if network is None or netmask is None:
        announcer.announce("e", "Both network and netmask needs to be supplied")
        exit(1)

    live_hosts = ping_sweep(network, netmask, threads, interface, announcer)

    announcer.announce("a", '\nFound the following live hosts')

    for host in live_hosts:
        announcer.announce("a", host)
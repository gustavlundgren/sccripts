#!/usr/bin/python3

import argparse
from scapy.all import IP, TCP, sr1 
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


parser = argparse.ArgumentParser(description="Scan a target for open ports")
parser.add_argument("-i", "--ip", help="Target ip adress")


def scan_one_port(ip, port):
    try:
        ip_header = IP(src="10.10.10.5", dst=ip)
        tcp_header = TCP(sport=12345, dport=port, flags="S") 
        syn_packet = ip_header / tcp_header

        response = sr1(syn_packet, timeout=1, verbose=0)
        
        return response
    
    except Exception as e:
        print(f'Error {e}')


def scan_all_ports(ip):
    ports = range(1, 65000)

    with ThreadPoolExecutor(max_workers=10) as executor:
        with tqdm(total=len(ports), desc="Scanning ports", unit="ports"):
            
            futures = {executor.submit(lambda p: scan_one_port(ip, p)): port for port in ports}

            for future in as_completed(futures):
                port = futures[future]
                
                print(port)


if __name__ == '__main__':
    args = parser.parse_args()
    ip = args.ip

    print(scan_one_port(ip, 80))
    
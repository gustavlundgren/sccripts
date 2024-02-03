#!/usr/bin/python3 

import argparse
import requests
from tqdm import tqdm 
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys


# Import my own modules
sys.path.append("../announcer")
from Announcer import Announcer

# Get full host adress, get wordlist, get whitelist and get verbose mode 
parser = argparse.ArgumentParser(description="Fuzz api endpoints")
parser.add_argument("-u", "--url", help="The base url of api to fuzz")
parser.add_argument("-w", "--wordlist", help="Wordlist to use for the fuzz")
parser.add_argument("-s", "--whitelist", default='200', help="Whitelistet http codes for valid endpoint. Example 200,301")
parser.add_argument("-t", "--threads", type=int, default=4, help="Number of threads to use")
parser.add_argument("-V", "--verbose",action=argparse.BooleanOptionalAction, default=False, help="Use this flag if you want the program to output status")

# Send request to url
def check_endpoint(url, session):
    try:
        with session.get(f'{url}', timeout=10) as response:
            return response

    except Exception as e:
        announcer.announce("e", f'Request to word failed with error {e}')
        exit(0)
    finally:
        response.close()

# Loop trough all words in wordlist and send request to api. 
def fuzzer(url, wordlist, whitelist, threads, announcer):
    valid_endpoints = []

    num_threads = threads

    wordlist_file = open(wordlist, "r")
    words = [e.strip() for e in wordlist_file.readlines() if not e.startswith("#")]

    valid_response_codes = whitelist.split(",")

    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            with tqdm(total=len(words), desc="Fuzzing endpoints", unit="req") as pbar:
                futures = {executor.submit(check_endpoint, f'{url}/{word}', session): word for word in words}

                for future in as_completed(futures):
                    word = futures[future]
                    result = future.result()

                    if str(result.status_code) in valid_response_codes:
                        announcer.announce("a", f'{word}\t[Status: {result.status_code}, Size: {len(result.content)} Time: {round(result.elapsed.total_seconds() * 1000)} ms]', bar=pbar)

                        valid_endpoints.append(word)

                    pbar.update(1)

    return valid_endpoints

# Main function 
if __name__ == '__main__':
    args = parser.parse_args()
    
    url = args.url
    wordlist = args.wordlist
    whitelist = args.whitelist
    threads = args.threads
    verbose = args.verbose

    announcer = Announcer(verbose)

    if url[len(url)-1] == "/":
        url = url[:len(url)-1]

    valid_endpoints = fuzzer(url, wordlist, whitelist, threads, announcer)
    


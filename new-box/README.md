# Note taking template

This is a simple project that makes a template for notes when taking on a pentest lab such as Hack the Box or Try Hack Me. The script will make all the nessesary folders and files and also do some basic enumerations to get you started.

## Getting Started

### Installing

```bash
git clone https://github.com/gustavlundgren/scripts/blob/a51b20590300302df8f479dc0df419508152f7fe/new-box/new-box.py
```

### Usage

```bash
$ ./new-box.py -h

usage: new-box [-h] [--path PATH] [--name NAME] [-i IP] [-V | --verbose | --no-verbose]

Enum script for a new box

options:
  -h, --help            show this help message and exit
  --path PATH           The path to put the folders for the box
  --name NAME           The name of the box. (Will also be the name of the folder)
  -i IP, --ip IP        The ip adress of the box
  -V, --verbose, --no-verbose Add this if you want the program to write out it's progress to the console
```

Example usage of this script when starting the boc Blue

```bash
./new-box.py --author 'John Doe' --path /home/john --name Blue --ip 10.10.11.15 -v
```

This will make a folder at `/home/john/Blue` with subfolders nmap, enum, exploit and privesc.

In the nmap folder will be one file with the result of a nmap scan for each open port

If there is open ports running a http server the enum folder will contain `gobuster.log` and `nikto.log` with initial scans
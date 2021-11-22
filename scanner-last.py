import os
import sys
import requests
import argparse
import platform
import re
import subprocess
import ipaddr
import socket
import threading
import time
from netaddr import IPNetwork, IPAddress
from vars import sub_domain, short_ports, long_ports

connected_hosts = []

def scanPing(host):
    global connected_hosts
    if OS == "Linux":
        output = subprocess.Popen(
            ["ping", "-w", "1", "-W", "1", str(host)], stdout=subprocess.PIPE
        ).communicate()[0]
        if "icmp_seq=1 ttl=" in output.decode("utf-8") or "icmp_seq=1 received" in output.decode('utf-8'):
            print(str(host), "is Online")
            connected_hosts.append(str(host))
    else:
        output = subprocess.Popen(
            ["ping", "-n", "1", "-w", "250", str(host)], stdout=subprocess.PIPE
        ).communicate()[0]
        if "re\x87us = 1" in output.decode("ISO-8859-1"):
            print(str(host), "is Online")
            connected_hosts.append(str(host))

def scanDomain(domain, outputs):

    discovered_subdomains = []

    for sub in sub_domain:
        url = f"http://{sub}.{domain}"
        try:
            requests.get(url)
        except requests.ConnectionError:
            pass
        else:
            print("Discovered subdomain : ", url)
            discovered_subdomains.append(url)
    
    if outputs != None:
        with open(outputs, 'a') as file:
            for sub in range(len(discovered_subdomains)):
                file.write("Discovered subdomain : "+discovered_subdomains[sub]+"\n")

def scanLinux(options):

    os.system("ip a > network.txt")
    path = subprocess.check_output("pwd").decode().strip()
    path = path + "/network.txt"

    if os.path.isfile(path) == False:
        print("\nFile wasn't created")
        exit()

    list = os.listdir(".")
    print("\nDirectory content\n")
    for i in range(len(list)):
        print(list[i])

    choices = {}
    number = 0
    print("\nHere are available IP address \n")
    os.system("grep 'inet ' network.txt | awk '{print $2}' > ip_available")
    with open("ip_available", "r") as ips:
        for ip in ips:
            usable_ip = ip.strip("\n")
            print("[%i] : \t%s" % (number, usable_ip))
            choices[str(number)] = usable_ip
            number += 1

    os.remove("network.txt")
    os.remove("ip_available")
    userChoice = str(input("\nPlease choose the ip you want to target : "))

    while userChoice not in choices:
        print("\nThis is not quite right !")
        userChoice = str(input("\nPlease choose the ip you want to target : "))

    target = ipaddr.IPv4Network(choices[userChoice])

    # Get all hosts on that network
    all_hosts = target.iterhosts()

    for host in all_hosts:
        thread_ping = threading.Thread(target=scanPing, args=(host, ))
        thread_ping.start()

    time.sleep(1)

    if options.outputs != None:
        with open(options.outputs, 'a') as file:
            for ip in range(len(connected_hosts)):
                file.write(connected_hosts[ip]+" is connected !\n")

    if options.ports:
        if options.ports.lower() == "long":
            list_port = long_ports
        elif options.ports.lower() == "short":
            list_port = short_ports
        else:
            print("Scan port option incorrect, selecting short !")
            list_port = short_ports
        
        for host in connected_hosts:
            print("ping")
            sock = socket.socket()
            sock.settimeout(0.5)

            available_ports = []
            for port in list_port:
                try:
                    test = sock.connect((host, port))
                except:
                    print("Port : "+str(port)+" closed, on host : "+host)
                else:
                    print("Port : "+str(port)+" opened, on host : "+host)
                    available_ports.append(str(port))
            time.sleep(1)

            if options.outputs != None:
                with open(options.outputs, 'a') as file:
                    for port in available_ports:
                        file.write("Port : "+port+" open, on host : "+host+" !\n")

def scanWindows(options):

    os.system("ipconfig > ipconfig.txt")
    path = os.getcwd() + "\ipconfig.txt"

    if os.path.isfile(path) == False:
        print("\n le fichier .txt n'a été créé \n")
        exit()

    choices = {}
    number = 0
    print("\n Voici vos adresses IP \n")

    # get every ip and mask by putting them in a file
    os.system("findstr IPv4 ipconfig.txt > ipv4use.txt")
    os.system("findstr Mas ipconfig.txt > maskuse.txt")

    # Print and select function of ip you want to scan
    with open("ipv4use.txt", "r") as ips:
        for ip in ips:

            usable_ip = ip.split(":")[1]
            usable_ip = usable_ip.strip("\n")
            usable_ip = usable_ip.strip(" ")
            print("[%i] : \t%s" % (number, usable_ip))
            choices[str(number)] = usable_ip
            number += 1

    os.remove("ipv4use.txt")
    userChoice = str(input("\nPlease choose the ip you want to target : "))

    while userChoice not in choices:
        print("\nThis is not quite right !")
        userChoice = str(input("\nPlease choose the ip you want to target : "))

    # take mask depenting to ip chosed by user
    file = open("maskuse.txt", "r")
    lines_to_read = [int(userChoice)]

    for position, line in enumerate(file):
        if position in lines_to_read:
            line = line[44:].rstrip()
            CIDR = IPAddress(line).netmask_bits()  # This is the CIDR of ip

    file.close()
    # output of target will be "ip/cidr"
    target = ipaddr.IPv4Network(choices[userChoice])
    target = str(target)[:-2]
    target = target + str(CIDR)
    print(target)

    # ping request
    for host in IPNetwork(target):
        thread_ping = threading.Thread(target=scanPing, args=(host, ))
        thread_ping.start()

    time.sleep(1)

    if options.outputs != None:
        with open(options.outputs, 'a') as file:
            for ip in range(len(connected_hosts)):
                file.write(connected_hosts[ip]+" is connected !\n")

    if options.ports:
        if options.ports.lower() == "long":
            list_port = long_ports
        elif options.ports.lower() == "short":
            list_port = short_ports
        else:
            print("Scan port option incorrect, selecting short !")
            list_port = short_ports
        
        for host in connected_hosts:
            sock = socket.socket()
            sock.settimeout(0.5)

            available_ports = []
            for port in list_port:
                try:
                    test = sock.connect((host, port))
                except:
                    print("Port : "+str(port)+" closed, on host : "+host)
                else:
                    print("Port : "+str(port)+" opened, on host : "+host)
                    available_ports.append(str(port))
            time.sleep(1)

            if options.outputs != None:
                with open(options.outputs, 'a') as file:
                    for port in available_ports:
                        file.write("Port : "+port+" open, on host : "+host+" !\n")


if __name__ == "__main__":

    # initialize the ArgumentParser
    parser = argparse.ArgumentParser()

    # add the arguments
    parser.add_argument("-p", "--ping", help="Scan the network with pings", default=False, action="store_true")
    parser.add_argument("-s", "--ports", help="Scan all available hosts ports", default=False, type=str)
    parser.add_argument("-d", "--domain", help="Scan sub domains for selected domains", default=False, type=str)
    parser.add_argument("-o", "--outputs", help="Outputs data to file", default=None, type=str)

    # and then parse them
    args = parser.parse_args()

    OS = platform.system()

    if args.ping != False:
        if OS == "Linux":
            scanLinux(args)
        elif OS == "Windows":
            scanWindows(args)
        else:
            print("OS non supporté")
            exit()
    else:
        print("You are using "+OS)

    if args.domain:
        if args.outputs:
            scanDomain(args.domain, args.outputs)
        else:
            scanDomain(args.domain, None)

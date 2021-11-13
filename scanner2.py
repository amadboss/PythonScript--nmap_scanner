import os
import sys
import platform
import re
import subprocess
import ipaddr
import socket
from netaddr import IPNetwork
from netaddr import IPAddress

if len(sys.argv) == 2 and sys.argv[1] == "-h":
    print("Ce programme va récupérer les info réseaux d'une machine Linux ou Windows et les sauvergarder sur un fichier puis ressorit les adresses IP présentes")
    exit()

OS = platform.system()
print("OS on your system is ",OS)
list_ports = [22, 80, 443]
if OS == "Linux":

    os.system("ip a > network.txt")
    path = subprocess.check_output("pwd").decode().strip()
    path = path  + "/network.txt"

    if os.path.isfile(path) == False:
        print("\nFile wasn't created")
        exit()
    
    list = os.listdir(".")
    print("\nDirectory content\n")
    for i in range (len(list)):
        print(list[i])
    
    choices = {}
    number = 0
    print("\nHere are available IP address \n")
    os.system("grep 'inet ' network.txt | awk '{print $2}' > ip_available")
    with open("ip_available", "r") as ips:
        for ip in ips:
            usable_ip = ip.strip("\n")
            print("[%i] : \t%s" %(number, usable_ip))
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
    connected_hosts = []
    print()

    for host in all_hosts:
        output = subprocess.Popen(['ping', '-w', '1', '-W', '1', str(host)], stdout=subprocess.PIPE).communicate()[0]
        if "icmp_seq=1" in output.decode('utf-8'):
            connected_hosts.append(host)
            print(str(host), "is Online")
    print()

    if "-s" in sys.argv:
        for host in connected_hosts:
            nom_fichier = str(host).replace(".", "-")+"_scan"
            print("scanning "+ str(host))
            os.system("cat scanning "+ str(host) +" >> "+ str(sys.argv[output+1]))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for port in list_ports:
                test = sock.connect(host, port)
                if test == 0:
                    if "-o" in sys.argv:
                        output = sys.argv.index("-o")
                        os.system("cat "+ nom_fichier +" >> "+ str(sys.argv[output+1]))
                    else:
                        os.system("cat "+nom_fichier)
                        os.remove(nom_fichier)
            print("Complete")
            

elif OS == "Windows":

   os.system("ipconfig > ipconfig.txt")
    path = os.getcwd() + "\ipconfig.txt"

    if os.path.isfile(path) == False:
        print("\n le fichier .txt n'a été créé \n")
        exit()

    list = os.listdir(".")
    print("\n Contenu du dossier \n")
    for i in range (len(list)):
        print(list[i])
    
    choices = {}
    number = 0
    print("\n Voici vos adresses IP \n")
  
    #get every ip and mask by putting them in a file
    os.system("findstr IPv4 ipconfig.txt > ipv4use.txt")
    os.system("findstr Mas ipconfig.txt > maskuse.txt")

    #Print and select function of ip you want to scan
    with open("ipv4use.txt", "r") as ips:
        for ip in ips:
            usable_ip = ip.split(':')[1]
            usable_ip = usable_ip.strip("\n")
            usable_ip = usable_ip.strip(" ")
            print("[%i] : \t%s" %(number, usable_ip))
            choices[str(number)] = usable_ip
            number+=1
    
    os.remove("ipv4use.txt")
    userChoice = str(input("\nPlease choose the ip you want to target : "))

    while userChoice not in choices:
        print("\nThis is not quite right !")
        userChoice = str(input("\nPlease choose the ip you want to target : "))

    #take mask depenting to ip chosed by user
    file = open("maskuse.txt", "r")
    lines_to_read = [int(userChoice)]
    for position, line in enumerate(file):

        if position in lines_to_read:
            line = line[44:].rstrip()
            CIDR = IPAddress(line).netmask_bits() #This is the CIDR of ip
    file.close()
    
    #output of target will be "ip/cidr"
    target = ipaddr.IPv4Network(choices[userChoice])
    target = str(target)[:-2]
    target = target + str(CIDR)
    print(target)
    
    # Get all hosts on that network
    #all_hosts = target.iterhosts()
    connected_hosts = []

    #ping request 
    for host in IPNetwork(target):
        print("target : ",host)
        output = subprocess.Popen(['ping', '-n', '1', '-w', '250', str(host)], stdout=subprocess.PIPE).communicate()[0]
        if "re\x87us = 1" in output.decode('ISO-8859-1'):
            print("This IP is ONLINE")
            connected_hosts.append(host)
            print(str(host), "is Online")
        else:
            print("OFFLINE")
    print("This is the list of all connected hosts")
    print(connected_hosts)

else:
    print("Pas d'OS supporté")

import os
import sys
import platform
import re
import subprocess
import ipaddr
import socket
from netaddr import IPNetwork
from netaddr import IPAddress

scan_port = 0
printl = 0
scan_ping = 0
scan_domain = 0

if len(sys.argv) == 1:
    print("-p pour le scan de ping | -s pour le scan de port | -o pour sortire les resultat dans un fichier")
    print("Subtilité : -s = -p -s  | -o = -p -s -o")
    exit()

for i in range(len(sys.argv)):
    if sys.argv[i] == "-h":
        print("-p pour le scan de ping | -s pour le scan de port | -o pour sortire les resultat dans un fichier")
        print("Subtilité : -s = -p -s  | -o = -p -s -o")
        exit()
    if sys.argv[i] == "-s":
        scan_ping = 1
        scan_port = 1
    if sys.argv[i] == "-o":
        scan_ping == 1
        printl = 1
        scan_port = 1
    if sys.argv[i] == "-d":
        scan_domain = 1
            
OS = platform.system()
#print("OS on your system is ",OS)
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
   
    if scan_ping == 1:
        os.system("ipconfig > ipconfig.txt")
        path = os.getcwd() + "\ipconfig.txt"

        if os.path.isfile(path) == False:
            print("\n le fichier .txt n'a été créé \n")
            exit()

        #list = os.listdir(".")
        #print("\n Contenu du dossier \n")
        #for i in range (len(list)):
        #    print(list[i])
        
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

    if scan_port == 1:
        long_ports = [9,20,21,22,23,25,53,67,68,69,80,110,123,143,389,443,465,500,554,636,1352,1433,1521,1723,3306,3389,5432,6667,1,5,7,9,11,13,17,27,29,31,33,35,37,41,48,52,62,82,101,115,242,256,259,271,280,286,308,333,344,586,660,704,709,729,741,744,747,758,767,769,780,800,810,828,847,853,860,873,886,900,910,953,989,995,1010,1021,1025,1029,1033,1110,1277,1303,1492,1529,1784,2197,2201,2260,2370,2379,2683,2694,2795,2826,2874,2926,3093,3098,3127,3302,3326,3372,3405,3547,3695,3995,4049,4078,4085,4087,4145,4174,4192,4197,4199,4300,4316,4320,4325,4340,4343,4368,4389,4395,4400,4413,4419,4425,4442,4484,4500,4535,4545,4559,4563,4566,4573,4590,4593,4646,4658,4700,4711,4725,4727,4730,4733,4737,4749,4756,4774,4784,4786,4800,4827,4837,4867,4876,4879,4883,4888,4894,4899,4912,4940,4949,4969,4984,4999,5015,5020,5032,5042,5048,5059,5080,5093,5099,5106,5111,5114,5117,5120,5133,5137,5145,5150,5154,5161,5172,5190,5200,5209,5215,5221,5245,5248,5264,5269,5280,5298,5312,5320,5343,5349,5352,5397,5443,5445,5450,5453,5461,5470,5475,5500,5550,5553,5565,5573,5579,5597,5618,5627,5646,5666,5670,5683,5688,5693,5696,5700,5705,5713,5741,5750,5755,5757,5766,5777,5780,5785,5793,5813,5841,5859,5863,5868,5883,5900,5910,5963,5968,5984,5999,6064,6068,6084,6099,6121,6130,6133,6140,6159,6200,6209,6222,6241,6251,6267,6300,6306,6315,6320,6324,6343,6346,6350,6355,6360,6370,6379,6382,6389,6417,6432,6440,6442,6455,6464,6471,6480,6500,6505,6513,6543,6547,6558,6566,6568,6579,6600,6619,6632,6640,6653,6655,6670,6678,6687,6697,6701,6714,6767,6777,6785,6801,6817,6831,6841,6850,6868,6888,6900,6924,6935,6946,6951,6961,6969,6997,7030,7070,7080,7099,7117,7121,7128,7161,7200,7215,7227,7236,7244,7262,7272,7365,7391,7397,7400,7410,7421,7426,7437,7443,7471,7473,7478,7491,7500,7508,7542,7551,7560,7563,7566,7569,7574,7588,7606,7624,7626,7633,7648,7663,7672,7680,7683,7687,7689,7697,7700,7707,7720,7724,7734,7738,7741,7747,7775,7777,7781,7786,7789,7794,7797,7810,7845,7869,7878,7880,7887,7900,7913,7932,7962,7967,7979,7997,7999,8015,8019,8025,8032,8040,8051,8066,8070,8074,8077,8080,8086,8090,8097,8100,8115,8121,8128,8140,8148,8153,8160,8181,8190,8194,8199,8204,8230,8243,8270,8276,8280,8282,8292,8300,8313,8320,8351,8376,8383,8400,8415,8423,8442,8450,8457,8470,8500,8554,8567,8600,8610,8665,8675,8686,8688,8699,8710,8733,8750,8763,8778,8786,8793,8800,8804,8873,8880,8883,8888,8899,8910,8937,8953,8980,8989,8997,9005,9008,9020,9050,9060,9080,9083,9100,9111,9119,9122,9131,9160,9191,9200,9222,9255,9278,9287,9292,9300,9306,9310,9312,9318,9321,9339,9343,9374,9380,9387,9396,9400,9418,9443,9450,9500,9535,9555,9592,9612,9614,9616,9628,9640,9666,9694,9700,9747,9750,9753,9762,9800,9875,9888,9898,9900,9909,9911,9925,9950,9966,9978,9981,9987,9990,10020,10050,10055,10080,10100,10107,10110,10113,10125,10128,10160,10200,10252,10260,10288,10321,10443,10540,10548,10631,10800,10805,10809,10860,10880,10933,10990,11000,11095,11103,11109,11161,11172,11201,11208,11211,11319,11367,11371,11489,11600,11623,11720,11723,11751,11796,11876,11967,11971,12000,12010,12012,12109,12121,12168,12172,12300,12302,12321,12345,12753,12865,13160,13216,13223,13400,13720,13724,13782,13785,13818,13894,13929,14000,14033,14141,14145,14149,14154,14250,14414,14500,14936,15000,15002,15345,15363,15555,15660,15740,15999,16020,16161,16309,16360,16367,16384,16619,16665,16789,16900,16950,16991,17007,17184,17219,17223,17225,17234,17500,17555,17729,17754,17777,18000,18104,18136,18181,18241,18262,18463,18634,18668,18769,18881,18888,19000,19007,19020,19191,19194,19220,19283,19315,19398,19410,19539,19998,20005,20013,20034,20046,20048,20057,20167,20202,20222,20480,20670,20999,21010,21212,21221,21553,21590,21800,21845,22000,22125,22128,22222,22273,22305,22335,22343,22347,22350,22537,22555,22763,22800,22951,23000,23053,23294,23333,23400,23456,23546,24000,24242,24249,24321,24323,24386,24465,24554,24577,24666,24676,24680,24754,24922,25000,25576,25604,25793,25900,26000,26133,26208,26257,26260,26486,26489,27010,27017,27345,27442,27504,27782,27876,27999,28010,28200,28240,28589,29167,29999,30100,30260,30400,30999,31016,31020,31400,31416,31457,31620,31685,31765,31948,32034,32249,32400,32483,32635,32767,32801,32811,32896,33000,33060,33123,33331,33333,33434,33656,34249,34378,34567,34962,34980,35000,35100,35354,36001,36524,36602,36700,36865,37475,37483,37601,37654,38000,38201,38800,38865,39681,40000,40404,40841,41111,41121,41230,41794,42508,43000,43188,43210,43439,44123,44321,44444,44553,44818,44900,45000,45045,45054,45514,45678,45824,45966,46336,46998,47557,47624,47806,47808,48000,48048,48128,48556,48619,48653,49000,49150]
        short_ports = [9,20,21,22,23,25,53,67,68,69,80,110,123,143,389,443,465,500,554,636,1352,1433,1521,1723,3306,3389,5432,6667]
        
        choise = str(input("(Q)uick scan or (L)ong scan ?"))
        if choise == 'Q' or choise == "q":
            ports = short_ports
        elif choise == 'L' or choise == "l":
            ports = long_ports
        else:
            print("Wrong arguments short list taked")
            ports = short_ports

        with open("result.txt", "w") as file:    
            for j in connected_hosts :
                for i in ports :
                    print("scan",j,"port",i)
                    s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)
                    result = s.connect_ex((str(j),i))
                    if result ==0:
                        t = 'port '+ str(i)+ ' open on '+ str(j) + '\n'
                        file.write(str(t)) 
                        print("Port {} is open".format(i))
                    s.close()
        file.close()
        print("--------------")
        file = open("result.txt")
        lines = file.readlines()
        for line in lines:
            print(line)
        file.close()
        
        if printl == 0:
            os.remove("result.txt")

    if scan_domain == 1:

        # Fonction de tri des domaine
        domain= []
        os.system("ipconfig > ipconfig.txt")
        path = os.getcwd() + "\ipconfig.txt"

        if os.path.isfile(path) == False:
            print("\n le fichier .txt n'a été créé \n")
            exit()
        os.system("findstr DNS ipconfig.txt > subuse.txt")

        file = open("subuse.txt", "r")
        for position, line in enumerate(file):
            line = line[44:].rstrip()
            line = line.splitlines()
            if line:
                domain.extend(line)
        file.close()
        os.remove("subuse.txt")
        os.remove("ipconfig.txt")

        i = 0
        j = 0
        while j != len(domain):
            while i != len(domain):
                if domain[j] == domain[i]:
                    domain.pop(i)
                    i = i + 1
                else:
                    i = i + 1
            j = j + 1
        #Fin fonction de tri des domaine
        

        print("Voici le(s) domaine(s) auquelle vous etes connecter :", domain)
        
        sub_domain = ['mail','mail2','www','ns2','ns1','blog','localhost','m','ftp','mobile','ns3','smtp','search','api','dev','secure','webmail','admin','img','news','sms','marketing','test','video','www2','media','static','ads','mail2','beta','wap','blogs','download','dns1','www3','origin','shop','forum','chat','www1','image','new','tv','dns','services','music','images','pay','ddrint','conc']
        #for sub in sub_domain :
           # print(i)
else:
    print("Pas d'OS supporté")
    
    
    
        print("Voici le(s) domaine(s) auquelle vous etes connecter :", domain)
        print("Voulez-vous faire un scan sur un scan sur (c)e domain ou un (a)utre ?")
        choise = str(input())
        sub_domain = ['mail','mail2','www','ns2','ns1','blog','localhost','m','ftp','mobile','ns3','smtp','search','api','dev','secure','webmail','admin','img','news','sms','marketing','test','video','www2','media','static','ads','mail2','beta','wap','blogs','download','dns1','www3','origin','shop','forum','chat','www1','image','new','tv','dns','services','music','images','pay','ddrint','conc']

        if choise == "c" or choise == "C":
            sub_scan(domain)
        if choise == "a" or choise == "A":
            domain = []
            #choise = 
            domain.append(str(input("Veuiller indiquer le domain sur lequelle vous vouler scanner les sous domains")))
            print(domain)
            sub_scan(domain)

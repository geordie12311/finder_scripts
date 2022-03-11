import getpass
import threading
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from rich import print as rprint
from collections import Counter
#Importing various libaries including counter to count the dictionary values for the output of the 
#IP addresses so the functions can identify any duplicates. F filter from nornir.core to enable the user
#to define locations to search or exclude (or leave default for all areas) and threading to clean up 
#the way the data is displayed to the user.

nr = InitNornir(config_file="config.yaml")
password = getpass.getpass()
nr.inventory.defaults.password = password
#above section is initialising nornir and using getpass to prompt the user to enter their password

ipadd_list = []
#creating empty list to hold results of IP address search

LOCK = threading.Lock()
#creating object for threading.Lock that will be used to clean up the data displayed
filtered = False
#setting filtered default as False

answer = input("Would you like to apply a location filter to this script? <y/n> ")
if answer == "y":
    filtered = True
    location = input("Select a location to target: ")
    filter_type = input ("Do you want to include or exclude this location? <include/exclude> ")
    if filter_type == "exclude":
        filtered_hosts = nr.filter(~F(location=location))
    else:
        filtered_hosts = nr.filter(F(location=location))
#The above section is creating an input logic for the user if they wish to filter the search
#by a specific location or to exclude one. Once the user has completed the input depending on their
#answers the logic at the end of the script will trigger the correct logic in the script

def get_ipaddr(task):
    response = task.run(task=send_command, command="show interfaces")
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    interfaces =task.host["facts"]
    for intf in interfaces:
        try:
            ip_key = interfaces[intf]["ipv4"]
            for ip in ip_key:
                ip_addr = ip_key[ip]["ip"]
                ipadd_list.append(ip_addr)
        except KeyError:
            pass
#The above function is going to run the command Show Interfaces and then uing task.host["facts"]
#we are going to send the output to genie parse which will output it in structured data format
#then we use the facts object that contains the data and create an intf object for interfaces
#a ip_key object for the ipv4 information and a ip_key object for ip address of the interface
#finally we create an expection to ignore KeyErrors if there is no IP information on the interface 

def locate_ip(task):
    response = task.run(task=send_command, command="show interfaces")
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    interfaces =task.host["facts"]
    for intf in interfaces:
        try:
            ip_key = interfaces[intf]["ipv4"]
            for ip in ip_key:
                ip_addr = ip_key[ip]["ip"]
                if ip_addr in targets:
                    version_result = task.run(task=send_command, command="show version")
                    task.host["versionfacts"] = version_result.scrapli_response.genie_parse_output()
                    serial_num = task.host["versionfacts"]["version"]["chassis_sn"]
                    LOCK.acquire()
                    print(f"{task.host} {intf} - {ip_addr}")
                    print(f"MGMT IP: {task.host.hostname}")
                    print(f"SERIAL NUMBER: {serial_num}")
                    data = task.host.data
                    for k, v in data.items():
                        if "facts" not in k:
                            print(f"{k}: {v}")
                    print("\n")
                    LOCK.release()
        except KeyError:
            pass
#This function above is also going to use show interfaces command to parse out data to genie parser
#but this time it is going to use the data to display extra information if a duplicate IP was identified
#during the first function. The second task this function will perform is that will run a second command 
#"show version" and again using genie parser will pull out data specific relating to the devices which have 
#been found with a duplicate IP. It is also going to pull data for the host from the hostfile that is held 
# under the data heading that is specfic to the device and print it out along with hostname, IP, 
#interface details etc. 

if filtered:
    filtered_hosts.run(task=get_ipaddr)
    targets = [k for k, v in Counter(ipadd_list).items() if v > 1]
    if targets:
        rprint("[red]ALERT: DUPLICATE IPs DETECTED![/red]")
        rprint(targets)
        rprint("\n[cyan]Locating address locations....[/cyan]\n")
        filtered_hosts.run(task=locate_ip)
    else:
        rprint("I[green]IP SCAN COMPLETED - NO DUPLICATE IPs DETECTED[/green]")
#Above section will be triggered if the user says yes to filter option
else:
    nr.run(task=get_ipaddr)
    targets = [k for k, v in Counter(ipadd_list).items() if v > 1]
    if targets:
        rprint("[red]ALERT: DUPLICATE IPs DETECTED![/red]")
        rprint(targets)
        rprint("\n[cyan]Locating address locations....[/cyan]\n")
        nr.run(task=locate_ip)
    else:
        rprint("I[green]IP SCAN COMPLETED - NO DUPLICATE IPs DETECTED[/green]")
#Above section will be triggered if the user says no to filter option

#These two logic layers triger based on the input from the user at the start regarding 
# filter settings and the outcome of the search of IP addresses is going to trigger the correct
#function. If after collating the IP address information there is duplicates found and stored in 
#the ip_add list it will trigger the locate_IP function above to collate the device hostname, 
#interface etc and also the additional host specific information gathered from the show version
#and from the data section in the host file. If no duplicate IPs are found it will inform the user
#by outputting the NO DUPLICATE IPs DETECTED statement above to the screen

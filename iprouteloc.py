"""
You will need to install the following python libraries for this script:
1. nornir-scrapli
2. rich
"""
#Python script using nornir-scrapli to find routes by type for both Cisco and Arista
import getpass
import os
import time
from ipaddress import ip_address, ip_network
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from rich import print as rprint
#Importing various libaries including ip_address and ip_network from ipaddress which will allow
#us to check for specific IP in a subnet
rprint("[bold red on yellow]***************************THIS SCRIPT WILL FIND AN IP ROUTE ON THE NETWORK*************************[/bold red on yellow]")
time.sleep(2)
#displaying a banner to confirm what the script does to the user
nr = InitNornir(config_file="config.yaml")
print("Please enter your Login credentials")
username = input("username: ")
password = getpass.getpass()
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
#above section is initialising nornir and using getpass to prompt the user to enter 
#their username and password. It will use the credentials to login to each host
target = input("Enter the target IP address: ")
ipaddr = ip_address(target)
my_list = []
CLEAR = "clear"
os.system(CLEAR)
#above section is creating an object called target and will take the input from the user and use it
#later in the script. Also creating an object called ipadder and appending it to the IP_address
#function from ipaddress and linking it to target object. My_list is creating a blank list that will be 
#used to capture output later in the script
def get_cisco_routes(task):
    response = task.run(task=send_command, command="show ip route")
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    prefixes = task.host["facts"]["vrf"]["default"]["address_family"]["ipv4"]["routes"]
#The above function is creating and object called get_cisco_routes and associating it with task. Then we 
#are setting response to be the task (send_command and the command to be sent Show IP route)
#and using genie parser to output the data as structured data. Then we are linking the object 
#prefixes to the task.host output from genie and looking up routes
    for cisco_prefix in prefixes:
        network = ip_network(cisco_prefix)
        if ipaddr in network:
            source_prot = prefixes[cisco_prefix]["source_protocol"]
            if source_prot == "connected":
                try:
                    outgoing_intf = prefixes[cisco_prefix]["next_hop"]["outgoing_interface"]
                    for intf in outgoing_intf:
                        exit_intf = intf
                        print(f"{task.host} is connected to {target} via interface {exit_intf}")
                except KeyError:
                    pass
            else:
                try:
                    next_hop_list = prefixes[cisco_prefix]["next_hop"]["next_hop_list"]
                    route_preference = prefixes[cisco_prefix]["route_preference"]
                    for key in next_hop_list:
                        next_hop = next_hop_list[key]["next_hop"]
                        if route_preference == 20:
                            source_prot = "eBGP"
                        elif route_preference == 200:
                            source_prot = "iBGP"
                        my_list.append(f"{task.host} can reach {target} via next hop {next_hop} ({source_prot})")
                except KeyError:
                    pass
    for uptime in next_hop_list:
        route_uptime = prefixes[cisco_prefix][next_hop][next_hop_list][1]["updated"]
        if route_uptime < "01.00.00":
            my_list.append(f"{task.host} next hop {next_hop} route uptime is less than 1hr")
        else:
            my_list.append(f"{task.host} next hop {next_hop} route uptime is more than 1hr")

#The above section is creating a for loop called cisco_prefix and is going to loop through the prefixes from 
#The routes output from prefixes object for Cisco devices. Then we create a object called network and 
#using ip_network function from ipaddress library we are going to idenifiy the networks in prefix object 
#then we are going to loop through looking for the target IP address in netowrk object and if it is found
#then it is going to find next hop details and print the address, device(s) the route exists on and which 
#network it is advertised in along with next hop details. 
cisco = nr.filter(F(platform="ios"))
cisco.run(task=get_cisco_routes)
#this is going to create an object "cisco" and filter ios platform only devices
#it is then going to run the task get_cisco_routes
if my_list:
    sorted_list = sorted(my_list)
    rprint(sorted_list)
else:
    rprint(f"{target} is not reachable")
#this above section is going to take the object output from the run the task get_cisco_routes
#sort the output and print it out to screen with the relevant next hop information etc.
# If the IP is not found it will display to the screen IP xxxx is not reachable

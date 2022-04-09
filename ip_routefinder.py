""" Python script to find a route on the network. 
Note: You will need to install the following python libraries 
for this script to work:
1. nornir-scrapli
2. rich
"""

import getpass
import os
import time
from ipaddress import ip_address, ip_network
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from rich import print as rprint


rprint("[bold red on yellow]***************************THIS SCRIPT WILL FIND AN IP ROUTE ON THE NETWORK*************************[/bold red on yellow]")
time.sleep(2)
#displaying a banner to confirm what the script does to the user


"""Initialising nornir and using getpass to prompt user for credentials"""

nr = InitNornir(config_file="config.yaml")
print("Please enter your Login credentials")
username = input("username: ")
password = getpass.getpass()
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password


"""Creating blank lists and clearing the screen"""

target = input("Enter the target IP address: ")
ipaddr = ip_address(target)
my_list = []
CLEAR = "clear"
os.system(CLEAR)
#above section is creating an object called target and will take the input from the user and use it later in the script. 
#Also creating an object called ipadder and appending it to the IP_address function from ipaddress and linking it to target object. 
#My_list is creating a blank list that will be used to capture output later in the script

"""Generatinng the route information from cisco hosts"""

def get_cisco_routes(task):
    response = task.run(task=send_command, command="show ip route")
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    prefixes = task.host["facts"]["vrf"]["default"]["address_family"]["ipv4"]["routes"]
#The above function is creating and object called get_cisco_routes and associating it with task. 
#Then setting response to be the task (send_command and the command to be sent Show IP route) and using 
#genie parser to output the data as structured data. Then we are linking the object prefixes to the task.host 
#output from genie and looking up routes
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
                    next_hop_list = prefixes[cisco, prefix]["next_hop"]["next_hop_list"]
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
#The above section is creating a for loop called cisco_prefix and is going to loop through the prefixes from 
#The routes output from prefixes object for Cisco devices. Then we create a object called network and using ip_network function 
#from ipaddress library we are going to idenifiy the networks in prefix object then we are going to loop through looking for the 
#target IP address in netowrk object and if it is found then it is going to find next hop details and print the address, 
# device(s) the route exists on and which network it is advertised in along with next hop details. 


"""Generating the route information from arista hosts"""

def get_arista_routes(task):
    result = task.run(task=send_command, command="show ip route | json")
    task.host["facts"] = json.loads(result.result)
    arista_prefixes = task.host["facts"]["vrfs"]["default"]["routes"]
    for arist_prefix in arista_prefixes:
        net = ip_network(arist_prefix)
        if ipaddr in net:
            route_type = arista_prefixes[arist_prefix]["routeType"]
            vias = arista_prefixes[arist_prefix]["vias"]
            for via in vias:
                exit_intf = via["interface"]
                if route_type == "connected":
                    my_list.append(f"{task.host} is connected to {target} via interface {exit_intf}")
                else:
                    next_hop = via["nexthopAddr"]
                    my_list.append(f"{task.host} can reach {target} via next hop {next_hop} ({route_type})")
#The above function is creating and object called get_arista_routes and associating it with task. Then we are setting 
#response to be the task (send_command and the command to be sent Show IP route | json) to output the data as structured data. 
#Then we create a object called route_type that is going to validate the route type for the route and an object called vias 
#which will be used to verify the exit interface. Then we are going to loop through looking for the target #IP address in 
#network object and if it is found, then it is going to find next hop details and print the address, device(s) the route 
# exists on and which network it is advertised in along with next hop details. 
cisco = nr.filter(F(platform="ios"))
cisco.run(task=get_cisco_routes)
#this is going to create an object "cisco" and filter ios platform only devices it is then going to run the task get_cisco_routes
arista = nr.filter(F(platform="eos"))
arista.run(task=get_arista_routes)
#this is going to create an object "cisco" and filter eos platform only devices it is then going to run the task get_arista_routes
if my_list:
    sorted_list = sorted(my_list)
    rprint(sorted_list)
else:
    rprint(f"{target} is not reachable")
#this above section is going to take the object output from the run the task get_cisco_routes sort the output and print it out to screen
#with the relevant next hop information etc. If the IP is not found it will display to the screen IP xxxx is not reachable

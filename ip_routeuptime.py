"""
You will need to install the following python libraries for this script:
1. nornir-scrapli
2. rich
"""
# Python script using nornir-scrapli to find routes by type for both Cisco and Arista
import getpass
import os
import time
from ipaddress import ip_address, ip_network
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from rich import print as rprint

# Importing various libaries including ip_address and ip_network from ipaddress which will allow
# us to check for specific IP in a subnet
nr = InitNornir(config_file="config.yaml")
password = getpass.getpass()
nr.inventory.defaults.password = password

# above section is creating an object called target and will take the input from the user and use it
# later in the script. Also creating an object called ipadder and appending it to the IP_address
# function from ipaddress and linking it to target object. My_list is creating a blank list that will be
# used to capture output later in the script
def get_routes(task):
    response = task.run(task=send_command, command="show ip route")
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    prefixes = task.host["facts"]["vrf"]["default"]["address_family"]["ipv4"]["routes"]
    for cisco_prefix in prefixes:
        network = ip_network(cisco_prefix)


def route_uptime(task):
    response = task.run(task=send_command, command="show ip route")
    task.host["facts"] = response.scrapli_response.genie_parse_output()
    prefixes = task.host["facts"]["vrf"]["default"]["address_family"]["ipv4"]["routes"]
    for cisco_prefix in prefixes:
        network = ip_network(cisco_prefix)
        next_hop_list = prefixes[cisco_prefix]["next_hop"]["next_hop_list"]
        route_preference = prefixes[cisco_prefix]["route_preference"]
        routetime = prefixes[cisco_prefix]["next_hop"]["next_hop_list"]["updated"]


nr.run(task=route_uptime)
print(route_uptime)

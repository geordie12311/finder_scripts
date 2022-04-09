"""
You will need to install the following python libraries for this script:
1. nornir-scrapli
2. rich
"""
import getpass
import os
import time
from ipaddress import ip_address
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_command
from rich import print as rprint

# Importing various libaries including ip_address and ip_network from ipaddress which will allow
# us to check for specific IP in a subnet
rprint(
    "[bold red on yellow]***************************THIS SCRIPT WILL LOCATE A MAC ADDRESS ON THE NETWORK*************************[/bold red on yellow]"
)
time.sleep(2)
# displaying a banner to confirm what the script does to the user
nr = InitNornir(config_file="config.yaml")
print("Please enter your Login credentials")
username = input("username: ")
password = getpass.getpass()
nr.inventory.defaults.username = username
nr.inventory.defaults.password = password
# above section is initialising nornir and using getpass to prompt the user to enter
# their username and password. It will use the credentials to login to each host
target_list = []
ipadd_list = []
CLEAR = "clear"
os.system(CLEAR)
# creating empty list to hold results of mac address search and clearing screen
target_mac = input("Enter the mac address that you want to find: ")
# prompting the user to ennter the mac address they are searching for
def pull_mac(task):

    interface_result = task.run(task=send_command, command="show interfaces")
    task.host["facts"] = interface_result.scrapli_response.genie_parse_output()
    interfaces = task.host["facts"]
    for interface in interfaces:
        try:
            mac_addr = interfaces[interface]["mac_address"]
            if target_mac == mac_addr:
                target_list.append(mac_addr)
                intf = interface
                print_info(task, intf)
        except KeyError:
            pass
    ip_address = task.host["facts"]
    # for ip in ip_address:
    #    ip_addr = interfaces[interface]["ipv4"]


# above function is going to run show interfaces command and then parse the data using genie to
# output structured data then its going to check for mac_address on the interfaces looking for
# the specified mac as well as the actual interface details. It will then output the findings
# to the target_list, an empty list will trigger the final part of the script #otherwise the
# functions below will use the details in the list to display the output. Ti also will ignore
# key errors
def print_info(task, intf):
    rprint("\n[green]***TARGET MAC IDENTIFIED!***[/green]")
    print(f"MAC ADDRESS: {target_mac} is present on {task.host}'s {intf}\n")
    rprint("\n[cyan] GENERATING Host Device Details....[/cyan]")
    cdp_result = task.run(task=send_command, command="show cdp neighbors")
    task.host["cdpinfo"] = cdp_result.scrapli_response.genie_parse_output()
    dev_id = ""
    index = task.host["cdpinfo"]["cdp"]["index"]
    for num in index:
        local_intf = index[num]["local_interface"]
        if local_intf == intf:
            dev_id = index[num]["device_id"]
            port_id = index[num]["port_id"]
    # above function is going to use genie parser to parse the data and output structured data
    # then its going to run show cdp neighbor to lookup the neighbor interface details
    version_result = task.run(task=send_command, command="show version")
    task.host["verinfo"] = version_result.scrapli_response.genie_parse_output()
    version = task.host["verinfo"]["version"]
    serial_number = version["chassis_sn"]
    operating_system = version["os"]
    firmware_version = version["version"]
    uptime = version["uptime"]
    print(f"Device Serial number is: {serial_number}")
    print(f"Device Operating System is: {operating_system}")
    print(f"Device firmware Version is: {firmware_version}")
    print(f"Device upime is: {uptime}")
    print(f"Device MGMT IP is: {task.host.hostname}")
    if dev_id:
        rprint("\n[cyan] REMOTE CONNECTION DETAILS...[/cyan]")
        print(f"Connect to {port_id} on {dev_id}")


# above part of the function is going to run a show version command and again use genie to parse
# the structured data to find chassis serial, os version, firmware versoin and uptime as well as
# the management IP address. It will then display the findings from the MAC search, if it doesn't
# find it it will tell the user or if it does find it then it will display all the above
# information to the screen. Note if the interface with target mac does not have a remote connection
# the script will just not output the remote connection details
nr.run(task=pull_mac)
if target_mac not in target_list:
    rprint("[red]MAC address you are searching for has not been found[/red]")
# this final section is running the task and going to print the statement MAC address is not
# found if it cannot find the target MAC otherwise it will show which host / interface it is
# connected to and provide the addtional host information as well

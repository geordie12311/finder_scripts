import getpass
import os
import time
from ipaddress import ip_address
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_command
from rich import print as rprint
#Importing various libaries including ip_address and ip_network from ipaddress which will allow
#us to check for specific IP in a subnet
rprint("[bold red on yellow]***************************THIS SCRIPT WILL LOCATE A MAC ADDRESS ON THE NETWORK*************************[/bold red on yellow]")
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

nr = InitNornir(config_file="config.yaml")
target_list = []

CLEAR = "clear"
os.system(CLEAR)

target = input("Enter the mac address that you wish to find: ")


def pull_info(task):

    interface_result = task.run(task=send_command, command="show interfaces")
    task.host["facts"] = interface_result.scrapli_response.genie_parse_output()
    interfaces = task.host["facts"]
    for interface in interfaces:
        try:
            mac_addr = interfaces[interface]["mac_address"]
            if target == mac_addr:
                target_list.append(mac_addr)
                intf = interface
                print_info(task, intf)
        except KeyError:
            pass

def print_info(task, intf):
    rprint("\n[green]*** TARGET IDENTIFIED ***[/green]")
    rprint("\n[cyan]GENERATING DETAILS...[/cyan]")
    print(f"MAC ADDRESS: {target} is present on {task.host}'s {intf}\n")
    cdp_result = task.run(task=send_command, command="show cdp neighbors")
    task.host["cdpinfo"] = cdp_result.scrapli_response.genie_parse_output()
    dev_id = ""
    index = task.host["cdpinfo"]["cdp"]["index"]
    for num in index:
        local_intf = index[num]["local_interface"]
        if local_intf == intf:
            dev_id = index[num]["device_id"]
            port_id = index[num]["port_id"]
    ver_result = task.run(task=send_command, command="show version")
    task.host["verinfo"] = ver_result.scrapli_response.genie_parse_output()
    version = task.host["verinfo"]["version"]
    serial_num = version["chassis_sn"]
    oper_sys = version["os"]
    uptime = version["uptime"]
    version_short = version["version_short"]
    print(f"DEVICE MGMT IP: {task.host.hostname}")
    print(f"DEVICE SERIAL NUMBER: {serial_num}")
    print(f"DEVICE OPERATION SYSTEM: {oper_sys}")
    print(f"DEVICE UPTIME: {uptime}")
    print(f"DEVICE VERSION: {version_short}")
    if dev_id:
        rprint("[cyan]REMOTE CONNECTION DETAILS...[/cyan]")
        print(f"Connected to {port_id} on {dev_id}")


nr.run(task=pull_info)
if target not in target_list:
    rprint("[red]TARGET NOT FOUND[/red]")
import getpass
import getpass
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_command

nr = InitNornir(config_file="config.yaml")
password = getpass.getpass()
nr.inventory.defaults.password = password
#above section is initialising nornir and using getpass to prompt the user to enter their passwor
target_mac = input("Enter the mac address that you want to find: ")
#prompting the user to ennter the mac address they are searching for
def pull_mac(task):
    interface_result = task.run(task=send_command, command="show interfaces")
    task.host["facts"] = interface_result.scrapli_response.genie_parse_output()
    interfaces = task.host["facts"]
    for interface in interfaces:
        mac_addr = interfaces[interface]["mac_address"]
        if target_mac == mac_addr:
            intf = interface
            print_info(task, intf)

def print_info(task, intf):

    print(f"MAC ADDDRESS: {target_mac} is present on {task.host}'s {intf}")
    cdp_result = task.run(task=send_command, command = "show cdp neighbors")
    task.host["cdpinfo"] = cdp_result.scrapli.response.geni_parse.output()
    testvar = task.host["cdpinfo"]
    print(testvar)

nr.run(task=pull_mac)


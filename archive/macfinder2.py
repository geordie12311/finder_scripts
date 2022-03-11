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
#above function is going to run show interfaces command and then parse the data using
#genie to output structured data then its going to check for mac_address on the interfaces
#looking for the specified mac as well as the actual interface details

def print_info(task, intf):
    print(f"MAC ADDRESS: {target_mac} is present on {task.host}'s {intf}")
    cdp_result = task.run(task=send_command, command = "show cdp neighbors")
    task.host["cdpinfo"] = cdp_result.scrapli_response.genie_parse_output()
    index = task.host["cdpinfo"]["cdp"]["index"]
    for num in index:
        local_intf = index[num]["local_interface"]
        if local_intf == intf:
            dev_id = index[num]["device_id"]
            port_id = index[num]["port_id"]
            print(f"Connect to {dev_id} on its interface {port_id}")     
#above function is going to then run a show cdp neighbors command and using genie paset
#the output as structured data then its going find the remote interface that is linked to
#the local interface the MAC is present on and output the details to the screen
nr.run(task=pull_mac)
#finally we are calling the task "pull_mac" to start the process
import ipdb
ipdb.set_trace()
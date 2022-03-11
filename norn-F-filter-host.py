#Python script using nornir.scrapli send configs from file and
#F filter from nornir.core.filter to filter out a specific host in the host file
#based on multiple data attributes and an MOTD banner to it
from distutils import command
import getpass
from nornir import InitNornir
from nornir_scrapli.tasks import send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from rich import print as rprint
#Note we are importing F filter from nornir.core.filter

nr = InitNornir(config_file="config.yaml")
password = getpass.getpass()
nr.inventory.defaults.password = password
#above section is initialising nornir and using getpass to prompt the user to enter their password
def config_push(task):
    task.run(task=send_config, config="username test priv 15 sec test1")
device_host = nr.filter(F(hostname="CSR1"))
#above function is going to use the "contains" logic (which you need to use double underscore)  
#to find all hosts who's town contains the letters "amp" and also where the device function 
#has Az in their device_function name
results = device_host.run(task=config_push)
print_result(results)
#now we create the object results based on the output from the function output
#and the task banner_push and print the results
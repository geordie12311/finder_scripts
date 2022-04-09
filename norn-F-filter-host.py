"""Python script to filter out specific host in host file based on data attributes"""

import getpass
from nornir import InitNornir
from nornir_scrapli.tasks import send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from rich import print as rprint

# Note we are importing F filter from nornir.core.filter


"""Initialising nornir, and using getpass to prompt for password"""
nr = InitNornir(config_file="config.yaml")
password = getpass.getpass()
nr.inventory.defaults.password = password


"""Generating the configuration to send to the hosts"""


def config_push(task):
    task.run(task=send_config, config="username test priv 15 sec test1")


device_host = nr.filter(F(hostname="CSR1"))
# above function is going to use the "contains" logic (which you need to use double underscore)
# to find all hosts who's town contains the letters "amp" and also where the device function
# has Az in their device_function name

results = device_host.run(task=config_push)
print_result(results)

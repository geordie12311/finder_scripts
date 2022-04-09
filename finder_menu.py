"""Menu for Python finder scripts"""
import sys
import time
from rich import print as rprint

def quit():
    rprint("The menu will now wait...")
    time.sleep(2)
    sys.exit()

def menu():
    rprint("*****Exiting Main Menu*****")
    time.sleep(1)

choice = input("""
        A: Run the IP Route Finder Script
        B: Run Duplicate IP Finder Script
        C: Run MAC Address Finder Script
        Q: Quit the programme

        Please make a selection from above menu, you will then be prompted to enter your password
""")
if choice == "A" or choice == "a":
    import ip_routefinder
elif choice == "B" or choice == "b":
    import ip_dupfinder
elif choice == "C" or choice == "c":
    import mac_addressfinder
elif choice == "Q" or choice == "q":
    menu()
else:
    rprint("Error you must enter a valid option from the Menu")

menu
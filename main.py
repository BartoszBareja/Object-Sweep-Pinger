from shower import Shower
from getter import *
import psutil


def main():
    if __name__ == "__main__":  # avoiding recursion

        # initiating two main objects
        main_getter = Getter(psutil.net_if_addrs())
        main_shower = Shower("0", "0", "0")

        # getting network interfaces data and showing them
        interfaces = Getter.get_interfaces(main_getter)
        main_shower.show_interfaces(interfaces)

        if main_shower.get_host() == "::1":
            print("Something went wrong with choosen interface")
            return False

        # sweep pinging
        devices = get_addresses(main_shower.get_host(), main_shower.get_netmask())

        # getting MAC addresses and producers
        out = main_getter.get_macs(devices)

        # adding our device to list
        out.append(main_getter.get_host_mac(main_shower.get_host(), main_shower.get_mac()))

        # displaying final output
        main_shower.show_end_window(out)


main()

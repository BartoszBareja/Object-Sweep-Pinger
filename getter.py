import math
import subprocess
import multiprocessing
import ipaddress
import re
import requests


# getting subnetwork information
def get_subnet_info(netmask):
    if netmask != 'None':
        parts = netmask.split(".")

        first = bin(int(parts[2]))[2:]
        second = bin(int(parts[3]))[2:]

        first += (8 - len(first)) * "0"
        second += (8 - len(second)) * "0"

        netmask = first + "." + second
        zeros = netmask.count("0")
        sub_networks = 1
        addresses = 255
        if zeros > 8:
            sub_networks = math.pow(2, zeros - 8)

        if zeros < 8:
            addresses = math.pow(2, zeros)

        return [sub_networks, addresses]
    else:
        return ['-', '-']


# sweep pinging itself
def sweep_ping(start, stop):
    devices = []
    start = start.split(".")
    stop = stop.split(".")

    while 1:

        response = subprocess.call(f"ping -w 40 -n 1 {start[0]}.{start[1]}.{start[2]}.{start[3]}")
        if response == 0:
            devices.append(f"{start[0]}.{start[1]}.{start[2]}.{start[3]}")

        if int(start[3]) == 255:
            start[2] = str(int(start[2]) + 1)
            start[3] = 0
            continue

        start[3] = str(int(start[3]) + 1)

        if start[3] == stop[3] and start[2] == stop[2]:
            return devices


# organizing batches for network scan
def get_addresses(host, netmask):
    subnet_info = get_subnet_info(netmask)
    devices = []
    address = ipaddress.ip_network(f"{host}/{str(netmask)}", strict=False)
    subnet_address = str(address.network_address).split(".")
    print(subnet_address)

    if subnet_info[0] > 2:
        tmp = subnet_info[0] / 4
        with multiprocessing.Pool(processes=4) as pool:
            devices = pool.starmap(sweep_ping, [
                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{subnet_address[3]}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 1 - 1}.255"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 1}.{subnet_address[3]}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 2 - 1}.255"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 2}.{subnet_address[3]}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 3 - 1}.255"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 3}.{subnet_address[3]}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{tmp * 4 - 1}.255")])

    elif subnet_info[0] == 2:

        with multiprocessing.Pool(processes=4) as pool:
            devices = pool.starmap(sweep_ping, [
                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.0",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.128"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.128",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.255"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2] + 1}.0",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2] + 1}.128"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2] + 1}.128",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2] + 1}.255")])

    elif subnet_info[0] == 1:
        tmp = subnet_info[1] / 4

        with multiprocessing.Pool(processes=4) as pool:
            devices = pool.starmap(sweep_ping, [
                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.0",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 1}"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 1}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 2}"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 2}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 3}"),

                (f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 3}",
                 f"{subnet_address[0]}.{subnet_address[1]}.{subnet_address[2]}.{tmp * 4}")])

    devices_tmp = []

    for i in range(len(devices)):  # loop to organize finding more than one IP in batch
        if len(devices[i]) > 0:
            tmp = devices[i]
            for ii in tmp:
                devices_tmp.append(ii)
    devices = devices_tmp

    return devices


class Getter:

    def __init__(self, addrs):
        self.__addrs = addrs

    def get_addrs(self):
        return self.__addrs

    # returning interfaces data in suitable form
    def get_interfaces(self):
        interface_addresses = []

        addrs = self.get_addrs()
        for interface, addresses in addrs.items():
            interface_addresses.append([interface, addresses[1].address, addresses[1].netmask, addresses[0].address])

        return interface_addresses

    # getting MAC addresses
    def get_macs(self, devices):
        collected = []
        for i in devices:
            if len(i) > 0:
                response = subprocess.check_output("arp -a " + i)  # checking ARP for MAC address

                out = re.findall("([0-9a-f]{2}(?:-[0-9a-f]{2}){5})", str(response))  # looking for MAC in string

                if len(out) == 1:
                    api = "https://api.macvendors.com/" + out[0]  # checking API for producer
                    response = requests.get(api).text
                    if response[0] == "{":  # checking if call to API returned error
                        response = "No data"
                    collected.append([i, out[0], response])  # building final message

        return collected

    # getting host MAC address
    def get_host_mac(self, host, host_mac):

        api = "https://api.macvendors.com/" + host_mac  # checking API for producer
        response = requests.get(api).text
        if response[0] == "{":  # checking if call to API returned error
            response = "No data"

        return [host, host_mac, response]

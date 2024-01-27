import tkinter as tk
from tkinter import ttk
from tkinter import *
from getter import get_subnet_info


class Shower:

    def __init__(self, host, netmask, mac):
        self.__host = host
        self.__netmask = netmask
        self.__mac = mac

    def set_host(self, new_host):
        self.host = new_host

    def get_host(self):
        return self.host

    def set_netmask(self, new_netmask):
        self.netmask = new_netmask

    def get_netmask(self):
        return self.netmask

    def set_mac(self, new_mac):
        self.mac = new_mac

    def get_mac(self):
        return self.mac

    # displaying window with a list of network interfaces
    def show_interfaces(self, interfaces):
        main_window = tk.Tk()
        main_window.title("Sweep Pinger")

        main_window.columnconfigure(0, weight=1)
        main_window.columnconfigure(1, weight=1)
        main_window.columnconfigure(2, weight=1)
        main_window.columnconfigure(3, weight=1)
        main_window.columnconfigure(4, weight=1)

        name = ttk.Label(text="nazwa")
        address = ttk.Label(text="adres")
        netmask = ttk.Label(text="maska")
        subnets = ttk.Label(text="podsieci")

        name.grid(column=1, row=0)
        address.grid(column=2, row=0)
        netmask.grid(column=3, row=0)
        subnets.grid(column=4, row=0)

        idx = 1

        for interface in interfaces:
            subnet = get_subnet_info(str(interface[2]))

            name = ttk.Label(text=interface[0])
            address = ttk.Label(text=interface[1])
            netmask = ttk.Label(text=interface[2])
            subnets = ttk.Label(text=subnet[0])
            button = tk.Button(text=str(interface[0]), command=lambda interface=interface: [main_window.destroy(), self.set_host(interface[1]), self.set_netmask(interface[2]), self.set_mac(interface[3])])

            name.grid(column=1, row=idx)
            address.grid(column=2, row=idx)
            netmask.grid(column=3, row=idx)
            subnets.grid(column=4, row=idx)
            button.grid(column=5, row=idx)
            idx += 1

        main_window.mainloop()

    # displaying window with results of scan
    def show_end_window(self, devices):
        main_window = tk.Tk()
        main_window.title("Sweep Pinger")
        table = tk.Frame(main_window)
        table.pack(expand=True, fill="both")

        table_mac = ttk.Treeview(table)

        table_mac['columns'] = ("id", "IP", "MAC", "Producer")

        table_mac.column("#0", width=0, stretch=tk.NO)
        table_mac.column("id", anchor=tk.CENTER, width=20)
        table_mac.column("IP", anchor=tk.CENTER, width=100)
        table_mac.column("MAC", anchor=tk.CENTER, width=100)
        table_mac.column("Producer", anchor=tk.CENTER, width=100)

        table_mac.heading("#0", text="", anchor=tk.CENTER)
        table_mac.heading("id", text="id", anchor=tk.CENTER)
        table_mac.heading("IP", text="IP", anchor=tk.CENTER)
        table_mac.heading("MAC", text="MAC", anchor=tk.CENTER)
        table_mac.heading("Producer", text="Producer", anchor=tk.CENTER)

        for i in range(len(devices)):
            if len(devices[i]) > 1:
                table_mac.insert(parent="", index="end", iid=i + 1, text="",
                                 values=(i + 1, devices[i][0], devices[i][1], devices[i][2]))

        table_mac.pack(expand=True, fill="both")
        main_window.mainloop()

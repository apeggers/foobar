#!/usr/bin/python

import sys
import getopt
import os

import colorama
from colorama import Fore, Back, Style

import matplotlib.pyplot as plt
import numpy as np

"""
latency_test.py
    
Performs a series of pings to a specified server with specified packet size and
frequency. Generates a plot of ping latency using matplotlib.

Usage:  See usage_msg below or run ./latency_test.py -h.
        Requires sudo for interval <0.2s

Required parameters:
    testtime:    Length of test in seconds
    packetsize:  Size of individual packets in Bytes
    interval:    Delay between each ping in seconds. Interval <0.2s requires sudo.
    target:      IP address to ping (ipv6 not tested)

Optional paramters:
    logfile  [./default.log]: Logfile to write test results to.
    machinename ["unspecified"]: Name of machine test is running on (figure title)
    plotonly: If specified, takes -l logfile option and plots existing data

"""

def main(argv):
    usage_msg = "latency_test.py -w <testtime> -s <packetsize> -i <interval> -t <targetip> [-l <logfile>] [-m <machinename>]\n\nlatency_test.py --plotonly -l <logfile>"

    # Test conditions
    fname = "lt_default.log"
    psize = -1
    time = -1
    ip = ""
    interval = -1.
    machine = "unspecified"
    plotonly = False

    # Setting conditions from commandline args
    try:
        opts, args = getopt.getopt(argv,"hw:s:i:t:l:m:",
                ["deadline=","packetsize=","interval=","targetip=","logfile=","machine=","plotonly"])
    except getopt.GetoptError:
        print(usage_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(usage_msg)
            sys.exit()
        elif opt in ("-w", "--deadline"):
            time = int(arg)
        elif opt in ("-s", "--packetsize"):
            psize = int(arg)
        elif opt in ("-i", "--interval"):
            interval = float(arg)
        elif opt in ("-t", "--targetip"):
            ip = arg
        elif opt in ("-l", "--logfile"):
            fname = arg
        elif opt in ("-m", "--machine"):
            machine = arg
        elif opt == "plotonly":
            plotonly = True
    
    # Error Checking
    if not plotonly:
        if psize==-1 or time==-1 or interval==-1 or ip=="":
            print(Fore.RED + "Error: Required arguments not specified."+Style.RESET_ALL)
            print("Usage: "+usage_msg)
            sys.exit(2)
        
        if psize<=0:
            print(Fore.RED + "Error: packetsize must be positive, nonzero."+Style.RESET_ALL)
            sys.exit(2)
        if time<=0:
            print(Fore.RED + "Error: testtime must be positive, nonzero."+Style.RESET_ALL)
            sys.exit(2)
        if interval<=0:
            print(Fore.RED + "Error: interval must be positive, nonzero."+Style.RESET_ALL)
            sys.exit(2)
        
        if interval<0.2 and os.geteuid()!=0:
            print(Fore.RED + "Error: Root user permissions required for interval<0.2s (use sudo)"+Style.RESET_ALL)
            sys.exit(2)

        exec_flag = ''
        if os.path.exists(fname):
            print(Fore.YELLOW + "Warning: Log file already exists.")
            print(Style.RESET_ALL+ "Would you like to Overwrite the file (o) or Cancel (c)?")
            exec_flag = input()
            
            if exec_flag == 'c':
                sys.exit()
            elif exec_flag == 'o':
                os.remove(fname)
            else:
                print(Fore.RED + "Error: Invalid option entered" + Style.RESET_ALL)
                sys.exit(2)
    
        run_test(time, psize, interval, ip, fname, machine)
    
    if plotonly:
        if not os.path.exists(fname):
            print(Fore.RED + "Error: Specified logfile does not exist" + Style.RESET_ALL)
            sys.exit(2)
    
    
    plot(fname)


def run_test(time, psize, interval, ip, fname, machine):
    print(Fore.GREEN + "Running test with parameters:" + Style.RESET_ALL)
    print("\nLog file:    " + fname)
    print("Machine:     " + machine)
    print("Target IP:   " + ip)
    print("Packet Size: " + str(psize) + "B")
    print("Interval:    " + "{:.4f}".format(interval) + "s")
    print("Test Time:   " + str(time) + "s")

    header_str = "{},{},{:.4f},{},{}".format(time,psize,interval,ip,machine)
    with open(fname, "w") as f:
        f.write(header_str)
    
    cmd = "ping -w"+str(time)+" -s"+str(psize)+" -i"+"{:.4f}".format(interval)+" "+ip+" | grep icmp_seq | cut -f7 -d \" \" | cut -f2 -d \"=\" >>"+fname
    os.system(cmd)


def plot(fname):
    # File reading
    header = []
    data = []
    with open(fname, "r") as f:
        header = f.readline().split(",")
        for line in f.readlines():
            data.append(float(line))

    # Reading vars from header row
    time = int(header[0])
    psize = int(header[1])
    pps = int(1/float(header[2]))
    ip = header[3]
    machine = header[4]

    # Plot initialization
    plt.rcParams['axes.grid'] = True
    fig, ax = plt.subplots(1,1, sharey=True)

    # Plotting
    ax.plot(np.linspace(0.0,float(time), num=len(data)), data)

    # Formatting
    ax.set_xticks(np.arange(0,float(time+10),10))
    ax.set_yticks(np.arange(0,650,50))
    ax.set_xlim([0,time])
    ax.set_ylim([0,600])
    ax.set_ylabel("RTT [ms]")
    ax.set_xlabel("Approx. Elapsed Time [s]")

    # Titles
    fig.suptitle(str(psize)+"B Packets @ "+str(pps)+" Packets per Second"+
            "\nTarget: "+ip+
            "\nMachine: "+machine+
            "\nMean Latency: {:.2f} ms".format(sum(data)/len(data)))

    # Display the plot
    plt.show()


if __name__ == "__main__":
    main(sys.argv[1:])

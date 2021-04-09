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
    outputfile  [./default.log]: Logfile to write test results to.
    machinename ["unspecified"]: Name of machine test is running on (figure title)
"""

def main(argv):
    usage_msg = "latency_test.py -w <testtime> -s <packetsize> -i <interval> -t <targetip> [-o <outputfile>] [-m <machinename>]"

    # Test conditions
    fname = "lt_default.log"
    psize = -1
    time = -1
    ip = ""
    interval = -1.
    machine = "unspecified"

    # Setting conditions from commandline args
    try:
        opts, args = getopt.getopt(argv,"hw:s:i:t:o:m:",
                ["deadline=","packetsize=","interval=","targetip=","ofile=","machine="])
    except getopt.GetoptError:
        print usage_msg
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print usage_msg
            sys.exit()
        elif opt in ("-w", "--deadline"):
            time = int(arg)
        elif opt in ("-s", "--packetsize"):
            psize = int(arg)
        elif opt in ("-i", "--interval"):
            interval = float(arg)
        elif opt in ("-t", "--targetip"):
            ip = arg
        elif opt in ("-o", "--ofile"):
            fname = arg
        elif opt in ("-m", "--machine"):
            machine = arg
    
    # Error Checking
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


    if os.path.exists(fname):
        print(Fore.RED + "Error: Log file already exists.")
        print(Style.RESET_ALL)
        sys.exit(2)


    print("\nLog file:    " + fname)
    print("Machine:     " + machine)
    print("Target IP:   " + ip)
    print("Packet Size: " + str(psize) + "B")
    print("Interval:    " + "{:.4f}".format(interval) + "s")
    print("Test Time:   " + str(time) + "s")

    run_test(time, psize, interval, ip, fname)
    plot(time, psize, int(1./interval), ip, fname, machine)


def run_test(time, psize, interval, ip, fname):
    cmd = "ping -w"+str(time)+" -s"+str(psize)+" -i"+"{:.4f}".format(interval)+" "+ip+" | grep icmp_seq | cut -f7 -d \" \" | cut -f2 -d \"=\" >>"+fname
    print(Fore.GREEN + "\nRunning: "+cmd)
    print(Style.RESET_ALL)
    os.system(cmd)


def plot(time, psize, pps, ip, fname, machine):
    # File reading
    data = []
    with open(fname, "r") as f:
        for line in f.readlines():
            data.append(float(line))

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

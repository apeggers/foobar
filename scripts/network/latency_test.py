#!/usr/bin/python

import sys
import getopt
import os

import colorama
from colorama import Fore, Back, Style

import matplotlib.pyplot as plt
import numpy as np


def main(argv):
    usage_msg = "latency_test.py -w <testtime> -s <packetsize> -i <interval> -t <targetip> -o <outputfile> -m <machinename>"

    # Test conditions
    fname = ""
    psize = 300
    time = 0
    ip = ""
    interval = 1
    machine = ""

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
    print("\nLog file:    " + fname)
    print("Machine:     " + machine)
    print("Target IP:   " + ip)
    print("Packet Size: " + str(psize) + "B")
    print("Interval:    " + "{:.4f}".format(interval) + "s")
    print("Test Time:   " + str(time) + "s")

    if os.path.exists(fname):
        print(Fore.RED + "Error: Log file already exists.")
        print(Style.RESET_ALL)
        sys.exit(2)

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

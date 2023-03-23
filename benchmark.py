########################################################################################################################
# Description: script to test the performance of a system based on different metrics.
#              script is meant to be run on many different systems, and then results outputed into a file
# args: 
#   1. name of system that is being tested
#   2. path of file to store results in
########################################################################################################################

import subprocess
import re
import os
import sys

############################################################
# constants
############################################################
N_TRIES = 3
DECIMAL_PRECISION = 2
GIGA_TO_BYTES = 1000000000
MAX_PRIMES = [(10**i) * 10000 for i in range(4)]
MEMORY_SIZES = range(100, 500, 100) #size in gigabytes
FILEIO_SIZES = range(10, 30, 5) # size in gigabytes

############################################################
# functions
############################################################
def get_events_per_second(text):
    pattern = r"events per second:\s+([\d.]+)"
    match = re.search(pattern, text)

    return float(match.group(1))

def get_mib_per_seconds(text):
    pattern = r'(\d+\.\d+) MiB/sec'
    match = re.search(pattern, text)

    return float(match.group(1))

def get_throughput(text):
    start = text.find("written, MiB/s: ") + len("written, MiB/s: ")
    end = text.find("\n", start)

    return float(text[start:end].strip())

############################################################
# main
############################################################
platform = sys.argv[1]
filename = sys.argv[2]
if not os.path.exists(filename):
    #fill up titles for csv
    with open(filename, "w") as report:
        report.write("Comparison between platform performances, all tests results are averages over " + str(N_TRIES) + " iterations\n")
        for maxPrime in MAX_PRIMES:
            report.write(",CPU (max-prime = " + str(maxPrime) + ")")

        for memSize in MEMORY_SIZES:
            report.write(",Memory (total-mem-size = " + str(memSize) + "GBs)")

        for fileSize in FILEIO_SIZES:
            report.write(",FileIO (total-file-size = " + str(fileSize) + "GBs)")

with open(filename, "a") as report:
    report.write("\n" + platform)

    #cpu stats
    for maxPrime in MAX_PRIMES:
        arg = "--cpu-max-prime=" + str(maxPrime)
        values = 0
        for i in range(N_TRIES):
            result = subprocess.run(["sysbench", "--test=cpu", arg, "run"], stdout=subprocess.PIPE)
            values += get_events_per_second(result.stdout.decode('utf-8'))
        #calculate average and put in csv
        value = round(values / N_TRIES, DECIMAL_PRECISION)
        report.write("," + str(value) + " (events per second)")
    
    #memory stats
    for memSize in MEMORY_SIZES:
        arg = "--memory-total-size=" + str(memSize * GIGA_TO_BYTES)
        values = 0
        for i in range(N_TRIES):
            result = subprocess.run(["sysbench", "--test=memory", arg, "run"], stdout=subprocess.PIPE)
            values += get_mib_per_seconds(result.stdout.decode('utf-8'))
        #calculate average and put in csv
        value = round(values / N_TRIES, DECIMAL_PRECISION)
        report.write("," + str(value) + " (MiB/s)")
    
    #fileio stats
    for fileSize in FILEIO_SIZES:
        arg = "--file-total-size=" + str(fileSize * GIGA_TO_BYTES)
        values = 0
        for i in range(N_TRIES):
            result = subprocess.run(["sysbench", "--test=fileio", "--file-test-mode=seqwr", arg, "run"], stdout=subprocess.PIPE)
            os.system('rm test_file.*')
            values += get_throughput(result.stdout.decode('utf-8'))
        #calculate average and put in csv
        value = round(values / N_TRIES, DECIMAL_PRECISION)
        report.write("," + str(value) + " (MiB/s)")
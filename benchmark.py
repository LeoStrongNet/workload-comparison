import subprocess
import re
import os
import sys

def get_events_per_second(text):
    pattern = r"events per second:\s+([\d.]+)"
    match = re.search(pattern, text)

    if match:
        result = match.group(1)
        return result
    return "0"

def get_mib_per_seconds(text):
    pattern = r"([\d.]+ MiB/sec)"
    match = re.search(pattern, text)

    if match:
        result = match.group(1)
        return result
    return "0"

def get_throughput(text):
    start = text.find("written, MiB/s: ") + len("written, MiB/s: ")
    end = text.find("\n", start)

    return text[start:end].strip()

#cpu usage
report = "CPU usage:\n"
for i in range(4):
    v = str((10**i)*10000)
    maxPrime = "--cpu-max-prime=" + v
    result = subprocess.run(["sysbench", "--test=cpu", maxPrime, "run"], stdout=subprocess.PIPE)
    value = result.stdout.decode('utf-8')
    report += "\tmax-prime: " + v + " -> events per second: " + get_events_per_second(value) + "\n" 
report += "\n"   

#ram usage 
report += "Memory usage:\n"
for i in range(1, 5):
    gigabytes = i * 100
    v = str(gigabytes * 1000000000)
    totalSize = "--memory-total-size=" + v
    result = subprocess.run(["sysbench", "--test=memory", totalSize, "run"], stdout=subprocess.PIPE)
    value = result.stdout.decode('utf-8')
    report += "\ttotal size: " +  str(gigabytes) + "G -> MiB per seconds: " + get_mib_per_seconds(value) + "\n"
report += "\n"

#io latency
report += "FileIO usage:\n"
for i in range(1, 5):
    v = str(i * 10)
    totalSize = "--file-total-size=" + v
    result = subprocess.run(["sysbench", "--test=fileio", "--file-test-mode=seqwr", "run"], stdout=subprocess.PIPE)
    
    #remove all the test files
    os.system("rm test_file.*")
    value = result.stdout.decode('utf-8')
    report += "\ttotal size: " + v + "G -> throughput (MiB/s): " + get_throughput(value) + "\n"

filename = sys.argv[1] + ".txt"
with open(filename, "w") as file:
    file.write(report)
print(report)
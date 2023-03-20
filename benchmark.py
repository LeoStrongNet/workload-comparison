import subprocess
import re
import os

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
result = subprocess.run(["sysbench", "--test=memory", "run"], stdout=subprocess.PIPE)
value = result.stdout.decode('utf-8')
report += "\tMiB per seconds: " + get_mib_per_seconds(value) + "\n"
report += "\n"

#io latency
report += "FileIO usage:\n"
result = subprocess.run(["sysbench", "--test=fileio", "--file-test-mode=seqwr", "run"], stdout=subprocess.PIPE)
value = result.stdout.decode('utf-8')
report += "\tThroughput (MiB/s): " + get_throughput(value) + "\n"

#remove all the test files
os.system("rm test_file.*")

print(report)
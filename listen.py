#!/usr/bin/python
import os
import signal
import subprocess
import sys
import time
import paho.mqtt.client as mqtt

mqttc = mqtt.Client()

# Ignore SIGCHLD
# This will prevent zombies
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

# The token to look for in tcpdump's output
# This should be your unique network SSID
# SSID_TOKEN = sys.argv[1] if len(sys.argv) > 1 else 'Free Public Wifi'

# This file holds a list of SSID's to look for in tcpdump's output
# Each SSID is delineated by a new line
# White space at the beginning and end of each line is stripped out before processing
f = open("dash_ssids")
lines = f.readlines()
f.close()

SSID_TOKENS = []
for line in lines:
    SSID_TOKENS.append(line.strip())

print "Number of tokens in list:"
print len(SSID_TOKENS)


times = {}
print "SSID_TOKENS is/are:"
for SSID_TOKEN_PRINT in SSID_TOKENS:
    print SSID_TOKEN_PRINT
    times[SSID_TOKEN_PRINT] = time.time()
    
cmd = 'tcpdump -l -K -q -i Butts -n -s 256'
proc = subprocess.Popen(cmd.split(), close_fds=True,
                        bufsize=0, stdout=subprocess.PIPE)

mqttc.connect("192.168.1.3")
mqttc.loop_start()

while True:
    line = proc.stdout.readline()
    if not line:
        print "tcpdump exited"
        break
    for SSID_TOKEN in SSID_TOKENS:
        if SSID_TOKEN in line:
            sys.stdout.write(line)
            sys.stdout.flush()
            if time.time() - times[SSID_TOKEN] > 1.0:
       	        mqttc.publish("/dash/" + SSID_TOKEN, "pressed")
                times[SSID_TOKEN] = time.time()

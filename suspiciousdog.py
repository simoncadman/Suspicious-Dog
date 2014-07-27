#! /bin/sh
"true" '''\'
if command -v python2 > /dev/null; then
  exec python2 "$0" "$@"
else
  exec python "$0" "$@"
fi
exit $?
'''

import socket
import sys
import re
import time
import sqlite3
import subprocess
dbconn = sqlite3.connect('log.db')
c = dbconn.cursor()

# create table if not exists
try:
    c.execute('''CREATE TABLE addresses
             (hostname text, ip text, mac text, timestamp date, investigated bool)''')
    dbconn.commit()
except sqlite3.OperationalError:
    pass

arpregex = re.compile("(.*) \(((?:\d{1,3}\.){3}\d{1,3})\) at ((?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}) \[ether\]  on ")

HOST = '0.0.0.0'
PORT = 60000
ROUTERIP = "192.168.1.1"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
while True:
    # collect data
    conn, addr = s.accept()
    arpdata = ""
    timestamp = time.time()
    while 1:
        data = conn.recv(1024)
        # only store data if from correct ip
        if addr[0] == ROUTERIP:
            arpdata += data
        if not data: break
    conn.close()
    
    # only process data if from correct ip
    if addr[0] == ROUTERIP:
        # loop over lines in data
        for line in arpdata.splitlines():
            # if line valid arp line
            results = arpregex.match(line)
            if results != None:
                # matches expected format
                hostname = results.groups(0)[0]
                ipaddr = results.groups(0)[1]
                macaddr = results.groups(0)[2]
                
                c.execute('SELECT * FROM addresses WHERE mac=?', (macaddr,))
                result = c.fetchone()
                if result == None:
                    print "New mac address seen:", hostname, ipaddr, macaddr
                    if len(sys.argv) == 2:
                        subprocess.call([sys.argv[1], 'New mac address detected', " ".join( [ hostname, ipaddr, macaddr ] )])
                    c.execute("INSERT INTO addresses VALUES (?,?,?,?,0)", ( hostname, ipaddr, macaddr, timestamp ))
                    dbconn.commit()

dbconn.close()
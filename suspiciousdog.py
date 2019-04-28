#! /usr/bin/env python3

import sys
import re
import time
import json
import sqlite3
import subprocess
import boto3
SNS_ARN = "arn:aws:sns:us-east-1:294819063748:niftyalert"
SNS_REGION = 'us-east-1'

dbconn = sqlite3.connect('log.db')
c = dbconn.cursor()
client = boto3.client('sns', region_name=SNS_REGION)

# create table if not exists
try:
    c.execute('''CREATE TABLE addresses
             (hostname text, ip text, mac text, timestamp date, investigated bool)''')
    dbconn.commit()
except sqlite3.OperationalError:
    pass

arpregex = re.compile("(.*) \(((?:\d{1,3}\.){3}\d{1,3})\) at ((?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}) \[ether\] on ")

while True:
    # collect data
    arpdata = subprocess.check_output(['arp', '-a'])
    timestamp = time.time()
    
    # loop over lines in data
    for line in arpdata.splitlines():
        # if line valid arp line
        results = arpregex.match(line.decode('utf-8'))
        if results != None:
            # matches expected format
            hostname = results.groups(0)[0]
            ipaddr = results.groups(0)[1]
            macaddr = results.groups(0)[2]
            
            c.execute('SELECT * FROM addresses WHERE mac=?', (macaddr,))
            result = c.fetchone()
            if result == None:
                try:
                    print('New mac address detected: %s' % ( " ".join( [ hostname, ipaddr, macaddr ] )), flush=True)
                    response = client.publish(
                        TopicArn=SNS_ARN,
                        Message=" - ".join( [ hostname, ipaddr, macaddr ] ),
                        Subject=('New mac address detected - ' + hostname + ' - ' + ipaddr)[0:100],
                    )
                    c.execute("INSERT INTO addresses VALUES (?,?,?,?,0)", ( hostname, ipaddr, macaddr, timestamp ))
                    dbconn.commit()
                    print('Logged', flush=True)
                except Exception as e:
                    print(e, flush=True)
                    pass
            else:
                # update last time seen
                c.execute("update addresses set timestamp = ? where mac = ?", ( timestamp, macaddr ))
                dbconn.commit()
        else:
            print("Unable to parse: %s" % ( line.decode('utf-8'), ), flush=True)
    time.sleep(5)

dbconn.close()

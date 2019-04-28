#! /usr/bin/env python3

import sqlite3
import datetime

dbconn = sqlite3.connect('log.db')
c = dbconn.cursor()

now = datetime.datetime.now()
then = now - datetime.timedelta(days=7)
timestamp = then.strftime('%s')
c.execute("delete from addresses where timestamp <= ?", (timestamp,) )
dbconn.commit()

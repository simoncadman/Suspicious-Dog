#! /bin/sh
"true" '''\'
if command -v python2 > /dev/null; then
  exec python2 "$0" "$@"
else
  exec python "$0" "$@"
fi
exit $?
'''

import sqlite3
import datetime

dbconn = sqlite3.connect('log.db')
c = dbconn.cursor()

now = datetime.datetime.now()
then = now - datetime.timedelta(days=14)
timestamp = then.strftime('%s')

c.execute("delete from addresses where timestamp <= ?", ( timestamp ))
dbconn.commit()

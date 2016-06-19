Suspicious-Dog
==============

Logs and investigates new MAC addresses seen on LAN

Set this cron up on router:

* * * * * root arp -a  | nc niftylogger:60000

#!/bin/bash
echo "Stopping MyPapers Server ..."
PIDs=`ps -ef|grep web.py|grep -v grep|awk '{print $2}'`
for PID in $PIDs
do
   echo "Kill a process: $PID"
   kill -9 $PID
   sleep 1
done
echo "Done."

# OpenTap Startup Script
# Authors: Christian Macias and Michael P. McGarry
# Description: This script launches OpenTap (the Web Server and the Garbage collector)
#

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

cd /opt/opentap/bin

printf "Starting OpenTap\n"

#See if the garbage collector is already running and kill it
IDs=$(ps -aux | grep opentapGarbage | grep -v grep | awk '{ print $2 }')
if ! [ -z $IDs ]; then
		kill $IDs
fi

# Launch the Garbage collector
printf "Starting OpenTap's Garbage Collector (check log directory for output)\n"
bash opentapGarbageCollector.sh &> /opt/opentap/log/garbageCollector.log &

IDs=$(ps -aux | grep opentapGarbage | grep -v grep | awk '{ print $2 }')
if [ -z $IDs ]; then
	printf "Error while starting Garbage Collector\n\n"
fi

# Launch the Python OpenTap web server
printf "Starting the OpenTap Web Server (check log directory for output)\n"
#Start web server
serverAddress=$(cat /etc/opentap/opentap.conf | grep "websrv-addr:")
serverAddress=${serverAddress//"websrv-addr: "}
python opentapWebServer.py $serverAddress &> /opt/opentap/log/webserver.log &

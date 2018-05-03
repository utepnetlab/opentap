# OpenTap Shutdown Script
# Authors: Christian Macias and Michael P. McGarry
# Description: This script shuts down OpenTap (the Web Server and the Garbage collector)
#

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

printf "Shutting down OpenTap\n"

# See if the garbage collector is running and kill it
IDs=$(ps -aux | grep opentapGarbage | grep -v grep | awk '{ print $2 }')
if ! [ -z $IDs ]; then
		kill $IDs
fi

# See if the web server is running and kill it
IDs=$(ps -aux | grep opentapWeb | grep -v grep | awk '{ print $2 }')
if ! [ -z $IDs ]; then
		kill $IDs
fi


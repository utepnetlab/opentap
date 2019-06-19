# OpenTap Garbage Collector
# Authors: Christian Macias and Michael P. McGarry
# Description: This script periodically checks for data files that were last accessed
#  greater than the retention period in the past; if so the file is deleted
#
#   Do not rename this file and do not execute directly; use start_opentap.sh

retention=$(cat /etc/opentap/opentap.conf | grep "retention:")
retention=${retention//"retention:"}
retention=${retention//" "}

echo "The OpenTap Garbage Collector will delete all data older than "$retention" minutes"
echo "Below is a list of files that have been deleted:"
cd /opt/opentap/log

# Wake up every 5 minutes and delete data (in CSV files) that is older than the retention period
while true;
do
	# delete CSV files that older than the retention period
	find ./ -name "*.csv" -type f -amin +$retention -delete -print
	# delete files left around by NFDUMP
	find ./ -name "nfcapd.*" -type f -amin +$retention -delete -print
	sleep 300s
done

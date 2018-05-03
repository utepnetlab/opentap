# OpenTap uninstall
#
error=0
OS="/"unknown/""

# must be run as root
if [ $EUID -ne 0 ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# remove OpenTap directories
rm -rf /opt/opentap > /dev/null 2>/dev/null
rm -rf /etc/opentap > /dev/null 2>/dev/null
rm -rf /var/www/opentap > /dev/null 2>/dev/null

#-------------------DONE----------
echo ""
echo "OpenTap has been successfully uninstalled."
echo "Sorry to see you go!"	


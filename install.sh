# OpenTap install
error=0
OS="/"unknown/""

# must be run as root
if [ $EUID -ne 0 ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# create OpenTap directories
mkdir /opt/opentap > /dev/null 2>/dev/null
mkdir /opt/opentap/log > /dev/null 2>/dev/null
mkdir /opt/opentap/bin > /dev/null 2>/dev/null
mkdir /opt/opentap/dependencies > /dev/null 2>/dev/null
mkdir /etc/opentap > /dev/null 2>/dev/null
mkdir /var/www/opentap > /dev/null 2>/dev/null

# execute script that will interview the user to setup the opentap.conf file
python2 etc/opentap/buildConfig.py && cp -r -f ./etc/opentap/opentap.conf /etc/opentap

# copy over OpenTap files
cp -r -f ./web/* /var/www/opentap/
cp -r -f ./bin/* /opt/opentap/bin/
cp -r -f ./dependencies/* /opt/opentap/dependencies/

# setup execute permissions for start/stop scripts
chmod 775 /opt/opentap/bin/start_opentap.sh
chmod 775 /opt/opentap/bin/stop_opentap.sh

# setup execute permissions for web scripts
chmod 755 /var/www/opentap/capture
chmod 755 /var/www/opentap/capture/*
chmod 755 /var/www/opentap/retrieve


#-------set no password execution permission----------------
grep -q "nobody ALL=(root) NOPASSWD:/opt/opentap/dependencies/netflowcap*" /etc/sudoers
ret=$?
if [ $ret -ne 0 ]; then
	sudo sh -c "echo \"nobody ALL=(root) NOPASSWD:/opt/opentap/dependencies/netflowcap*\" >> /etc/sudoers"	
fi

# allow webserver access to read/create files
chmod 775 /opt/opentap/log


#-------------------DONE----------
echo ""
echo "OpenTap has been successfully installed!"
echo "To start OpenTap, run \"sudo bash /opt/opentap/bin/start_opentap.sh\""
echo "The webserver, by default, will run on 127.0.0.1:80 and listen for traffic on all interfaces"
echo "To change the configuration, edit /etc/opentap/opentap.conf"	


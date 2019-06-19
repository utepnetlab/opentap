#!/bin/bash
#
# OpenTap install script
#
error=0

# must be run as root
if ! [ $(id -u) = 0 ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Determine Linux distribution
RedHat=$(cat /proc/version | grep -c Red)
Ubuntu=$(cat /proc/version | grep -c Ubuntu)
Debian=$(cat /proc/version | grep -c Debian)
OS="/"unknown/""
installCmd="apt-get"
if [ $RedHat -ge 1 ]; then
	OS="RedHat"
	echo "Installing on a Red Hat distribution"
	installCmd="yum"
fi
if [ $Ubuntu -ge 1 ]; then
	OS="Ubuntu"
	echo "Installing on an Ubuntu distribution"
	installCmd="apt-get"
fi
if [ $Debian -ge 1 ]; then
	OS="Debian"
	echo "Installing on a Debian distribution"
	installCmd="apt-get"
fi


# Check for ifconfig
if ! [ -x "$(command -v ifconfig)" ]; then
	echo "Error: The ifconfig utility is required to poll for network interfaces, please install it before proceeding; it is part of a package called net-tools" 1>&2
	echo "Would you like to have net-tools installed by this script (y/N)?"
	read resp
	if [ $resp = "Y" ] || [ $resp = "y" ]; then
		$installCmd install net-tools
	else
		exit 1
	fi
fi

# Check for tcpdump
if ! [ -x "$(command -v tcpdump)" ]; then
	echo "Error: The tcpdump utility is required to collect data from network interfaces, please install it before proceeding" 1>&2
	echo "Would you like to have tcpdump installed by this script (y/N)?"
	read resp
	if [ $resp = "Y" ] || [ $resp = "y" ]; then
		$installCmd install tcpdump
	else
		exit 1
	fi
fi

# Check for Python 3
if ! [ -x "$(command -v python3)" ]; then
   echo "Error: OpenTap depends on Python 3 (including pip3), please install it before proceeding; it is best for you to install it on your own" 1>&2
   exit 1
fi

install_phidgets=0
no_pip3=0
echo "Do you want to use OpenTap with Phidgets sensors (Y/n)?"
read resp
if [ -z $resp ] || [ $resp = "Y" ] || [ $resp = "y" ]; then
	install_phidgets=1
fi

if [ $install_phidgets -eq 1 ]; then

	# if OS is Ubuntu, install libusb as it will be detected but not installed correctly for Phidgets, this resolves that issue
	if [ $OS = "RedHat" ]; then
		echo "Installing libusb-devel"
		sudo yum install libusb-devel
	fi
	if [ $OS = "Ubuntu" ]; then
		echo "Installing libusb-1.0-0-dev"
		sudo apt-get install libusb-1.0-0-dev
	fi
	if [ $OS = "Debian" ]; then
		echo "Installing libusb-1.0-0-dev"
		sudo apt-get install libusb-1.0-0-dev
	fi

	phidgets=1
	# Check for libusb
	if [ -z "$(ldconfig -p | grep libusb)" ]; then
   		phidgets=0
	fi

	# Check for libphidgets
	if [ -z "$(ldconfig -p | grep libphidget22)" ]; then
		if ! [ -f /usr/lib/libphidget22.so ]; then
	   		phidgets=0
		fi
	fi

	origDir=$(pwd)
	if [ $phidgets -eq 0 ]; then
		echo "The Phidgets driver is not installed. This driver is required to support collecting Phidgets sensor data."
		echo "Would you like to have the Phidgets driver installed by this script (Y/n)?"
		read resp
		if [ -z $resp ] || [ $resp = "Y" ] || [ $resp = "y" ]; then
			$installCmd install libusb
			# Be sure libusb was successfully installed before installing Phidgets driver
			if [ -z "$(ldconfig -p | grep libusb)" ]; then
   				echo "Error: OpenTap's sensor features require the libusb driver, install it and then re-install OpenTap" 1>&2
   				phidgets=0
			else
				wget https://www.phidgets.com/downloads/phidget22/libraries/linux/libphidget22.tar.gz
				tar -zxvf libphidget22.tar.gz
				directory="$(ls | grep libphidget22-)"
				cd $directory
				./configure --prefix=/usr && make && sudo make install
				cd $origDir
				if ! [ -x "$(command -v pip3)" ]; then
		  			echo 'Error: pip3 is not installed' >&2
					echo "Would you like to have pip3 installed by this script (Y/n)?"
					read resp
					if [ -z $resp ] || [ $resp = "Y" ] || [ $resp = "y" ]; then
		  				$installCmd install python3-pip
		  			else
						phidgets=0
						no_pip3=1
		  			fi
		  		else
					pip3 install Phidget22
					phidgets=1
				fi
			fi
		fi
	fi
	cd $origDir

	# Phidgets driver might be installed but the Phidget22 Python module is not, check for that
	python3 -c "import Phidget22"
	if [ $? -ne 0 ]; then
		echo "The Phidgets Python module is required for OpenTap sensor support, it is not installed."
		echo "Would you like to have it installed by this script? (Y/n)?"
		read resp
		if [ -z $resp ] || [ $resp = "Y" ] || [ $resp = "y" ]; then
			if ! [ -x "$(command -v pip3)" ]; then
				echo 'Error: pip3 is not installed' >&2
				echo "Would you like to have pip3 installed by this script (Y/n)?"
				read resp
				if [ -z $resp ] || [ $resp = "Y" ] || [ $resp = "y" ]; then
		  			$installCmd install python3-pip
					pip3 install Phidget22
					phidgets=1
				else
					phidgets=0
		  		fi
			else
				pip3 install Phidget22
				phidgets=1
			fi
		else
			phidgets=0
		fi
	fi

	python3 -c "import Phidget22"
	if [ $? -ne 0 ]; then
		echo "The Phidgets Python module is still not installed; not sure why. Resolve it and re-install OpenTap if you want to use Phidgets devices."
		phidgets=0
	fi
fi

if ! [ -x "$(command -v pip3)" ]; then
	echo 'Error: pip3 is not installed' >&2
	echo "Would you like to have pip3 installed by this script (Y/n)?"
	read resp
	if [ -z $resp ] || [ $resp = "Y" ] || [ $resp = "y" ]; then
		$installCmd install python3-pip
	else
		no_pip3=1
	fi
fi

if [ $no_pip3 -eq 1 ]; then
	echo "You will need to manually install the pandas, flask, and requests modules for Python3"
else
	# Install PANDAS, Flask, and requests
	pip3 install pandas flask requests
fi

#
# create OpenTap directories
#
if ! [ -d /opt ]; then
   mkdir /opt
fi
mkdir /opt/opentap > /dev/null 2>/dev/null
mkdir /opt/opentap/log > /dev/null 2>/dev/null
mkdir /opt/opentap/bin > /dev/null 2>/dev/null
mkdir /opt/opentap/dependencies > /dev/null 2>/dev/null
mkdir /etc/opentap > /dev/null 2>/dev/null

# copy over OpenTap files
cp -r -f ./bin/* /opt/opentap/bin/
cp -r -f ./dependencies/* /opt/opentap/dependencies/

# setup execute permissions for start/stop scripts
chmod 775 /opt/opentap/bin/start_opentap.sh
chmod 775 /opt/opentap/bin/stop_opentap.sh

# execute script that will interview the user to setup the opentap.conf file
python3 etc/opentap/buildConfig.py && cp -r -f ./etc/opentap/opentap.conf /etc/opentap
if [ $? = 1 ]; then
   exit 1
fi


#-------set no password execution permission----------------
grep -q "nobody ALL=(root) NOPASSWD:/opt/opentap/dependencies/netflowcap*" /etc/sudoers
ret=$?
if [ $ret -ne 0 ]; then
	sudo sh -c "echo \"nobody ALL=(root) NOPASSWD:/opt/opentap/dependencies/netflowcap*\" >> /etc/sudoers"	
fi

# allow webserver access to read/create files
chmod 775 /opt/opentap/log

if [ $install_phidgets -eq 1 ]; then

	#
	# Launch the Python script to detect attached Phidgets Sensors
	#
	if [ $phidgets -ne 0 ]; then
		python3 opentapSensorDetect.py
		if [ $? -ne 0 ]; then
	   	exit 1
		fi
	fi
fi

#
# If not using Phidgets sensors, use no sensor version of OpenTap web server
#
if [ $install_phidgets -eq 0 ]; then
	rm /opt/opentap/bin/opentapWebServer.py
	rm /opt/opentap/bin/sensor.py
	mv /opt/opentap/bin/opentapWebServer_nosensor.py /opt/opentap/bin/opentapWebServer.py
fi

#-------------------DONE----------
echo ""
echo ""
echo ""
echo "OpenTap has been successfully installed!"
if [ $install_phidgets -eq 1 ]; then
	if [ $phidgets -eq 0 ]; then
		echo "However, Phidget sensor support will not work! The Phidget driver must be installed and OpenTap re-installed."
	fi
fi
echo ""
webServAddr=$(cat /etc/opentap/opentap.conf | grep "websrv-addr:")
webServAddr=${webServAddr//"websrv-addr:"}
webServAddr=${webServAddr//" "}
addrPieces=(${webServAddr//:/ })
servIPAddr=${addrPieces[0]}
servPort=${addrPieces[1]}
devName=$(cat /etc/opentap/opentap.conf | grep "name:")
devName=${devName//"name:"}
devName=${devName//" "}

echo "The OpenTap REST API will be hosted on "$webServAddr", as you have configured"
echo "To change the configuration, edit /etc/opentap/opentap.conf"
echo ""
echo "Add "$devName" = {'name': '"$devName"', 'ipaddr': '"$servIPAddr"', 'portnum': '"$servPort"' } to opentap.py to create a reference to this device"
echo ""
echo "To start OpenTap, run \"sudo bash /opt/opentap/bin/start_opentap.sh\""
echo ""

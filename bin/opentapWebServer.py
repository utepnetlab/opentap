# OpenTap Python web server
# Authors: Christian Macias
# Description: This Python script is the OpenTp web server (uses CGI)
#

import sys
import os

host = ''
port = 80
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if ':' in arg:
        host, port = arg.split(':')
        port = int(port)
    else:
        try:
            port = int(sys.argv[1])
        except:
            host = sys.argv[1]

server_address = (host, port)

#Version Check
req_version = (2,9)
cur_version = sys.version_info

if cur_version >= req_version:
	import http.server as httpSrv
	os.chdir("/var/www/opentap")

	CGIHandler = httpSrv.CGIHTTPRequestHandler
	CGIHandler.cgi_directories.append('/')
	CGIHandler.cgi_directories.append('/capture')
	CGIHandler.cgi_directories.append('/html')
	print(CGIHandler.cgi_directories)
	CGIHttpd = httpSrv.HTTPServer(server_address, CGIHandler) #http server deameon

	CGIHttpd.serve_forever()
else:
	import CGIHTTPServer
	import BaseHTTPServer
	os.chdir("/var/www/opentap")

	CGIHandler = CGIHTTPServer.CGIHTTPRequestHandler
	CGIHandler.cgi_directories.append('/')
	CGIHandler.cgi_directories.append('/capture')
	CGIHandler.cgi_directories.append('/html')
	print(CGIHandler.cgi_directories)
	CGIHttpd = BaseHTTPServer.HTTPServer(server_address, CGIHandler) #http server deameon

	CGIHttpd.serve_forever()

"""
OpenTap API

An API for interfacing with OpenTap

Author:  Christian Macias and Michael P. McGarry
Version: 0.1
Date:    February 15, 2018

"""
import pandas as pd
import requests
import json
import io

# path to CSV files containing IP address data (AS data, geo data), UPDATE FOR YOUR SYSTEM
csvpath = './'

# IP addresses for REST API of various OpenTap locations
LOCAL = { 'name': 'local', 'ipaddr': '127.0.0.1', 'portnum': '2020' }

#
# Function: capture
#
def capabilities(location=LOCAL):
    """
    Query an OpenTap device for its capabilities
    Input:  location - location dictionary for OpenTap device (default=LOCAL)
    Output: Capabilities data structure (a dictionary)
    """
    # Setup the REST API URL string
    #
    apiString = 'http://' + location['ipaddr'] + ':' + str(location['portnum']) + '/capabilities'

    # Make the REST API Request
    resp = requests.get(apiString)
    content_type = resp.headers['Content-Type']
    
    if content_type == 'application/json':
        return json.loads(resp.text)
    else:
        print("Unexpected response from OpenTap device:")
        print(resp.text)
        return {}


#
# Function: capture
#
def capture(datatype,startTime,stopTime,captureID='auto',observationPt='',period=None,location=LOCAL):
    """
    Start an OpenTap data capture
    Input:  Data type: ethernet, netflow, sensor
            Capture Start and Stop Time in UTC UNIX seconds  
            Capture ID (or filename)
            and optionally IP address (ip) and Port number (port) for REST API
    Output: Measurement Task ID
    """
    if captureID == 'auto':
        captureID = datatype + '_' + observationPt + '_' + str(startTime) + '_' + str(stopTime)
    
    # Setup the REST API URL string
    #
    if observationPt == '':
        apiString = 'http://' + location['ipaddr'] + ':' + str(location['portnum']) + '/capture/' + datatype + '?id=' + str(captureID) + '&start=' + str(startTime) + '&stop=' + str(stopTime)
    else:
        apiString = 'http://' + location['ipaddr'] + ':' + str(location['portnum']) + '/capture/' + datatype + '?id=' + str(captureID) + '&start=' + str(startTime) + '&stop=' + str(stopTime) + '&observationPt=' + observationPt

    # append the period argument if it is present
    if period != None:
        apiString = apiString + '&period=' + str(period)

    # Make the REST API Request
    resp = requests.get(apiString)
    content_type = resp.headers['Content-Type']
    
    if content_type == 'application/json':
        respData = json.loads(resp.text)
        if respData['status'] == 'error':
            print("OpenTap Capture Error: " + respData['msg'])
        elif respData['status'] == 'success':
            print("OpenTap Capture Success: " + respData['msg'])
            captureID = respData['id']
    else:
        print("Unexpected response from OpenTap device:")
        print(resp.text)
        captureID = ''

    # Retrieve and return the measurement task ID
    return captureID
    
#
# Function: retrieve
#
def retrieve(capturetype,captureID,location=LOCAL):
    """
    Retrieve data from an OpenTap device
    Input:  Capture type: packet, netflow, temp
            Capture ID (or filename)
            and optionally IP address (ip) and Port number (port) for REST API
    Output: PANDAS DataFrame containing retrieved data
    """
    # Setup the REST API URL string
    #
    apiString = 'http://' + location['ipaddr'] + ':' + str(location['portnum']) + '/retrieve?id=' + captureID

    # Make the REST API Request
    resp = requests.get(apiString)
    status_code = resp.status_code
    content_type = resp.headers['Content-Type']
    
    #print('Content type = ' + content_type)
    #print("RESP: " + resp.text)
    
    if status_code == 200:
        # Received a positive response
        if resp.text.count('\n') < 2:
            print("RESP: " + resp.text)
            # Return a NULL PANDAS data frame
            return pd.DataFrame()
        if content_type == 'text/csv':
            csvFile = io.StringIO(resp.text)
            if capturetype == 'netflow':
                netflowData = pd.read_csv(csvFile)
                if set(['ts', 'te', 'td', 'sa', 'da', 'sp', 'dp', 'pr', 'ipkt', 'ibyt']).issubset(netflowData.columns):
                    # Netflow data is in NFDUMP format, convert it
                    netflowData = nfdumpToNetflow(netflowData)
                return netflowData
            elif capturetype == 'sensor':
                sensorData = pd.read_csv(csvFile)
                sensorData['time'] = pd.to_datetime(sensorData['time'], unit='ms', utc=True)
                return sensorData
            elif capturetype == 'ethernet':
                ethernetData = pd.read_csv(csvFile)
                ethernetData['time'] = pd.to_datetime(ethernetData['time'], unit='ms', utc=True)
                return ethernetData
            else:
                print("Unsupported data type: " + capturetype)
                return pd.DataFrame()
        elif content_type == 'application/json':
            # Server did not return a CSV file, it is sending a message in JSON
            respData = json.loads(resp.text)
            print('OpenTap Retrieve ' + respData['status'] + ': ' + respData['msg'])
            # Return a NULL PANDAS data frame
            return pd.DataFrame()
        else:
            print("Unexpected response from OpenTap device:")
            print(resp.text)
            # Return a NULL PANDAS data frame
            return pd.DataFrame()
    else:
        print("Errored HTTP response from OpenTap device: " + str(status_code))
        # Error from server, return a NULL PANDAS data frame
        return pd.DataFrame()

#
# Function: nfdumpToNetflow
#
def nfdumpToNetflow(nfdumpData):
    """
    Convert Netflow records in NFDUMP CSV file format to our Netflow v5 format
    Input:  PANDAS data frame containing NetFlow records in NFDUMP format
    Output: PANDAS data frame containing NetFlow records in our format
    """
    # Removes the Summary data from the last 3 rows:
    nfdumpData = nfdumpData[:(len(nfdumpData.index)-3)]

    # Keep only the columns of interest:
    nfdumpData = nfdumpData[['ts', 'te', 'td', 'sa', 'da', 'sp', 'dp', 'pr', 'ipkt', 'ibyt']]

    # Rename these columns:
    nfdumpData.columns = ['first','last','duration','srcaddr','dstaddr','srcport','dstport','prot','dPkts','dOctets']
    
    # Make sure the column types are correct:
    nfdumpData['first'] = nfdumpData['first'].astype(str)
    nfdumpData['last'] = nfdumpData['last'].astype(str)
    nfdumpData['first'] = pd.to_datetime(nfdumpData['first'])
    nfdumpData['last'] = pd.to_datetime(nfdumpData['last'])
    nfdumpData['duration'] = nfdumpData['duration'].astype(float) * 1000
    nfdumpData['duration'] = nfdumpData['duration'].astype(int)
    nfdumpData['srcaddr'] = nfdumpData['srcaddr'].astype(str)
    nfdumpData['dstaddr'] = nfdumpData['dstaddr'].astype(str)
    nfdumpData['srcport'] = nfdumpData['srcport'].astype(int)
    nfdumpData['dstport'] = nfdumpData['dstport'].astype(int)
    nfdumpData['prot'] = nfdumpData['prot'].astype(str)
    nfdumpData['dPkts'] = nfdumpData['dPkts'].astype(int)
    nfdumpData['dOctets'] = nfdumpData['dOctets'].astype(int)

    return nfdumpData


#
# Function: netflowAddApplication
#
def netflowAddApplication(netflowData):
    """
    Adds application data to Netflow records
    Input:  Netflow records as a PANDAS data frame
    Output: Netflow records (with application data) as a PANDAS data frame
    """
    netflowData = netflowConvertProtoStr2Num(netflowData)
    for lab, row in netflowData.iterrows():
        # Look up application data
        srcApp = appLookup(row['srcport'],row['prot'])
        dstApp = appLookup(row['dstport'],row['prot'])
        # Determine the definitve application considering the lookups on both source and destination port number
        if dstApp == "unknown":
            netflowData.loc[lab, 'app'] = srcApp
        else:
            # Maybe select the application that is most popular? (A crude way to do that is to select the smaller port number)
            if netflowData.loc[lab, 'srcport'] < netflowData.loc[lab, 'dstport']:
                netflowData.loc[lab, 'app'] = srcApp
            else:
                netflowData.loc[lab, 'app'] = dstApp

    netflowData = netflowConvertProtoNum2Str(netflowData)
    return netflowData


#
# Function: appLookup
#
def appLookup(port,prot):
    """
    Lookup application name using port number and IP protocol number
    Input:  Port number and IP protocol number
    Output: Application name (string)
    """
    if not 'portnum' in globals():
        try:
            global portnum
            portnum = pd.read_csv(csvpath+'portnum.csv')
            print('Loading IANA port number data for the first time')
        except OSError:
            del portnum
            print('portnum CSV file not found')
    if not 'portnum' in globals():
        return 'no lookup data'
    else:
        portnumVal = portnum[(portnum['portnum'] == port) & (portnum['prot'] == prot)]
        if not portnumVal.empty :
            portnumVal = portnumVal.iloc[0]     # only look at the first row in the data frame
            if portnumVal['name'] != "" :
                # add the application name
                return portnumVal['name']
            else :
                # try a match to an application that is not associated with any IP protocol
                portnumVal = portnum[(portnum['portnum'] == port) & (portnum['prot'] == 255)]
                if not portnumVal.empty :
                    portnumVal = portnumVal.iloc[0]     # only look at the first row in the data frame
                    if portnumVal['name'] != "" :
                        # add the application name
                        return portnumVal['name']
                    else :
                        # add the application name "unknown"
                        return 'unknown'
                else :
                    # add the application name "unknown"
                    return 'unknown'
        else :
            # try a match to an application that is not associated with any IP protocol
            portnumVal = portnum[(portnum['portnum'] == port) & (portnum['prot'] == 255)]
            if not portnumVal.empty :
                portnumVal = portnumVal.iloc[0]     # only look at the first row in the data frame
                if portnumVal['name'] != "" :
                    # add the application name
                    return portnumVal['name']
                else :
                    # add the application name "unknown"
                    return 'unknown'
            else :
                # add the application name "unknown"
                return 'unknown'
    return 'unkown'
    
#
# Function: netflowConvertProtoStr2Num
#
def netflowConvertProtoStr2Num(netflowData):
    """
    Convert IP protocol field (prot) of Netflow records from a string to a number
    Input:  Netflow records as a PANDAS data frame
    Output: Netflow records as a PANDAS data frame with prot field converted
    """
    for lab, row in netflowData.iterrows():
        try:
            netflowData.loc[lab, 'prot'] = protoData.index(row['prot'].upper())
        except ValueError:
            if row['prot'].isdigit():
                netflowData.loc[lab, 'prot'] = int(row['prot'])
            else:
                netflowData.loc[lab, 'prot'] = 0
    return netflowData

#
# Function: netflowConvertProtoNum2Str
#
def netflowConvertProtoNum2Str(netflowData):
    """
    Convert IP protocol field (prot) of Netflow records from a number to a string
    Input:  Netflow records as a PANDAS data frame
    Output: Netflow records as a PANDAS data frame with prot field converted
    """
    for lab, row in netflowData.iterrows():
        try:
            netflowData.loc[lab, 'prot'] = protoData[row['prot']]
        except IndexError:
            netflowData.loc[lab, 'prot'] = row['prot']
    return netflowData

    
# IP Protocol number data
protoData = ('HOPOPT','ICMP','IGMP','GGP','IP-in-IP','ST','TCP','CBT','EGP','IGP','BBN-RCC-MON','NVP-II',
'PUP','ARGUS','EMCON','XNET','CHAOS','UDP','MUX','DCN-MEAS','HMP','PRM','XNS-IDP','TRUNK-1','TRUNK-2',
'LEAF-1','LEAF-2','RDP','IRTP','ISO-TP4','NETBLT','MFE-NSP','MERIT-INP','DCCP','3PC','IDPR','XTP','DDP',
'IDPR-CMTP','TP++','IL','IPv6','SDRP','IPv6-Route','IPv6-Frag','IDRP','RSVP','GRE','DSR','BNA','ESP',
'AH','I-NLSP','SWIPE (deprecated)','NARP','MOBILE','TLSP','SKIP','IPv6-ICMP','IPv6-NoNxt','IPv6-Opts',
'','CFTP','','SAT-EXPAK','KRYPTOLAN','RVD','IPPC','','SAT-MON','VISA','IPCV','CPNX','CPHB','WSN','PVP',
'BR-SAT-MON','SUN-ND','WB-MON','WB-EXPAK','ISO-IP','VMTP','SECURE-VMTP','VINES','TTP/IPTM','NSFNET-IGP',
'DGP','TCF','EIGRP','OSPFIGP','Sprite-RPC','LARP','MTP','AX.25','IPIP','MICP (deprecated)','SCC-SP',
'ETHERIP','ENCAP','','GMTP','IFMP','PNNI','PIM','ARIS','SCPS','QNX','A/N','IPComp','SNP','Compaq-Peer',
'IPX-in-IP','VRRP','PGM','','L2TP','DDX','IATP','STP','SRP','UTI','SMP','SM (deprecated)','PTP',
'ISIS over IPv4','FIRE','CRTP','CRUDP','SSCOPMCE','IPLT','SPS','PIPE','SCTP','FC','RSVP-E2E-IGNORE',
'Mobility Header','UDPLite','MPLS-in-IP','manet','HIP','Shim6','WESP','ROHC')


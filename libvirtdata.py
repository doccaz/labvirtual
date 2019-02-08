#!/usr/bin/python
import libvirt
import sys
import syslog
import re
import subprocess
import json
from subprocess import check_output, CalledProcessError
from subprocess import PIPE
from pprint import pprint
from lxml import etree

class DomainQuery():
    domainStates = { 
        0:'no state',
        1:'running',
        2:'blocked on resource',
        3:'paused',
        4:'shutting down',
        5:'off',
        6:'crashed',
        7:'suspended by power management',
        }

    ''' 
    Funcao basica de log 
    ''' 
    def log(msg): 
        syslog.syslog(msg) 
        print(msg) 
        return 

    # gets a value from a XPath
    def getAttribute(self, xml_in, searchstr, attrname):
        found = xml_in.findall(searchstr)
        try:
            for i in found:
                #print("found = %s" % i.attrib[attrname])
                return i.attrib[attrname]
        except KeyError as e:
            return "<unknown>"


    def __init__(self, conn_uri='qemu:///system'):
        #### main program
        self.domain_db = []
        self.conn = None

        # connect to the hypervisor
        # inicializa logs
        syslog.openlog('libvirt-python', syslog.LOG_PID, syslog.LOG_INFO)
        self.conn = libvirt.open(conn_uri)
        if self.conn == None:
            DomainQuery.log('Error connecting to hypervisor')
            return False

        DomainQuery.log('New connection to libvirtd: %s' % self.conn )
        return None

    def __repr__(self):
        return '<DomainQuery: %s>' % (self.domain_db)

    def getVMOwner(vm_name, port):
        owner = ''

        cmd_list = ['ss', '-tn']
        try:
            cmd_result = subprocess.check_output(cmd_list)
        except CalledProcessError as e:
            DomainQuery.log('Error while determining VM owner')

        test_str = cmd_result.decode('utf-8')
        regex = r"^ESTAB.*\ \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:1" + port + ".*\ (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        matches = re.finditer(regex, test_str, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                if match.group(groupNum) != "127.0.0.1" and match.group(groupNum) != "172.18.88.44":
                    owner = str(match.group(groupNum))
                #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

        if owner != "":
            DomainQuery.log('VM [%s] is in use by IP [%s]' % (vm_name, owner))
            return owner
        return ''


    def get_data(self):
        # get a list of the defined domains(VMs)
        domains = []
        try:
            domains = self.conn.listAllDomains()
        except Exception as e:
            log ('Failure while obtaining domain list: %s' % e)
            return None
        
        # fetch domain data
        for dom in domains:
            # Read some info from the XML desc
            xmldesc = dom.XMLDesc(0)
            #print("xml = [%s]" % xmldesc)
            dom_xml = etree.fromstring(xmldesc)
            #print("dom_xml = [%s]" % dom_xml)
            dom_name = dom.name()
            dom_state = dom.state()[0]
            dom_arch = self.getAttribute(dom_xml,'os/type', 'arch')
            dom_memory_size=int(dom.maxMemory())/1024
            dom_host_bridge = self.getAttribute(dom_xml, "devices/interface/source[@mode='bridge']", 'dev')
            dom_spiceport = self.getAttribute(dom_xml, "devices/graphics[@type='spice']", 'port')
            dom_guestagentport = self.getAttribute(dom_xml, "devices/channel/target[@name='org.qemu.guest_agent.0']", 'port')
            dom_nics = 'unknown'
            dom_type = 'unknown'
            if self.domainStates[int(dom_state)] == "running":
                dom_vcpus = len(dom.vcpus()[0])
                try:
                    ifaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
                except libvirt.libvirtError as e:
                    ifaces = None
                    DomainQuery.log('VM %s does not have a QEMU agent installed' % dom_name)

                if (ifaces == None):
                    dom_nics = 'none'
                else:
                    DomainQuery.log('VM %s does have a QEMU agent installed' % dom_name)
                    try:
                        # if it's Linux, go for eth0
                        dom_nics = ifaces['eth0']['addrs'][0]['addr'] + '/' + str(ifaces['eth0']['addrs'][0]['prefix'])
                        dom_type = "linux"
                    except KeyError as e:
                        # else it might be a windows VM, try the "Local Connection" interfaces
                        dom_type = "windows"
                        for nic in ifaces:
                            if 'Local' in nic:
                                for ip in ifaces[nic]['addrs']:
                                    if ip['type'] == 0:
                                        dom_nics = ip['addr'] + '/' + str(ip['prefix'])
            else:
                dom_vcpus = 0
                dom_nics = 'n/a'


            # determine system version
            dom_osinfo = DomainQuery.getOSVersion(dom_name, dom_type)
                
            domain_data = {}
            domain_data['id'] = dom.ID()
            domain_data['name'] = dom_name
            domain_data['arch'] = dom_arch
            domain_data['nics'] = dom_nics
            domain_data['memory'] = dom_memory_size
            domain_data['vcpus'] = dom_vcpus
            domain_data['state'] = self.domainStates[int(dom_state)]
            domain_data['bridge'] = dom_host_bridge
            if dom_spiceport != "<unknown>":
                domain_data['spiceport'] = "1" + dom_spiceport
            else:
                domain_data['spiceport']  = 'n/a'

            domain_data['type'] = dom_type
            domain_data['osinfo'] = dom_osinfo
            domain_data['object'] = dom

            # check if the websocket port is in use
            if dom_spiceport != '<unknown>':
                domain_data['in_use_by'] = DomainQuery.getVMOwner(dom_name, dom_spiceport)
            else:
                domain_data['in_use_by'] = ''

            #    pprint(domain_data)

            self.domain_db.append(domain_data)
           # pprint(self.domain_db)

        return self.domain_db

    def close():
        DomainQuery.log('ending libvirt session')
        syslog.closelog()
        #libvirt.connectClose(self.conn)
        return

    def getOSVersion(vm_name, vm_type):
        osInfoCMD = {
                "execute":"guest-get-osinfo"
                }

        if vm_type == "windows":
            pprint(json.dumps(osInfoCMD))
            cmd_list = ['virsh', 'qemu-agent-command', vm_name, json.dumps(osInfoCMD)]
            try:
                cmd_result = subprocess.check_output(cmd_list)
            except CalledProcessError as e:
                DomainQuery.log('Error while determining OS info')
                return "unknown"
        return "windows"

        if vm_type == "linux":
            versionInfo = DomainQuery.readFileFromVM(vm_name, "/etc/os-release")
            pprint(versionInfo)
        return "linux"

        
    def readFileFromVM(vm_name, filename):
        file_handle = -1
        fileOpenCMD = {
                "execute":"guest-file-open",
                "arguments":{
                    "path":"%s" % filename
                    }
                }

        fileReadCMD = {
                "execute":"guest-file-read",
                "arguments":{
                    "handle": file_handle, 
                    "count":16384
                    }
                }
        
        fileCloseCMD = {
                "execute":"guest-file-close", 
                "arguments":{
                    "handle":file_handle
                    }
                }

        # get the file handle first
        cmd_list = ['virsh', 'qemu-agent-command', vm_name, json.dumps(fileOpenCMD)]
        try:
            cmd_result = subprocess.check_output(cmd_list)
        except CalledProcessError as e:
            DomainQuery.log('Error while opening file from VM')
            return ""

        file_handle = json.loads(cmd_result)['return']

        if file_handle <= 0:
            DomainQuery.log('Invalid handle while opening file from VM')
            return ""

        # we have a valid file handle, let's get the contents
        cmd_list = ['virsh', 'qemu-agent-command', vm_name, json.dumps(fileReadCMD)]
        try:
            cmd_result = subprocess.check_output(cmd_list)
        except CalledProcessError as e:
            DomainQuery.log('Error while getting file contents from VM')
            return ""
        
        file_contents = json.loads(cmd_result)['return']['buf-b64']
        file_size = json.loads(cmd_result)['return']['count']
        DomainQuery.log("Received file data (%d bytes): [%s]" % (file_size, file_contents))

      #  {"return":{"count":730,"buf-b64":"IyBHZXJhZG8gcG9yIC0gKHZpYSBCQnJleHh0b29scyAxLjAtc3ZuMzQxMjgpCiMgMjAxOS0wMi0wMVQxMjo1MTo1Mi4wNTU1MzlaClNFVFVQX0RBVEU9IjAyLzAxLzE5IDEwOjUxOjEwIgpQUkVGSVhPPSI3OTk3IgpUQUJTUlY9InRhYnNydjAxLmRmLmJiIgpQRVJGSUw9IlRNRi1BRyIKSU5TVEFMTElEPSIzNzQ4OTQ3MCIKU0VSVkVSPSIxMC4xMS4xNzMuMSIKU0VRVUVOQ0lBTD0iMDY5IgpSRUNPTkZJRz0iMCIKSURfUkVHSVNURVI9IjIwMzAzMDMiClVGPSJERiIKTlVNRVJPX1NPTD0iNTkwMDAiClJFR0lTVEVSX0RBVEU9IjctMi0yMDE5IgpTVUJBR0VOQ0lBPSIwMiIKR0FURVdBWV9JUD0iMTAuMTEuMTczLjI1NCIKTEFCT1JBVE9SSU89IjAiCkZPUk5FQ0VET1I9IlRNRi1BRyIKU1JWX0ROU18xPSIxMC4xMS4xNzMuMSIKU1JWX0ROU18yPSIxMC44LjQuMSIKSFdDT05GSUc9IjAiClNSVl9ETlNfMz0iMC4wLjAuMCIKTVVOSUNJUElPPSJCUkFTSUxJQSIKRE9NQUlOPSJhZ2U3OTk3LmJiIgpNQUM9IjUyNTQwMGZlNmJlNCIKSE9TVE5BTUU9IlRGNzk5NzAyMDY5IgpOSUM9ImV0aDAiCk5PTUVfREVQRU49IkFHLiBURVNURSBTT0wgNzk5NyBTQjIiCkJFTV9OVU1FUk89IjEyODYwNDM1NTkwMDA2IgpNT0RFTE89IlRNRi1BRyIKVkVSU0lPTj0iMjAxNzA1MjQwNzAyIgpHQVRFV0FZPSIxMC4xMS4xNzMuMjU0IgpIT1NUSVA9IjEwLjExLjE3My4xMTUiCk1BU0s9IjI1NS4yNTUuMjU1LjAiCg==","eof":true}}

        decoded_file = base64.b64decode(file_contents)
        DomainQuery.log("Decoded content: [%s]" % (decoded_file))

        return ""

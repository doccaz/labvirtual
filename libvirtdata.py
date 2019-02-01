#!/usr/bin/python
import libvirt
import sys
import logging
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
        7:'suspended by power management'
        }


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
        self.conn = libvirt.open(conn_uri)
        if self.conn == None:
            print('Falha ao conectar ao hypervisor')
            return False

        return None

    def __repr__(self):
        return '<DomainQuery: %s>' % (self.domain_db)

    def get_data(self):
        # get a list of the defined domains(VMs)
        domains = []
        try:
            domains = self.conn.listAllDomains()
        except Exception as e:
            print ('Falha ao obter lista de dominios: %s' % e)
            return None
        
        # fetch domain data
        for dom in domains:
            # Read some info from the XML desc
            xmldesc = dom.XMLDesc(0)
            #print("xml = [%s]" % xmldesc)
            dom_xml = etree.fromstring(xmldesc)
            #print("dom_xml = [%s]" % dom_xml)
            dom_name = dom.name()
            try:
                dom_nics = dom.interfaceAddresses(1)
            except libvirt.libvirtError as e:
                dom_nics = "<unknown>"
                print('error while getting interface info for VM %s: %s' % (dom_name, e))
            dom_state = dom.state()[0]
            dom_arch = self.getAttribute(dom_xml,'os/type', 'arch')
            dom_memory_size=int(dom.maxMemory())/1024
            dom_host_bridge = self.getAttribute(dom_xml, "devices/interface/source[@mode='bridge']", 'dev')
            dom_spiceport = self.getAttribute(dom_xml, "devices/graphics[@type='spice']", 'port')

            if self.domainStates[int(dom_state)] == "running":
                dom_vcpus = len(dom.vcpus()[0])
            else:
                dom_vcpus = 0

            domain_data = {}
            domain_data['id'] = dom.ID()
            domain_data['name'] = dom_name
            domain_data['arch'] = dom_arch
            domain_data['nics'] = dom_nics
            domain_data['memory'] = dom_memory_size
            domain_data['vcpus'] = dom_vcpus
            domain_data['state'] = self.domainStates[int(dom_state)]
            domain_data['bridge'] = dom_host_bridge
            domain_data['spiceport'] = dom_spiceport
            domain_data['object'] = dom
            #    pprint(domain_data)

            self.domain_db.append(domain_data)

        #   pprint(domain_db)

        return self.domain_db

    def close():
        print('ending libvirt session')
        # libvirt.connectClose(self.conn)
        return

    def startVM(self, vm_name):
        for d in self.domain_db:
            if d['name'] == vm_name:
                print('starting VM: %s' % vm_name)
                print('create() = %d' % d['object'].create())
        return

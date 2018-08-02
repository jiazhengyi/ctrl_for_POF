'''
Created on Nov 13, 2014

@author: shengrulee
'''

'''
This is PofManager Module.
'''

from pox.lib.revent.revent import EventMixin
from pox.core import core
import pox.openflow.libopenflow_01 as of

import pox.openflow.PMdatabase as pmdatabase
import pox.openflow.bypassmanager as bpm  

log = core.getLogger()

def count_keyLength(flow_table):
    keyLength = 0
    if isinstance(flow_table, of.ofp_flow_table):
        match20_list = flow_table.matchFieldList
        for each_match20 in match20_list:
            keyLength += each_match20.length
        return keyLength
    else:
        log.error('count key length type error.')
        

class PofManager(EventMixin):
    
    def __init__(self):
        core.openflow.addListeners(self)
        
        self.connection_devicedid_dict = {}    #{connection: deviced_id}
        self.device_id_connection_dict = {}
        
        
    def _handle_FeaturesReceived(self, event):
        self.device_id = event.dpid
        self.connection = event.connection
        self.connection_devicedid_dict[self.connection] = self.device_id
        self.device_id_connection_dict[self.device_id] = self.connection
        core.PMdatabase.put_new_switch(event.ofp)
       
    def _handle_PortStatus(self, event):
        self.connection = event.connection
        self.device_id = event.dpid
        self.ofp = event.ofp
        core.PMdatabase.put_port(self.device_id, self.ofp)
    """ 
    def _handle_PortStatus(self, event):
        # add port (except eth0) to the switch
        msg = of.ofp_port_mod()
        msg.desc = event.ofp.desc
        msg.desc.of_enable = 1       # pof enable
        #print "CC: send PORT_MOD message\n",msg
        event.connection.send(msg)
    """    
    """
    def _handle_ConnectionReady(self, event):
        '''
        Make all ports OpenFlowEnable except eth0
        '''
        ports_list = self.get_all_ports(event.dpid)
        for port in ports_list:
            phy_port = port.desc
            if phy_port.openflowEnable == 0 and phy_port.name != 'eth0':
                self.set_port_pof_enable(event.dpid, phy_port.portId) 
        '''
        Install first table.
        '''
        dmac = of.ofp_match20(fieldId = 1, offset = 0, length = 48)
        dl_type = of.ofp_match20(fieldId = 3, offset = 96, length = 16)
        
        first_flow_table = of.ofp_flow_table()
        first_flow_table.matchFieldList.append(dmac)
        first_flow_table.matchFieldList.append(dl_type)
        first_flow_table.tableSize = 128
        first_flow_table.tableName = 'FirstEntryTable'
        
        #self.add_new_table(event.dpid, first_flow_table)
    """
        
    def get_switch(self, device_id):
        return core.PMdatabase.get_switch(device_id)
    
    def get_all_switches(self):
        return core.PMdatabase.get_all_switches()
    
    def get_port(self, device_id, port_id):
        return core.PMdatabase.get_port(device_id, port_id)
    
    def get_all_ports(self, device_id):
        return core.PMdatabase.get_all_ports(device_id)
    
    def set_port_pof_enable(self, device_id, port_id, enable = 1): # send a PORT_MOD message
        core.PMdatabase.set_port_pof_enable(device_id, port_id, enable)
        port_status = core.PMdatabase.get_port(device_id, port_id)
        phy_port = port_status.desc
        port_mod_msg = of.ofp_port_mod()
        port_mod_msg.desc = phy_port
        connection = self.device_id_connection_dict[device_id]
        connection.send(port_mod_msg)
        log.info('Controller -> [%s]: PORT_MOD name=%s port_id=%d ', \
                 device_id, phy_port.name, port_id)      
        
    def get_field_by_name(self, field_name):
        return core.PMdatabase.get_field_by_name(field_name)
        
    def add_new_protocol(self, protocol_name, field_list):
        # field_list is like: [(field_name, offset, length),(),()
        core.PMdatabase.add_new_protocol(protocol_name, field_list)
        
    def get_protocol(self, protocol_id):
        return core.PMdatabase.get_protocol(protocol_id) # return a Protocol() type
        
    def get_protocol_by_name(self, protocol_name):
        return core.PMdatabase.get_protocol_by_name(protocol_name)
        
    def add_new_table(self, device_id, flow_table):
        flow_table.keyLength = count_keyLength(flow_table)
        core.PMdatabase.add_new_table(device_id, flow_table)
        flow_table = core.PMdatabase.get_flow_table(device_id, flow_table.tableId)
        
        table_mod_msg = of.ofp_table_mod()
        table_mod_msg.flowTable = flow_table
        connection = self.device_id_connection_dict[device_id]
        connection.send(table_mod_msg)
        log.info('Controller -> [%s]: TABLE_MOD (Add Table)', device_id)
        
    def get_flow_table(self, device_id, table_id):
        return core.PMdatabase.get_flow_table(device_id, table_id)
        
    def del_flow_table(self, device_id, table_id):
        flow_table = core.PMdatabase.get_flow_table(device_id, table_id)
        
        core.PMdatabase.del_flow_table(device_id, table_id)
        
        flow_table.command = 2   # delete table
        table_mod_msg = of.ofp_table_mod()
        table_mod_msg.flowTable = flow_table
        connection = self.device_id_connection_dict[device_id]
        connection.send(table_mod_msg)
        log.info('Controller -> [%s]: TABLE_MOD (Delete Table)', device_id)   
        
    def add_flow_entry(self, device_id, table_id, flow_mod):
        if isinstance(flow_mod, of.ofp_flow_mod):
            #entry_id = flow_mod.index
            core.PMdatabase.add_flow_entry(device_id, table_id, flow_mod)           
            connection = self.device_id_connection_dict[device_id]
            connection.send(flow_mod)       
            log.info('Controller -> [%s]: FLOW_MOD(Add entry)', device_id)
    
    def get_flow_entry(self, device_id, table_id, flow_entry_id):
        return core.PMdatabase.get_flow_entry(device_id, table_id, flow_entry_id)    
        
    def del_flow_entry(self, device_id, table_id, flow_entry_id):
        #flow_mod = self.get_flow_entry(device_id, table_id, flow_entry_id)
        flow_mod = core.PMdatabase.del_flow_entry(device_id, table_id, flow_entry_id) 
        
        flow_mod.command = 3 # delete the flow entry
        connection = self.device_id_connection_dict[device_id]
        connection.send(flow_mod)  
        
        #core.PMdatabase.del_flow_entry(device_id, table_id, flow_entry_id) 
        log.info('Controller -> [%s]: FLOW_MOD(Delete entry)', device_id)
            

def launch():
    core.registerNew(PofManager)

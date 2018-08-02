'''
Created on Nov 24, 2014

@author: lsr, wenjian
'''

from pox.lib.revent.revent import EventMixin
from pox.core import core
import pox.openflow.libopenflow_01 as of

from collections import defaultdict

log = core.getLogger()

class Field(of.ofp_match20):
    
    def add(self, field_name, field_id, offset, length):
        self.fieldname = field_name
        self.fieldId = field_id
        self.offset = offset
        self.length = length
        return
    
    def modify(self, field_name, offset, length):
        self.fieldname = field_name
        #self.field_id = field_id
        self.offset = offset
        self.length = length
        return
    
    def show(self, prefix=''):
        outstr = ''
        outstr += prefix + 'field_name:' + str(self.fieldname) + '\n'
        outstr += prefix + 'field_id:  '+  str(self.fieldId) + '\n' 
        outstr += prefix + 'offset:    '+  str(self.offset) + '\n' 
        outstr += prefix + 'length:    '+  str(self.length) + '\n' 
        return outstr  
        
    def to_ofp_match20(self):
        field_match20 = of.ofp_match20()
        field_match20.fieldname = self.fieldname
        field_match20.fieldId = self.fieldId
        field_match20.length = self.length
        field_match20.offset = self.offset        
        return field_match20

class Protocol(object):
    
    def __init__(self, protocol_name):
        self.protocol_name = protocol_name
        self.protocol_id = None
        self.totallength = 0    # bit
        self.field_name_dict = {}    # {field_name: field_id}
        self.field_dict = {}    # {field_id: field}      
                  
        self.field_id_assigned = 1         
    
    def add_new_field(self, field_name, offset, length):
        field_id = self.field_id_assigned
        new_field = Field()
        new_field.add(field_name, field_id, offset, length)
        
        self.field_name_dict[field_name] = field_id
        self.field_dict[field_id] = new_field
        self.totallength += length
        
        self.field_id_assigned += 1
        return new_field
    
    def mod_field(self, field_id, field_name, offset, length): # or delete all then add new
        self.field_dict[field_id].modify(field_name, offset, length)
        return
        
    def get_field(self, field_id):
        for each_field_id in self.field_dict.keys():
            each_field = self.field_dict.get(each_field_id)
            if isinstance(each_field, Field) and each_field.field_id == field_id:
                return each_field
            
    def get_field_num(self):
        return len(self.field_dict)
    
    def del_field(self, field_id):
        deleted_field = self.field_dict.pop(field_id)
        return deleted_field
    
    def show(self,prefix = ''):
        outstr = ''
        outstr += prefix + 'protocol_name:' + str(self.protocol_name) + '\n'
        outstr += prefix + 'protocol_id:  ' + str(self.protocol_id) + '\n'
        outstr += prefix + 'totallength:  ' + str(self.totallength) + '\n'
        for each_field_id in self.field_dict.keys():
            outstr += self.field_dict[each_field_id].show(prefix + '  ') 
        return outstr
    
    def to_ofp_match20_list(self):
        ofp_match20_list = []
        for each_field_id in self.field_dict.keys():
            ofp_match20_list.append(self.field_dict[each_field_id].to_ofp_match20())
            
        return ofp_match20_list
    
    def to_match(self, *field_name):
        match_list = []
        for each_field_name in field_name:
            field_id = self.field_name_dict[each_field_name]
            field = self.field_dict[field_id]
            ofp_match20 = field.to_ofp_match20()
            match_list.append(ofp_match20)
        return match_list
            

        
class ProtocolDB(object):
    
    def __init__(self):
        self.protocol_name_dict = {}  # {protocol_name: protocol_id}
        self.protocol_dict = {}    # {protocol_id: protocol}
        
        self.protocol_id_assigned = 1
        
    def add_new_protocol(self, protocol):        
        if isinstance(protocol, Protocol):
            protocol_id = self.protocol_id_assigned
            protocol_name = protocol.protocol_name
            protocol.protocol_id = protocol_id
            
            self.protocol_name_dict[protocol_name] = protocol_id    
            self.protocol_dict[protocol_id] = protocol
            
            self.protocol_id_assigned += 1
        
    def get_protocol(self, protocol_id):
        return self.protocol_dict.get(protocol_id)
    
    def get_protocol_by_name(self, protocol_name):
        protocol_id = self.protocol_name_dict.get(protocol_name)
        return self.get_protocol(protocol_id)

    
    def show(self): 
        outstr = ''       
        for each_protocol_id in self.protocol_dict.keys():
            outstr += self.protocol_dict.get(each_protocol_id).show()           
        return outstr

'''
class FlowEntry(of.ofp_flow_mod):
    
    def __init__(self):
        of.ofp_flow_mod.__init__(self)
        self.flow_entry_id = None
'''          
        
class FlowTableDB(object): # all flow tables in a single switch
    
    def __init__(self):
        #self.flow_table_id = None
        self.flow_table_dict = {}    # {flow_table_id: flow_table}
        self.flow_table_name = {}    # {flow_table_name: flow_table_id}
        self.flow_table_entry = defaultdict(lambda: defaultdict())   # {flow_table_id: flow_entry_id}
               
        #self.flow_table_id_assigned = 0
        
    def add_flow_table(self, flow_table):
        if isinstance(flow_table, of.ofp_flow_table): 
            if flow_table.tableId not in self.flow_table_dict.keys():
                self.flow_table_dict[flow_table.tableId] = flow_table
                self.flow_table_name[flow_table.tableName] = flow_table.tableId
                return True
            else:
                log.error('This table ID is already exist.')
        else:
            log.info('Add flow_table type error in FlowTableDB()')
    
    def get_flow_table(self, flow_table_id):
        return self.flow_table_dict[flow_table_id]
    
    def get_flow_table_by_name(self, table_name):
        flow_table_id = self.flow_table_name[table_name]
        return self.flow_table_dict[flow_table_id]
    
    def del_flow_table(self, flow_table_id):     
        self.flow_table_dict.pop(flow_table_id)        
        
    def add_flow_entry(self, table_id, flow_mod):
        flow_entry_id = flow_mod.index
        if flow_entry_id != None:
            self.flow_table_entry[table_id][flow_entry_id] = flow_mod
        else:
            log.error('Flow entry id is None.')
        
    def get_flow_entry(self, table_id, flow_entry_id):
        if table_id in self.flow_table_entry.keys():
            if flow_entry_id in self.flow_table_entry[table_id].keys():                
                return self.flow_table_entry[table_id][flow_entry_id]
            else:
                log.error('Flow entry id does not exist.')
        else:
            log.error('Table id does not exist.')
            
    def del_flow_entry(self, table_id, flow_entry_id):
        return self.flow_table_entry[table_id].pop(flow_entry_id)
        
    
class Metadata(object): # wenjian
    
    def __init__(self):
        self.metadata_name_dict = {} # {field_name: filed_id}
        self.metadata_dict = {} # {field_id: field}
        self.metadata_id_assigned = 0    
        
    def add_metadata(self, metadata_name, offset, length):
        metadata_id = self.metadata_id_assigned
        new_metadata = Field(metadata_name, metadata_id, offset, length)
        self.metadata_name_dict[metadata_name] = metadata_id
        self.metadata_dict[metadata_id] = new_metadata
        
        self.metadata_id_assigned += 1
        return metadata_id
    
    def mod_metadata(self, metadata_name, new_metadata_name, offset, length):
        metadata_id = self.metadata_name_dict[metadata_name]
        self.metadata_dict[metadata_id].modify(new_metadata_name,offset,length)
        return
    
    def get_metadata_by_name(self, metadata_name):
        metadata_id = self.metadata_name_dict[metadata_name]
        return self.metadata_dict[metadata_id]
    
    def get_metadata_by_id(self, metadata_id):
        return self.metadata_dict[metadata_id]
    
    def get_all_metadata(self):
        return self.metadata_dict
    
    def show(self):
        outstr = ''       
        for each_metadata_id in self.metadata_dict.keys():
            outstr += self.metadata_dict.get(each_metadata_id).show()           
        return outstr


class Switch(object):
    
    def __init__(self, switch_id):
        self.device_id = switch_id
        self.ports_map = {}
        self.flow_table_database_map = {}
        self.counter_table = None
        self.group_table = None
        self.meter_table = None
        
    def put_port(self, port_id, ofp_port_status):
        if isinstance(ofp_port_status, of.ofp_port_status):
            self.ports_map[port_id] = ofp_port_status 
    
    def get_port(self, port_id):
        return self.ports_map[port_id]    # return a ofp_port_status structure
    
        
class PMdatabase(EventMixin):
    
    def __init__(self):
        core.openflow.addListeners(self)
        self.switch_database = {} #    {device_id: ofp_features_reply}
        self.switch_ports_map = defaultdict(lambda:defaultdict()) #    {device_id: [ofp_port_status]}
        
        self.field_database = {}    #  {field_name: Field()}
        self.protocol_database = ProtocolDB()
        self.flow_table_database = {}    #  {device_id: FlowTableDB()}
        
        log.info("PMdatabase initialization...")
        
    def put_new_switch(self, features_reply):
        if isinstance(features_reply, of.ofp_features_reply):                     
            device_id = features_reply.deviceId
            if device_id not in self.switch_database.keys():               
                self.switch_database[device_id] = features_reply
                #self.switch_ports_map[device_id] = []
                log.info('Put new switch [%s] successfully!', device_id)
            else:
                log.info('This switch was already in database.')
        else:
            log.info('put_new_switch: type error.')
            
        return device_id
                
    def get_switch(self, device_id):
        return self.switch_database[device_id]
    
    def get_all_switches(self):
        sw_list = []
        for dev_id in self.switch_database.keys():
            sw_list.append(self.switch_database[dev_id])
        return sw_list
        
    def put_port(self, device_id, port_status):
        if isinstance(port_status, of.ofp_port_status):
            port_id = port_status.desc.portId
            #print port_id
            #if port_id not in self.switch_ports_map[device_id].keys(): 
            self.switch_ports_map[device_id][port_id] = port_status
            return len(self.switch_ports_map[device_id]) 

    def get_port(self, device_id, port_id):
        port_status = self.switch_ports_map[device_id][port_id]
        return port_status
            
    def get_all_ports(self, device_id):
        port_list = []
        for port_id in self.switch_ports_map[device_id].keys():
            port_list.append(self.get_port(device_id, port_id))
        return port_list
    
    def set_port_pof_enable(self, device_id, port_id, enable = 1): # 1: pof enable
        port_status = self.get_port(device_id, port_id)
        phy_port = port_status.desc#.openflowEnable = enable
        phy_port.openflowEnable = enable
        port_status.desc = phy_port
        self.put_port(device_id, port_status)
        return
    
    def get_field_by_name(self, field_name):
        return self.field_database[field_name].to_ofp_match20()
    
    def add_new_protocol(self, protocol_name, field_list): 
        # field_list is like: [(field_name, offset, length),(),()]
        protocol = Protocol(protocol_name)
        for each_field in field_list:
            if isinstance(each_field, tuple):
                new_field = protocol.add_new_field(each_field[0], each_field[1], each_field[2])
                self.field_database[new_field.fieldname] = new_field
            else:
                log.debug('Add new protocol type error.')
        self.protocol_database.add_new_protocol(protocol)
    
    def get_protocol(self, protocol_id):
        return self.protocol_database.get_protocol(protocol_id)
        
    def get_protocol_by_name(self, protocol_name):
        return self.protocol_database.get_protocol_by_name(protocol_name)
    
    def add_new_table(self, device_id, flow_table):
        if isinstance(flow_table, of.ofp_flow_table):           
            self.flow_table_database[device_id] = FlowTableDB()
            self.flow_table_database[device_id].add_flow_table(flow_table)
            
    def get_flow_table(self, device_id, table_id):
        flow_table = self.flow_table_database[device_id].get_flow_table(table_id)
        return flow_table
           
    def del_flow_table(self, device_id, table_id):
        self.flow_table_database[device_id].del_flow_table(table_id)
        
    def add_flow_entry(self, device_id, table_id, flow_mod):       
        self.flow_table_database[device_id].add_flow_entry(table_id, flow_mod)
        
    def get_flow_entry(self, device_id, table_id, flow_entry_id):
        return self.flow_table_database[device_id].get_flow_entry(table_id, flow_entry_id)
        
    def del_flow_entry(self, device_id, table_id, flow_entry_id):
        return self.flow_table_database[device_id].del_flow_entry(table_id, flow_entry_id)
         

def launch():
    core.registerNew(PMdatabase)

if __name__ == "__main__":
    
    '''
    Ethernet header format.
    '''
    eth = Protocol('eth')
    eth.add_new_field('smac', 0, 48)
    eth.add_new_field('dmac', 48,48)
    eth.add_new_field('dl_type', 96, 16)
    
    
    '''
    OOE header format.
    '''    
    ooe = Protocol('ooe')
    ooe.add_new_field('start', 0, 32)
    ooe.add_new_field('length', 32, 32)
    ooe.add_new_field('dst', 64, 32)
    
    eth1 = Protocol('eth')
    eth1.add_new_field('smac', 0, 48)
    eth1.add_new_field('dmac', 48,48)
    eth1.add_new_field('dl_type', 96, 16)
    
    protocolDB1 = ProtocolDB()
    protocolDB1.add_new_protocol(eth)
    protocolDB1.add_new_protocol(ooe)
    
    print protocolDB1.show()
    '''
    print protocolDB1.__hash__()
    print eth.__hash__()
    print eth1.__hash__()
    print ooe.__hash__()
    print eth.__eq__(eth1)
    '''
    smac = Field()
    smac.add('smac',1, 0, 48)
    
    smac = smac.to_ofp_match20()
    print type(smac)
    print smac.length
    
    for each in ooe.to_ofp_match20_list():
        print each
        print type(each)
    
    
    
    

    
    
    
    
    

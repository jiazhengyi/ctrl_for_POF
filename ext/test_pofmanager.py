'''
Created on Dec 8, 2014

@author: lsr
'''

from pox.core import core
from pox.lib.revent.revent import EventMixin
import pox.openflow.libopenflow_01 as of

import time
from collections import defaultdict
from pox.openflow.PMdatabase import Field


#IPL231_dpid = 0x84088b2e
#IPL230_dpid = 0x84088aaa

sw_id2device_id = {1: 1254483000,
                   2: 1254483280,
                   3: 731388032,
                   4: 9212580
                   }
device_id2sw_id = {v:k for k, v in sw_id2device_id.items()}  #reverse

topo = defaultdict(lambda: defaultdict(lambda: None))
#topo[sw_id][sw_id] = egress_port
topo[1][2] = 1
topo[2][1] = 1
topo[1][3] = 3
topo[3][1] = 1
topo[1][4] = 5

eth_ipv4_field_list = [('dmac', 0, 48), ('smac', 48, 48), ('type', 96, 16)]
ipv4_field_list = [ ('version',112,4),('IHL', 116, 4), ('tos', 120, 8), 
                    ('totallength', 128, 16), ('id', 134, 16), ('flags_offset', 150, 16),
                    ('ttl', 168, 8), ('protocol', 176, 8), ('checksum', 184, 16),
                    ('sip', 200, 32), ('dip', 232, 32)]
ipvx_field_list = [('dip', 0, 64),('sip', 64, 128), ('protocol', 128, 16)]


class test_pofmanager(EventMixin):
    
    def __init__(self):
        core.openflow.addListeners(self)       
        core.PofManager.add_new_protocol('ethernet+ipv4', eth_ipv4_field_list)
        print core.PofManager.get_protocol_by_name('ethernet+ipv4').show()
        
    def _handle_ConnectionUp(self, event):

        sw_list = core.PofManager.get_all_switches()
        print 'switch number:', len(sw_list)
        '''
        Set port to openflow enable.
        '''
        for sw in sw_list:
            if isinstance(sw, of.ofp_features_reply):                    
                #print sw.show()
                ports_list = core.PofManager.get_all_ports(sw.deviceId)
                for port in ports_list:
                    phy_port = port.desc
                    if phy_port.openflowEnable == 1 and phy_port.name == 'eth0':
                        core.PofManager.set_port_pof_enable(event.dpid, phy_port.portId,0)       
                        #print core.PofManager.get_port(event.dpid, 7).show()
         
        '''
        Send second table mod
        '''
        flow_table = of.ofp_flow_table(tableName = 'Mac flow table',\
                                        tableId = 1, tableSize = 128)
        protocol = core.PofManager.get_protocol_by_name('ethernet+ipv4')
        flow_table.matchFieldList = protocol.to_match('dmac')       
        core.PofManager.add_new_table(event.dpid, flow_table)
        
        '''
        Install first entry in the first table
        '''
        #print 'get field', 'smac' 
        #print core.PofManager.get_field_by_name('smac')
        
        flow_mod_msg1 = of.ofp_flow_mod(tableId = 0, index = 0, priority = 1)
        dmac = of.ofp_matchx(fieldId = 1, offset = 0, length = 48)    
        dmac.set_value("010203040506")
        #dmac.value = [0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c]
        dmac.set_mask("000000000000")
        
        dl_type = of.ofp_matchx(fieldId = 2, offset = 96, length = 16)
        dl_type.set_value('0908')
        dl_type.set_mask("0000")

        flow_mod_msg1.matchx.append(dmac)
        flow_mod_msg1.matchx.append(dl_type)
        
        ins = of.ofp_instruction_gototable()
        ins.nextTableId = 1
        
        flow_mod_msg1.instruction.append(ins)
            
        core.PofManager.add_flow_entry(event.dpid, 0, flow_mod_msg1)
                        
    def _handle_PacketIn(self, event): 
                 
        '''
        Table_mod msg
        '''    
        packet = event.parsed
                
        if packet.effective_ethertype == 0x0908:

            print 'Dmac:', packet.dst
            print 'eth type: %x' % packet.effective_ethertype
            
            path = [(1,1,5), (4,1,3)] #(sw_id, in_port, out_port)
            table_id = 1
            entry_id = 0
            
            for each_sw in path:
                
                flow_mod_msg = of.ofp_flow_mod(tableId = table_id, index = entry_id,\
                                               priority = 0, idleTimeout = 1000)
                
                dmac = of.ofp_matchx(fieldId = 1, offset = 0, length = 48)
                print packet.dst.toStr()
                dmac.set_value("0708090a0b0c")
                dmac.set_mask("ffffffffffff")
                flow_mod_msg.matchx.append(dmac)               
                '''        
                smac = of.ofp_matchx()
                smac.fieldId = 2
                smac.offset = 48
                smac.length = 48
                flow_mod_msg.matchx.append(smac)
                
                type1 = of.ofp_matchx()
                type1.fieldId = 3
                type1.offset = 96
                type1.length = 16
                flow_mod_msg.matchx.append(type1)
                '''    
                if each_sw[0] == 4: 
                    instruction1 = of.ofp_instruction_applyaction()
                    version = of.ofp_matchx(fieldId = 4, offset = 100, length = 4)
                    version.set_mask('f')
                    version.set_value('4')
                    
                    action1 = of.ofp_action_setfield()
                    action1.fieldSetting = version
                    instruction1.actionList.append(action1)
                    flow_mod_msg.instruction.append(instruction1) 
                                  
                action2 = of.ofp_action_output()
                action2.portId = each_sw[2]   # out port                   
                instruction2 = of.ofp_instruction_applyaction()
                instruction2.actionList.append(action2) 
                
                      
                flow_mod_msg.instruction.append(instruction2)   
                          
                core.PofManager.add_flow_entry(sw_id2device_id[each_sw[0]], table_id, flow_mod_msg)   
                #core.PofManager.del_flow_entry(event.dpid, table_id, entry_id)
     
def launch():
    core.registerNew(test_pofmanager)
        

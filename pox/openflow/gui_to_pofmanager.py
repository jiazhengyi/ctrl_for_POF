'''
Created on Dec 12, 2014

@author: Wenjian
'''
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent.revent import EventMixin

import string

log = core.getLogger()

table_id_set = set()

def add_new_protocol(gui_protocol_name, gui_protocol):
    protocol_name = gui_protocol_name
    protocol = []
    for each_field in gui_protocol:
        if isinstance(each_field, tuple):
            field_tuple = (each_field[0],each_field[2],each_field[1])
            protocol.append(field_tuple)
        else:
            log.error('add new protocol error')
    #return protocol
    core.PofManager.add_new_protocol(protocol_name, protocol)

def del_protocol():
    pass
  
def add_flowtable_flowmod(device_id_str, table):
    global table_id_set
    
    table_id = table['table_id']
    #device_id = string.atoi(device_id_str)
    device_id = device_id_str
    if table_id in table_id_set:
        add_flow_entry(device_id, table)
    elif table_id not in table_id_set:
        
        table_id_set.add(table_id)
        
        add_new_table(device_id, table)
        add_flow_entry(device_id, table)

def add_new_table(device_id, table):
    flow_table = of.ofp_flow_table()
    
    flow_table.tableId = table['table_id']
    flow_table.tableName = table['table_name']
    flow_table.tableSize = string.atoi(table['size'])# table size
    
    match_list = []
    field_id_assigned = 0;
    for each_field in table['Table_entry']['match']:
        field_match20 = of.ofp_match20()
        field_match20.fieldId = field_id_assigned;
        field_match20.fieldname = each_field[0]
        field_match20.offset = each_field[2]
        field_match20.length = each_field[1]
        match_list.append(field_match20)
        field_id_assigned = field_id_assigned + 1
    
    flow_table.matchFieldList = match_list
    core.PofManager.add_new_table(device_id, flow_table)
    
def add_flow_entry(device_id, table):
    flow_mod_msg = of.ofp_flow_mod()
    
    flow_mod_msg.tableId = table['table_id']

    matchx_list = []
    field_id_assigned = 0;
    for each_field in table['Table_entry']['match']:
        field_matchx = of.ofp_matchx()
        field_matchx.fieldId = field_id_assigned;
        #field_matchx.fieldname = each_field[0]
        field_matchx.offset = each_field[2]
        field_matchx.length = each_field[1]
        field_matchx.set_value(each_field[3])
        field_matchx.set_mask(each_field[4])
        matchx_list.append(field_matchx)
        field_id_assigned = field_id_assigned + 1
    
    flow_mod_msg.matchx = matchx_list
    flow_mod_msg.index = string.atoi(table['Table_entry']['entry_id']) # !!!have problem!!!
    flow_mod_msg.priority = string.atoi(table['priority'])
    
    for each_key in table['instruction'].keys():
        #print table['instruction']
        if each_key == 'goto_table':
            instr = instr_goto_table(table['instruction']['goto_table'])
            flow_mod_msg.instruction.append(instr)
            table_id = flow_mod_msg.tableId
            core.PofManager.add_flow_entry(device_id, table_id, flow_mod_msg)

        elif each_key == 'goto_direct_table':
            instr = instr_goto_direct_table(table['instruction']['goto_direct_table'])
            flow_mod_msg.instruction.append(instr)
            table_id = flow_mod_msg.tableId
            core.PofManager.add_flow_entry(device_id, table_id, flow_mod_msg)
            
        elif each_key == 'meter':
            instr = instr_meter(table['instruction']['meter'])
            flow_mod_msg.instruction.append(instr)
            table_id = flow_mod_msg.tableId
            core.PofManager.add_flow_entry(device_id, table_id, flow_mod_msg)
        
        elif each_key == 'write_metadata':
            instr = instr_write_metadata(table['instruction']['write_metadata'])
            flow_mod_msg.instruction.append(instr)
            table_id = flow_mod_msg.tableId
            core.PofManager.add_flow_entry(device_id, table_id, flow_mod_msg)
        
        elif each_key == 'write_metadata_from_flow':
            instr = instr_write_metadata_from_flow(table['instruction']['write_metadata_from_flow'])
            flow_mod_msg.instruction.append(instr)
            table_id = flow_mod_msg.tableId
            core.PofManager.add_flow_entry(device_id, table_id, flow_mod_msg)
        
        elif each_key == 'apply_action':
            instr = instr_apply_action(table['instruction']['apply_action'])
            flow_mod_msg.instruction.append(instr)
            table_id = flow_mod_msg.tableId
            core.PofManager.add_flow_entry(device_id, table_id, flow_mod_msg)
            
def instr_goto_table(goto_table_data):
    goto_table = of.ofp_instruction_gototable()
    nextid = string.split(goto_table_data[0]['table_id'],':')[0]
    if goto_table_data[0]['offset'] == '':
        offset = 0
    else:
        offset = string.atoi(goto_table_data[0]['offset'])
    goto_table.nextTableId =  string.atoi(nextid)
    goto_table.packetOffset = offset
    return goto_table

def instr_goto_direct_table(goto_direct_table_data):
    goto_direct_table = of.ofp_instruction_gotodirecttable()
    nextid = string.split(goto_direct_table_data[0]['table_id'],':')[0]
    if goto_direct_table_data[0]['entry_index'] == '':
        entryindex = 0
    else:
        entryindex = string.atoi(goto_direct_table_data[0]['entry_index'])
    
    if goto_direct_table_data[0]['offset'] == '':
        offset = 0
    else:
        offset = string.atoi(goto_direct_table_data[0]['offset'])
    
    goto_direct_table.nextTableId =  string.atoi(nextid)
    goto_direct_table.indexValue = entryindex
    goto_direct_table.packetOffset = offset
    return goto_direct_table

def instr_meter(meter_data):
    meter = of.ofp_instruction_meter()
    meter.meterId = string.atoi(meter_data[0]['Meter_ID'])
    return meter

'''
what is metadata
'''
def instr_write_metadata(write_metadata_data):
    #write_metadata = of.ofp_instruction_writemetadata()
    
    #write_metadata.
    pass
def instr_write_metadata_from_flow(write_metadata_from_flow_data):
    pass

def instr_apply_action(apply_action_data):
    applyaction = of.ofp_instruction_applyaction()

    for each_action in apply_action_data.keys():
        
        if each_action == 'output':
            action = action_output(apply_action_data['output'])
            applyaction.actionList.append(action)

        elif each_action == 'set_field':
            action = action_set_field(apply_action_data['set_field'])
            applyaction.actionList.append(action)
            
        elif each_action == 'set_field_from_metadata':
            action = action_set_field_from_metadata(apply_action_data['set_field_from_metadata'])
            applyaction.actionList.append(action)
            
        elif each_action == 'modify_field':
            action = action_modify_field(apply_action_data['modify_field'])
            applyaction.actionList.append(action)
            
        elif each_action == 'add_field':
            action = action_add_field(apply_action_data['add_field'])
            applyaction.actionList.append(action)
            
        elif each_action == 'delete_field':
            action = action_delete_field(apply_action_data['delete_field'])
            applyaction.actionList.append(action)
            
        elif each_action == 'calculate_checksum':
            action = action_calculate_checksum(apply_action_data['calculate_checksum'])
            applyaction.actionList.append(action)
        
        elif each_action == 'group':
            action = action_group(apply_action_data['group'])
            applyaction.actionList.append(action)
            
        elif each_action == 'drop':
            action = action_drop(apply_action_data['drop'])
            applyaction.actionList.append(action)
            
        elif each_action == 'packet_in':
            action = action_packet_in(apply_action_data['packet_in'])
            applyaction.actionList.append(action)
            
        elif each_action == 'counter':
            action = action_counter(apply_action_data['counter'])
            applyaction.actionList.append(action)
    
    return applyaction

               
def action_output(action_output_data):
    output = of.ofp_action_output()
    output.portId = string.atoi(action_output_data[0]['output'])
    return output

def action_set_field(action_set_field_data):
    set_field = of.ofp_action_setfield()
    fieldsetting = of.ofp_matchx()
    fieldname_temp = action_set_field_data[0]['name']
    fieldname = string.split(fieldname_temp, ';')[0]
    #value = string.atoi(action_set_field_data[0]['value'])
    #mask = string.atoi(action_set_field_data[0]['mask'])
    
    fieldsetting_of20 = core.PofManager.get_field_by_name(fieldname)
    fieldsetting.fieldId = fieldsetting_of20.fieldId
    fieldsetting.offset = fieldsetting_of20.offset
    fieldsetting.length = fieldsetting_of20.length
    fieldsetting.set_value(action_set_field_data[0]['value'])
    fieldsetting.set_mask(action_set_field_data[0]['mask'])
    
    set_field.fieldSetting = fieldsetting
    
    return set_field

def action_set_field_from_metadata(action_set_field_from_metadata_data):
    set_field_from_metadata = of.ofp_action_setfieldfrommetadata()
    #fieldname = action_set_field_from_metadata_data[0]['name']
    fieldname_temp = action_set_field_from_metadata_data[0]['name']
    fieldname = string.split(fieldname_temp, ';')[0]
    fieldsetting_of20 = core.PofManager.get_field_by_name(fieldname)
    
    set_field_from_metadata.fieldsetting = fieldsetting_of20
    set_field_from_metadata.metadataoffset = string.atoi(action_set_field_from_metadata_data[0]['metadata_offset'])

    return set_field_from_metadata

def action_modify_field(action_modify_field_data):
    modify_field = of.ofp_action_modifyfield()
    #fieldname = action_modify_field_data[0]['name']
    fieldname_temp = action_modify_field_data[0]['name']
    fieldname = string.split(fieldname_temp, ';')[0]
    matchfield_of20 = core.PofManager.get_field_by_name(fieldname)
    
    modify_field.matchfield = matchfield_of20
    modify_field.increment = string.atoi(action_modify_field_data[0]['Increment'])
    
    return modify_field

def action_add_field(action_add_field_data):
    add_field = of.ofp_action_addfield()
    
    exist_field_name = string.split(action_add_field_data[0]['Existed_Field'],':')[0]
    fieldname = string.split(exist_field_name, ':')[1]
    #fieldsetting = eval(action_add_field_data[0]['Existed_Field'])
    
    
    fieldsetting_of20 = core.PofManager.get_field_by_name(fieldname)
    add_field.fieldId = fieldsetting_of20.fieldId#fieldsetting['Name']
    #add_field.fieldLength = fieldsetting['Length']
    #add_field.fieldPosition = fieldsetting['Offset']
    add_field.fieldLength = fieldsetting_of20.length
    add_field.fieldPosition = fieldsetting_of20.offset
    add_field.set_fieldValue(action_add_field_data[0]['field_value'])
    
    return add_field
 
def action_delete_field(action_delete_field_data):
    #delete_field = of.ofp_action_deletefield()
    pass

def action_calculate_checksum(action_calculate_checksum_data):
    pass

def action_group(action_group_data):
    pass

def action_drop(action_drop_data):
    drop = of.ofp_action_drop()
    reason = action_drop_data[0]['Reason']
    drop.reason = of.ofp_drop_reason_rev_map[reason]
    
    return drop 

def action_packet_in(action_packet_in_data):
    packet_in = of.ofp_action_packetin()
    reason = action_packet_in_data[0]['Reason']
    packet_in.reason = of.ofp_packet_in_reason_rev_map[reason]
    
    return packet_in

def action_counter(action_counter_data):
    counter = of.ofp_action_counter()
    counter.counterId = string.atoi(action_counter_data[0]['Counter_ID'])
    
    return  counter

def del_flow_table(device_id, table_id):
    global table_id_set
    if table_id in table_id_set:
        table_id_set.remove(table_id)
        core.PofManager.del_flow_table(device_id, table_id)
    else:
        print 'the table does not exist'
        
def del_flow_entry(device_id, table_id, entry_id):
    core.PofManager.del_flow_entry(device_id, table_id, entry_id)

'''
Use to send a flow entry in FirstEntryTable.
@author: shengrulee
'''
class gui_to_pofmanager(EventMixin):
    
    def __init__(self):
        core.openflow.addListeners(self)
        
    def _handle_PacketIn(self, event): 
        
        packet = event.parsed
        
        if packet.effective_ethertype == 0x0908:
            
            table_id = 0
            entry_id = 1
            
            flow_mod_msg0 = of.ofp_flow_mod(tableId = table_id, index = entry_id, priority = 1)
            
            dmac = of.ofp_matchx(fieldId = 1, offset = 0, length = 48)
            dmac.set_value("010203040506")
            dmac.set_mask("000000000000")            
            dl_type = of.ofp_matchx(fieldId = 3, offset = 96, length = 16)
            dl_type.set_value('0908')
            dl_type.set_mask("0000")
    
            flow_mod_msg0.matchx.append(dmac)
            flow_mod_msg0.matchx.append(dl_type)
            
            ins = of.ofp_instruction_gototable()
            ins.nextTableId = 1
            
            flow_mod_msg0.instruction.append(ins)
            
            event.connection.send(flow_mod_msg0)


def launch():
    core.registerNew(gui_to_pofmanager)













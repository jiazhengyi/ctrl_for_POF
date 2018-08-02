#coding:utf-8
"""
此文件主要用来配置流表
"""
import sys
sys.path.append('../../')

from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
import global_env as g

# match field format:{ field_id:[offset, length]}
#field_config = { 46:[0,32], 47:[32,64]}

# matchx format: { ('tname', index, field_id):[value, mask]}
#matchx = {('first table', 0, 46):['00000000', '00000001']}
# table format:{'tname':[tid, type, tsize, [match_field]]
#table = {'first table': [0, of.OF_MM_TABLE, 128, [46, 47]]}

# entry format:{(tname, index):[priority, counter_id, [matchx_id]}
#entry = {('first table', 0):[0, 0, [46]]}


def act_drop(args):# [reason]
	action=of.ofp_action_drop()
	action.reason = args[0]  
	print ("add the action 'drop' \n")

	return action


def act_cal_checksum(args):# [store_pos_type,  [args1], cal_pos_type, [args2]]
	action = of.ofp_action_calculatechecksum()
	action.checksumPosType = args[0]
	store = args[1]
	action.calcPosType = args[2]
	cal = args[3]
	if 0 == args[0]:
		action.checksumPosition = store[0]
		action.checksumLength = store[1]
	else :
		print ("the checksum pos value type is 1\n")
	
	if 0 == args[2]:
		action.calcStarPosition = cal[0]
		action.calcLength = cal[1]
	else :
 		print ("the cal field type is 1\n")

	print ("add the calculate checksum action\n")
	
	return action

def act_counter(args): # [counterId]
	action=of.ofp_action_counter()
	action.counterId = args[0]
	print ("add the counter action\n")
	
	return action

def ins_goto_table(args): # [next_table_id]
 	tempins=of.ofp_instruction_gototable()
    	tempins.nextTableId = args[0]
	print ("add the instruction go to table\n")

	return tempins


def ins_set_pkt_offset(args): #[offsettype, [value]] ps: value decide by the type
	tempins=of.ofp_instruction_setpacketoffset()
	tempins.offsetType = args[0]
	value = args[1]
	
	if 0 == args[0]:
		tempins.setvalue = value[0] # bytes
	else :
		print ("the offset type is 1\n")

	print ("add the set packet offset nstruction\n")

	return tempins


def ins_mov_pkt_offset(args):# [dir, valuetype, [value]]
	tempins=of.ofp_instruction_movepacketoffset()
	tempins.direction = args[0]
  	tempins.valueType = args[1]
	value = args[2]
	
	if 0 == args[1]:
	  	tempins.move_value = value[0]
	else :
		print ("the value type is 1\n")

	print ("add the instruction move pkt offset\n")

	return tempins


def ins_app_action(args): # [act1, act2, act3,..] ps: act = [act name, act args]
	tempins = of.ofp_instruction_applyaction()
	for i in args:
		tempact = insmap[i[0]](i[1])
		tempins.actionList.append(tempact)
	
	print ("add the apply instruction\n")
	return tempins


def act_add_field (args): # [field_id, value]
	action = of.ofp_action_addfield()
	action.fieldId = args[0]
	f = g.field_config[args[0]]
	action.fieldPosition = f[0]
	action.fieldLength = f[1]
	action.set_fieldValue(args[1])
	print ("add  'add_field' action\n")
	
	
	return action
	


def act_del_field (args): # [offset, length]
	print ("add delete field action\n")
	action=of.ofp_action_deletefield()
	action.tagPosition = args[0]
	action.tagLengthValueType = 0
	action.tagLengthValue = args[1]

	return action

def act_modify_field (args): # [field_id, increment]
	print ("add the modify field action\n")
	action = of.ofp_action_modifyfield()
	action.matchfield.fieldId = args[0]
	action.increment = args[1]
	
	f = g.field_config[args[0]]
	action.matchfield.offset = f[0]
	action.matchfield.length = f[1]
	#  action.increment = -1 + 2**32

	return action

def act_set_field (args): # [field_id, value, mask]
	action = of.ofp_action_setfield()
	action.fieldSetting.fieldId = args[0]
	f = g.field_config[args[0]]
	action.fieldSetting.offset = f[0]
	action.fieldSetting.length = f[1]
	action.fieldSetting.set_value(args[1]) 
	action.fieldSetting.set_mask(args[2])
	
	print ("add set_field action\n")
	return action

def act_output (args):  # [port_id]
	action = of.ofp_action_output()
	action.portId = args[0]
	action.metadataOffset = 0
	action.metadataLength = 0
	action.packetOffset = 0
	
	print ("add output action\n")
	return action


insmap = {
		'gototable': ins_goto_table,
		'setoffset': ins_set_pkt_offset,
		'movoffset': ins_mov_pkt_offset,
		'applyaction': ins_app_action,
		'addfield': act_add_field,
		'delfield': act_del_field,
		'modfield': act_modify_field,
		'setfield': act_set_field,
		'output': act_output,
		'drop': act_drop,
		'calchecksum': act_cal_checksum,
		'counter': act_counter,

}




def add_flow_table (tname): 
	#global field_config

	msg = of.ofp_table_mod()
	
	t = g.table[tname]
	msg.flowTable.command = 0    #OFPTC_ADD
	msg.flowTable.tableName = tname
	msg.flowTable.tableId = t[0]
	msg.flowTable.tableType = t[1]
	msg.flowTable.tableSize = t[2]
	msg.flowTable.matchFieldNum = len(t[3])


	key_len = 0
	match_field = []
	for i in t[3]:
		ofmatch20 = of.ofp_match20()
		ofmatch20.fieldId = i
		ofmatch20.offset = g.field_config[i][0]
		ofmatch20.length = g.field_config[i][1]
		match_field.append(ofmatch20)
		key_len += ofmatch20.length

	msg.flowTable.matchFieldList = match_field
	msg.flowTable.keyLength = key_len

	return msg


def add_flow_entry (tname, index):

	msg = of.ofp_flow_mod()
	msg.cookie = 0
	msg.cookieMask = 0

	e = g.entry[tname, index]
	g.counter_id += 1
	msg.counterId = g.counter_id
	msg.index = index
	msg.priority = e[0]
	msg.tableId = g.table[tname][0]
	msg.tableType = g.table[tname][1]

	for i in e[1]:
		tempmatchx = of.ofp_matchx()
		tempmatchx.fieldId = i
		tempmatchx.offset = g.field_config[i][0]
		tempmatchx.length = g.field_config[i][1]

		tempmatchx.set_value(g.matchx[tname, index, i][0])
		tempmatchx.set_mask(g.matchx[tname, index, i][1])

		msg.matchx.append(tempmatchx)

	instruct = g.ins[tname, index]
	
	for i in instruct:
		tempins = insmap[i[0]](i[1])
		msg.instruction.append(tempins)
		
	
	return msg



def print_entry (e):
	print ("index:%d\ntable id:%d\npri:%d\ncounterId:%d\n"\
		%(e.index, e.tableId, e.priority, e.counterId))
	return

def print_table (t):
	print ("table_name:%s\ntable_type:%d\ntable_id:%d\n"\
	%(t.flowTable.tableName,t.flowTable.tableType, t.flowTable.tableId))
	return

if __name__ == '__main__':
	t = add_flow_table('first table')
	e = add_flow_entry('first table', 1)

	print ("table_name:%s\ntable_type:%d\ntable_id:%d\n"\
	%(t.flowTable.tableName,t.flowTable.tableType, t.flowTable.tableId))
	print ("table key len:%d\nmatch_field_num:%d\n"%(t.flowTable.keyLength, t.flowTable.matchFieldNum))

	print ("index:%d\ntable id:%d\npri:%d\ncounterId:%d\n"\
		%(e.index, e.tableId, e.priority, e.counterId))


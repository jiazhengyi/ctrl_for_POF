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
import read_rules as r

# match field format:{ field_id:[offset, length, mask]}
#field_config = { 46:[0,32,'0xffffffff']}

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

def ins_to_cp(args): # [reasontype,app_act_flag,endflag,max_len,meta_pos,meta_len,reasonvalue/field_name] 
	tempins = of.ofp_instruction_to_CP()
	tempins.reasonType = args[0]    #0: immediate value; 1: from field
	tempins.apply_action_flag = args[1]
	tempins.end_flag = args[2]
	tempins.max_len = args[3]
	tempins.meta_pos = args[4]
	tempins.meta_len = args[5]
	if (0 == tempins.reasonType):
		tempins.reasonValue = args[6] 
	else : 
		field = g.field_config[args[6]]
		ofmatch20 = of.ofp_match20()
		ofmatch20.fieldId = field[0]
		ofmatch20.offset = field[1]
		ofmatch20.length = field[2]
		tempins.reason_field = ofmatch20

	print ("add the instruction to_CP \n")
	return tempins



def ins_app_action(args): # [act1, act2, act3,..] ps: act = [act name, act args]
	tempins = of.ofp_instruction_applyaction()
	for i in args:
		print i[0]
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
		'tocp':ins_to_cp,
		'addfield': act_add_field,
		'delfield': act_del_field,
		'modfield': act_modify_field,
		'setfield': act_set_field,
		'output': act_output,
		'drop': act_drop,
		'calchecksum': act_cal_checksum,
		'counter': act_counter,

}


def add_match_field (tname):
	key_len = 0
	match_field = []
	field_name_list = g.table[tname][3]
	for i in field_name_list:
		field = g.field_config[i]
		ofmatch20 = of.ofp_match20()
		ofmatch20.fieldId = field[0]
		ofmatch20.offset = field[1]
		ofmatch20.length = field[2]
		match_field.append(ofmatch20)
		key_len += ofmatch20.length

	return match_field, key_len


def gen_add_table_msg (tname):
	# global field_config

	msg = of.ofp_table_mod()
	
	t = g.table[tname]
	msg.flowTable.command = 0   #OFPTC_ADD
	msg.flowTable.tableName = tname
	msg.flowTable.tableId = t[0]
	msg.flowTable.tableType = t[1]
	msg.flowTable.tableSize = t[2]
	msg.flowTable.matchFieldNum = len(t[3])

	field_info = add_match_field(tname)
	msg.flowTable.matchFieldList = field_info[0]
	msg.flowTable.keyLength = field_info[1]

	return msg

def add_matchx_value_mask(field_name, value, mask):
	field = g.field_config[field_name]
	tempmatchx = of.ofp_matchx()
	tempmatchx.fieldId = field[0]
	tempmatchx.offset = field[1]
	tempmatchx.length = field[2]

	tempmatchx.set_value(value)
	tempmatchx.set_mask(mask)

	return tempmatchx


def gen_add_entry_from_config (tname,index):
	msg = of.ofp_flow_mod()
	msg.cookie = 0
	msg.cookieMask = 0

	e = g.entry[tname, index]
	msg.index = index
	msg.priority = e[0]
	msg.tableId = g.table[tname][0]
	msg.tableType = g.table[tname][1]

	matchx  = e[1]
	for i in matchx.keys():
		value = matchx[i][0]
		mask = matchx[i][1]
		tempmatchx = add_matchx_value_mask(i, value, mask)
		msg.matchx.append(tempmatchx)

	ins_sets = e[2]
	for i in ins_sets.keys():
		args = ins_sets[i]
		tempins = insmap[i](args)
		msg.instruction.append(tempins)
	
	return msg

def gen_add_entry_msgs_from_file (tname, file):
	msgs = []
	file_value = r.read_field_value(file, g.files[file][0])
	value_mask = r.map_file_value_to_field_value(tname,file)
	value = value_mask[0]
	mask = value_mask[1]
	ins_set = g.files[file][2]
	ins_arg = g.files[file][3]
	e_num = len(file_value[0])
	pri = e_num #only for static entry add
	for i in range(0,e_num):
		msg = add_one_flow_entry(tname, i, pri, value, mask, ins_set, ins_arg, file_value)
		msgs.append(msg)
		pri = pri - 1

	return msgs

def add_one_flow_entry (tname, index, pri, value, mask, inss, arg_map, arg_value):
	msg = of.ofp_flow_mod()
	msg.cookie = 0
	msg.cookieMask = 0
	msg.index = index
	msg.priority = pri

	tab = g.table[tname]
	msg.tableId = tab[0]
	msg.tableType = tab[1]

	field_list = tab[3]
	for j in field_list:
		temp = add_matchx_value_mask(j, value[j][index], mask[j][index])
		msg.matchx.append(temp)
	
	args = []
	for i in inss:
		n = arg_map[i]
		for j in n:
			args.append(arg_value[j][index]) 
		tempins = insmap[i](args)
		msg.instruction.append(tempins)
		
	return msg


def add_classfier_table(tname):
	msg = of.ofp_experimenter()
	msg.type = of.CLASSFIER_TABLE
	msg.ctab.type = of.SYNC_TABLE

	table = of.sync_flow_table()
	t = g.table[tname]
	table.command = 0    #OFPTC_ADD
	table.tableName = tname
	table.tableId = t[0]
	table.tableType = t[1]
	table.tableSize = t[2]
	table.matchFieldNum = len(t[3])
	field_info = add_match_field(tname)
	table.matchFieldList = field_info[0]
	table.keyLength = field_info[1]

	msg.ctab.table = table

	return msg


def add_classfier_entry(tname, index):
	msg = of.ofp_experimenter()
	msg.type = of.CLASSFIER_TABLE
	msg.ctab.type = of.SYNC_ENTRY

	entry = of.sync_flow_entry()
	e = g.entry[tname, index]
	entry.cookie = 0
	entry.cookieMask = 0

	entry.index = index
	entry.priority = e[0]
	g.counter_id += 1
	entry.counterId = g.counter_id
	entry.tableId = g.table[tname][0]
	entry.tableType = g.table[tname][1]

	matchx  = e[1]
	for i in matchx.keys():
		value = matchx[i][0]
		mask = matchx[i][1]
		tempmatchx = add_matchx_value_mask(i, value, mask)
		entry.matchx.append(tempmatchx)

	ins_sets = e[2]
	for i in ins_sets.keys():
		args = ins_sets[i]
		tempins = insmap[i](args)
		entry.instruction.append(tempins)
	
	msg.ctab.entry = entry

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
	t1 = 'L3table'
	gen_add_table_msg(t1)
	gen_add_entry_from_config(t1, 0)
	gen_add_entry_msgs_from_file(t1, g.file1)

'''
	print ("table_name:%s\ntable_type:%d\ntable_id:%d\n"\
	%(t.flowTable.tableName,t.flowTable.tableType, t.flowTable.tableId))
	print ("table key len:%d\nmatch_field_num:%d\n"%(t.flowTable.keyLength, t.flowTable.matchFieldNum))

	print ("index:%d\ntable id:%d\npri:%d\ncounterId:%d\n"\
		%(e.index, e.tableId, e.priority, e.counterId))
'''

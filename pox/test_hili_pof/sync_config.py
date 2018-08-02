
#coding:utf-8
import sys
sys.path.append('../../')
import pox.openflow.libopenflow_01 as of
import global_env as g
import table_config as tab_cfg



def add_time_slot () :
	#global tslot_config #dic
	#global tslot_unused # list
	#global tslot_used #dic

	print ("call the function add_time_slot()\n")

	msg = of.ofp_experimenter()
	msg.type = of.TIME_SLOT_CONFIG
	msg.tslot_cfg.cmd = 0 
	# todo: try to use 列表解析法	
	for i in g.tslot_config.keys():
		tag_info = of.sync_tag_info()
		tag_info.tag = g.tslot_config[i][0]
		tag_info.port = g.tslot_config[i][1]
		tag_info.tslot = g.tslot_unused[:g.tslot_config[i][2]]
		msg.tslot_cfg.data.append(tag_info)
		# updata the time slot used information
		g.tslot_used[i] = g.tslot_unused[:g.tslot_config[i][2]]
		g.tslot_unused = g.tslot_unused[g.tslot_config[i][2]:]

	msg.tslot_cfg.tag_num = len(msg.tslot_cfg.data) 
	
	return msg


def add_classfier_table (tname): 

	t = g.classfier_table[tname]

	msg = of.ofp_experimenter()
	msg.type = of.CLASSFIER_TABLE
	msg.ctab.type = of.SYNC_TABLE

	table = of.sync_flow_table()
	
	table.command = 0    #OFPTC_ADD
	table.tableName = tname
	table.tableId = t[0]
	table.tableType = t[1]
	table.tableSize = t[2]
	table.matchFieldNum = len(t[3])

	key_len = 0
	match_field = []
	for i in t[3]:
		ofmatch20 = of.ofp_match20()
		ofmatch20.fieldId = i
		ofmatch20.offset = g.field_config[i][0]
		ofmatch20.length = g.field_config[i][1]
		match_field.append(ofmatch20)
		key_len += ofmatch20.length

	table.matchFieldList = match_field
	table.keyLength = key_len

	msg.ctab.table = table

	return msg


def add_classfier_entry (tname, index):
	
	msg = of.ofp_experimenter()
	msg.type = of.CLASSFIER_TABLE
	msg.ctab.type = of.SYNC_ENTRY

	e = g.entry[tname, index]
	
	entry = of.sync_flow_entry()
		
	entry.cookie = 0
	entry.cookieMask = 0

	entry.priority = e[0]
	g.counter_id += 1
	entry.counterId = g.counter_id
	entry.index = index
	entry.tableId = g.classfier_table[tname][0]
	entry.tableType = g.classfier_table[tname][1]

	for i in e[1]:
		tempmatchx = of.ofp_matchx()
		tempmatchx.fieldId = i
		tempmatchx.offset = g.field_config[i][0]
		tempmatchx.length = g.field_config[i][1]

		tempmatchx.set_value(g.matchx[tname, index, i][0])
		tempmatchx.set_mask(g.matchx[tname, index, i][1])

		entry.matchx.append(tempmatchx)

	instruct = g.ins[tname, index]
	
	for i in instruct:
		print i[0]
		tempins = tab_cfg.insmap[i[0]](i[1])
		entry.instruction.append(tempins)
		
   	msg.ctab.entry = entry
	
	return msg


if __name__ == '__main__':
	print g.tslot_config
	test = add_time_slot()
	for i in test.tslot_cfg.data:
		print (i.tag, ":", i.port,i.tslot)
	
	print g.tslot_unused
	print g.tslot_used	

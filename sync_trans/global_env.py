#coding:utf-8

import sys
sys.path.append('../../')

import pox.openflow.libopenflow_01 as of

##############################################
# 这个文件用来配置一些全局资源，如时隙，流表
############################################## 
input_port = 1
output_port = 7

arp_dest_ip_offset = 38 * 8 + 3 * 8
arp_dest_ip_length = 1 * 8

counter_id = 0

# logic port
PTP = 0xffe0
ST_EDGE_IN = 0xffe1
ST_EDGE_OUT = 0xffe2
ST_CORE = 0xffe3
PIPELINE = 0xffe4



##############################################
# 流表-匹配域设置
##############################################

# match field format:{ field_id:[offset, length]}
field_config = { 0:[0, 32], 
		12:[0, 32], 
		47:[96, 16],# eth type: used by classfier table
		48:[22*8, 8], 
		49:[96, 32],# used by classfier to add flow tag
}

# table format:{'tname':[tid, type, tsize, [match_field]]
table = {'first table': [ 0, of.OF_MM_TABLE, 128, [47] ],
	'L2table': [ 1, of.OF_MM_TABLE, 128, [0]],
	'L3table': [ 2, of.OF_MM_TABLE, 128, [12, 48] ],

}

classfier_table = {
	'classfier_edge': [ 0xfd, of.OF_EM_TABLE, 128, [47] ],
	'classfier_core': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],
}


# entry format:{(tname, index):[priority, [matchx_id]}
entry = {('first table', 0): [ 0, [47] ],
	('first table', 1): [ 0,[47] ],
	('L2table', 0): [ 0, [0] ],
	('L2table', 1): [ 0, [0] ],
	('L3table', 0): [ 0, [12] ],
	('L3table', 1): [ 0, [12] ],
	('classfier_edge', 0): [ 0, [47] ],
	('classfier_edge', 1): [ 0, [47] ],

	('classfier_core', 2): [ 0, [0] ],
	('classfier_core', 3): [ 0, [0] ],

	('classfier_core', 4): [ 0, [0] ],
	('classfier_core', 5): [ 0, [0] ],
}

# matchx format: { ('tname', index, field_id):[value, mask]}
matchx = {('first table', 0, 47): [ '0806', 'ffff' ],
	('first table', 1, 47): [ '0800', 'ffff' ],
	('L2table', 0, 0): [ '00000001', '0000000f' ],
	('L2table', 1, 0): [ '00000007', '0000000f' ],
	('L3table', 0, 12): [ '00000001', '00000001' ],
	('L3table', 1, 12): [ '00000000', '00000001' ],
	('classfier_edge', 0, 47): [ 'ffff', 'ffff' ],# match tag
	('classfier_edge', 1, 47): [ '0806', 'ffff' ],# match ping

	('classfier_core', 0, 47): [ 'ffff', 'ffff' ],# match tag
	('classfier_core', 1, 47): [ '0806', 'ffff' ],# match ping

	('classfier_core', 2, 0): [ '00000001', 'ffffffff' ],# match input port
	('classfier_core', 3, 0): [ '00000007', 'ffffffff' ],# match input port

	('classfier_core', 4, 0): [ '00000001', 'ffffffff' ],# match input port
	('classfier_core', 5, 0): [ '00000007', 'ffffffff' ],# match input port
}

# insrtuction
'''
instruction format = {
		instruction: args format
		'gototable':  [next_table_id]
		'setoffset': [offsettype, [value]] ps: [0, [value]] or [1, [field_id]]
		'movoffset': [dir, valuetype, [value]] ps:[0,[value]] or [1, [field_id]]
		'applyaction': [act1, act2, act3,..] ps: act = [act name, act args]
		'addfield': [field_id] 
		'delfield':  [offset, length]
		'modfield': [field_id, increment]
		'setfield': [field_id, value, mask]
		'output':  [port_id]
		'drop': [reason]
		'calchecksum':  [store_pos_type, [args1], cal_pos_type, [args2]]
		'counter': [counterId]
}
'''


# instruction format{('tname', index): [ [ins1,[args]], [ins2,[args]], ...]}
ins = {('first table', 0) : [ ['gototable', [1]] ],
	('first table', 1) : [ ['gototable', [2]] ],
	('L2table', 0): [ ['applyaction',[ ['output', [7]] ]] ],
	('L2table', 1): [ ['applyaction',[ ['output', [1]] ]] ],
	('L3table', 0): [ ['applyaction',[ ['modfield', [48, -1]], ['calchecksum', [0,[192,16],0,[112,160]] ]]], 
			 ['gototable', [1]] ],
	('L3table', 1): [ ['applyaction',[ ['modfield', [48, -1]]] ], 
			 ['gototable', [1]] ],
	('classfier_edge', 1): [ ['applyaction', [ ['addfield',[49, 'ffff0001']], ['output', [ST_EDGE_OUT]] ]] ],
	('classfier_edge', 0): [ ['applyaction', [ ['output', [ST_EDGE_OUT]] ]] ],#match tag

	('classfier_core', 0): [ ['applyaction', [ ['output', [7]] ]] ],
	('classfier_core', 1): [ ['applyaction', [ ['drop', [0]] ]] ],
	
	('classfier_core', 2): [ ['applyaction', [ ['addfield',[49, 'ffff0007']], ['output', [ST_CORE]] ]] ],
	('classfier_core', 3): [ ['applyaction', [ ['addfield',[49, 'ffff0001']], ['output', [ST_CORE]] ]] ],
	
	('classfier_core', 4): [ ['applyaction', [ ['output', [7]] ]] ],
	('classfier_core', 5): [ ['applyaction', [ ['output', [1]] ]] ],
}



#########################################
# 同步传输使用以下资源
########################################

SYNC_MAX_TIME_SLOT_NUM = (100) #100
# format{ 'flow name': [tag, port, slot_num]}
tslot_config = {'flow1':[1,1,20], 'flow2':[2,3,30], 'flow3':[3,5,20], 'flow4':[7,7,20]}
tslot_unused = range(SYNC_MAX_TIME_SLOT_NUM)
tslot_used = tslot_config.copy()




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

SERVER_ST_STAT = 0xffe5
SERVER_PIPE_STAT = 0xffe6


ST_EDGE_IN_TEST = 0xffe7

ST_REPLY = 0xffe5
PIPE_REPLY = 0xffe6

##############################################
# 流表-匹配域设置
##############################################

# match field format:{ field_id:[offset, length]}
field_config = { 0:[0, 32], 
		12:[0, 32], 
		47:[96, 16],# eth type: ip, icmp, arp ...
		48:[22*8, 8], 
		49:[96, 32],# used by classfier to add flow tag
		55:[96, 48],# used by classfier to add flow tag
		50:[30*8, 32],# dest ip

		51:[64, 16],# sync reply

		52:[23 * 8, 8],#ip type: tcp or udp
		53:[36 * 8, 16],# udp dest port
}

# table format:{'tname':[tid, type, tsize, [match_field]]
table = {
	'pipe_edge1': [ 0, of.OF_MM_TABLE, 128, [0] ],

	'pipe_core0': [ 0, of.OF_MM_TABLE, 128, [0] ],
	'pipe_edge2': [ 0, of.OF_MM_TABLE, 128, [0] ],


	'pipe_edge3': [ 0, of.OF_MM_TABLE, 128, [0] ],
	
	'pipe_edge8': [ 0, of.OF_MM_TABLE, 128, [0] ],# used by test performence

	'pipe_edge9': [ 0, of.OF_MM_TABLE, 128, [0] ],#used by show time slot
	

	'pipe_sync_edge1': [ 0, of.OF_MM_TABLE, 128, [47] ],

	'pipe_sync_send1': [ 0, of.OF_MM_TABLE, 128, [47] ],
	'pipe_sync_reply1': [ 0, of.OF_MM_TABLE, 128, [47] ],
}

classfier_table = {
	'classfier_edge1': [ 0xfd, of.OF_EM_TABLE, 128, [0] ],

	'classfier_edge2': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],
	'classfier_core0': [ 0xfd, of.OF_EM_TABLE, 128, [47]],

	'classfier_edge3': [ 0xfd, of.OF_EM_TABLE, 128, [0] ],
	'classfier_edge4': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],
	'classfier_edge5': [ 0xfd, of.OF_EM_TABLE, 128, [47] ],
	'classfier_core1': [ 0xfd, of.OF_EM_TABLE, 128, [0] ],
	
	'classfier_edge6': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],
	'classfier_edge7': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],
	
	'classfier_edge8': [ 0xfd, of.OF_EM_TABLE, 128, [0] ],
	
	'classfier_edge9': [ 0xfd, of.OF_EM_TABLE, 128, [47, 52, 53] ],# used by show time slot
	
	'sync_reply1':[0xfd, of.OF_MM_TABLE, 128, [47]],
	'sync_send1':[0xfd, of.OF_MM_TABLE, 128, [47]],
	'sync_edge1':[0xfd, of.OF_MM_TABLE, 128, [47]],
	
	'new_st_edge': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],
	'new_st_core': [ 0xfd, of.OF_EM_TABLE, 128, [0, 47] ],

}


# entry format:{(tname, index):[priority, [matchx_id]}
entry = {
	('classfier_edge1', 0): [ 0, [0] ],
	('classfier_edge1', 1): [ 0, [0] ],
	('pipe_edge1', 0): [ 0, [0] ],
	('pipe_edge1', 1): [ 0, [0] ],
	('pipe_edge1', 2): [ 0, [0] ],
	('pipe_edge1', 3): [ 0, [0] ],
	
	('pipe_core0', 0): [ 0, [0] ],
	('pipe_core0', 1): [ 0, [0] ],

	('pipe_edge2', 0): [ 0, [0] ],
	('pipe_edge2', 1): [ 0, [0] ],
	
	('pipe_edge3', 0): [ 0, [0] ],
	('pipe_edge3', 1): [ 0, [0] ],


	('classfier_edge2', 0): [ 0, [47] ],
	('classfier_edge2', 1): [ 0, [0] ],
	
	('classfier_core0', 0): [ 0, [47] ],

	('classfier_edge3', 0): [ 0, [0] ],

	('classfier_edge4', 0): [ 0, [0] ],
	('classfier_edge5', 0): [ 0, [47] ],
	('classfier_core1', 0): [ 0, [0] ],
	
	('classfier_edge6', 0): [ 0, [0] ],
	('classfier_edge6', 1): [ 0, [0] ],

	('classfier_edge7', 0): [ 0, [0] ],
	
	('classfier_edge8', 0): [ 0, [0] ],
	('classfier_edge8', 1): [ 0, [0] ],
	('classfier_edge8', 2): [ 0, [0] ],
	('pipe_edge8', 0): [ 0, [0] ],

	('classfier_edge9', 0): [ 0, [47] ],
	('classfier_edge9', 1): [ 0, [47] ],
	('classfier_edge9', 2): [ 0, [47, 52, 53] ],
	('classfier_edge9', 3): [ 0, [47, 52, 53] ],
	('classfier_edge9', 4): [ 0, [47, 52, 53] ],
	('pipe_edge9', 0): [ 0, [0] ],
	('pipe_edge9', 1): [ 0, [0] ],


	('sync_reply1', 0):[0,[47]],
	('sync_reply1', 1):[0,[47]],
	('sync_reply1', 2):[0,[47]],

	('sync_send1', 0):[0,[47]],
	('sync_send1', 1):[0,[47]],
	('sync_send1', 2):[0,[47]],

	('sync_edge1', 0):[0,[47]],
	('sync_edge1', 1):[0,[47]],

	('pipe_sync_edge1', 0): [ 0, [47] ],

	('pipe_sync_send1', 0): [ 0, [47] ],
	('pipe_sync_reply1', 0): [ 0, [47] ],
	
	('new_st_edge', 0):[0,[47]],
	('new_st_edge', 1):[0,[47]],
	('new_st_edge', 2):[0,[47]],
	('new_st_edge', 3):[0,[47]],

	('new_st_core', 0):[0,[47]],
	('new_st_core', 1):[0,[47]],
	('new_st_core', 2):[0,[47]],


}


# matchx format: { ('tname', index, field_id):[value, mask]}
matchx = {
	
	('classfier_edge1', 0, 0): [ '00000001', 'ffffffff' ],# match input port
	('classfier_edge1', 1, 0): [ '0000000c', 'ffffffff' ],# match input port
	('pipe_edge1', 0, 0): [ '00000009', 'ffffffff' ],# match input port
	('pipe_edge1', 1, 0): [ '00000008', 'ffffffff' ],# match input port
	('pipe_edge1', 2, 0): [ '00000001', 'ffffffff' ],# match input port
	('pipe_edge1', 3, 0): [ '0000000c', 'ffffffff' ],# match input port


	('pipe_core0', 0, 0): [ '00000009', 'ffffffff' ],# match input porh
	('pipe_core0', 1, 0): [ '00000008', 'ffffffff' ],# match input porh

	('pipe_edge2', 0, 0): [ '00000012', 'ffffffff' ],# match input porh
	('pipe_edge2', 1, 0): [ '00000008', 'ffffffff' ],# match input porh
	
	('pipe_edge3', 0, 0): [ '00000009', 'ffffffff' ],# match input porh
	('pipe_edge3', 1, 0): [ '00000012', 'ffffffff' ],# match input porh

	('classfier_edge2', 0, 47): [ 'ffff', 'ffff' ],# match input port
	('classfier_edge2', 1, 0): [ '0000000c', 'ffffffff' ],# match input port

	('classfier_core0', 0, 47): [ 'ffff', 'ffff' ],# match input port
	

	
	('classfier_edge3', 0, 0): [ '0000000d', 'ffffffff' ],# match input
	
	('classfier_edge4', 0, 0): [ '0000000d', 'ffffffff' ],# match input port
	('classfier_edge5', 0, 47): [ 'ffff', 'ffff' ],# match input port
	
	('classfier_core1', 0, 0): [ '00000009', 'ffffffff' ],# match input port


	# test sync performance
	('classfier_edge6', 0, 0): [ '00000002', 'ffffffff' ],# match input port
	('classfier_edge6', 1, 0): [ '00000007', 'ffffffff' ],# match input port
	
	('classfier_edge7', 0, 0): [ '000000ff', 'ffffffff' ],# match input port
	
	('classfier_edge8', 0, 0): [ '00000008', 'ffffffff' ],# match input port
	('classfier_edge8', 1, 0): [ '00000009', 'ffffffff' ],# match input port
	('classfier_edge8', 2, 0): [ '00000013', 'ffffffff' ],# match input port
	('pipe_edge8', 0, 0): [ '00000012', 'ffffffff' ],# match input port
	
	('classfier_edge9', 0, 47):['ffff', 'ffff'],
	('classfier_edge9', 1, 47):['88f7', 'ffff'],
	('classfier_edge9', 2, 47): [ '0800', 'ffff' ],# match input port
	('classfier_edge9', 2, 52): [ '11', 'ff' ],# match udp
	('classfier_edge9', 2, 53): [ '300c', 'ffff' ],# match udp port
	('classfier_edge9', 3, 47): [ '0800', 'ffff' ],# match ip
	('classfier_edge9', 3, 52): [ '11', 'ff' ],# match udp
	('classfier_edge9', 3, 53): [ '300d', 'ffff' ],# match udp port
	('classfier_edge9', 4, 47): [ '0800', 'ffff' ],# match ip
	('classfier_edge9', 4, 52): [ '11', 'ff' ],# match udp
	('classfier_edge9', 4, 53): [ '300e', 'ffff' ],# match udp port
	('pipe_edge9', 0, 0): [ '00000002', 'ffffffff' ],# match input port
	('pipe_edge9', 1, 0): [ '00000003', 'ffffffff' ],# match input port
	
	('sync_reply1', 0, 47):['ffff', 'ffff'],
	('sync_reply1', 1, 47):['88f7', 'ffff'],
	('sync_reply1', 2, 47):['bbbb', 'ffff'],

	('sync_send1', 0, 47):['ffff', 'ffff'],
	('sync_send1', 1, 47):['88f7', 'ffff'],
	('sync_send1', 2, 47):['bbbb', 'ffff'],

	('sync_edge1', 0, 47):['ffff', 'ffff'],
	('sync_edge1', 1, 47):['88f7', 'ffff'],

	('pipe_sync_edge1', 0, 47): [ 'bbbb', 'ffff' ],

	('pipe_sync_reply1', 0, 47):['bbbb', 'ffff'],

	('pipe_sync_send1', 0, 47):['bbbb', 'ffff'],

	('new_st_edge', 0, 47):['bbbb', 'ffff'],
	('new_st_edge', 1, 47):['88f7', 'ffff'],
	('new_st_edge', 2, 47):['ffff', 'ffff'],
	('new_st_edge', 3, 47):['bbbb', 'ffff'],

	('new_st_core', 0, 47):['bbbb', 'ffff'],
	('new_st_core', 1, 47):['88f7', 'ffff'],
	('new_st_core', 2, 47):['ffff', 'ffff'],



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
ins = {
	('classfier_edge1', 0): [ ['applyaction', [ ['addfield',[49, 'ffff0001']], ['output', [ST_EDGE_IN]] ]] ],
	('classfier_edge1', 1): [ ['applyaction', [ ['addfield',[49, 'ffff0002']], ['output', [ST_EDGE_IN]] ]] ],
	('pipe_edge1', 0): [ ['applyaction', [ ['output', [8]] ]] ],#match
	('pipe_edge1', 1): [ ['applyaction', [ ['output', [9]] ]] ],#match
	('pipe_edge1', 2): [ ['applyaction', [ ['output', [12]] ]] ],#match
	('pipe_edge1', 3): [ ['applyaction', [ ['output', [1]] ]] ],#match

	('pipe_core0', 0): [ ['applyaction', [ ['output', [8]] ]] ],#match
	('pipe_core0', 1): [ ['applyaction', [ ['output', [9]] ]] ],#match

	('pipe_edge2', 0): [ ['applyaction', [ ['output', [8]] ]] ],#match
	('pipe_edge2', 1): [ ['applyaction', [ ['output', [18]] ]] ],#match


	('pipe_edge3', 0): [ ['applyaction', [ ['output', [18]] ]] ],#match
	('pipe_edge3', 1): [ ['applyaction', [ ['output', [9]] ]] ],#match


	('classfier_edge2', 0): [ ['applyaction', [ ['output', [ST_EDGE_OUT]] ]] ],#match tag
	('classfier_edge2', 1): [ ['applyaction', [ ['addfield',[49, 'ffff0002']], ['output', [ST_EDGE_IN]] ]] ],

	('classfier_core0', 0): [ ['applyaction', [ ['output', [ST_CORE]] ]] ],




	('classfier_edge3', 0): [ ['applyaction', [ ['addfield',[49, 'ffff0008']], ['output', [ST_CORE]] ]] ],
	('classfier_edge3', 1): [ ['applyaction', [ ['addfield',[49, 'ffff0002']], ['output', [ST_CORE]] ]] ],

	('classfier_edge4', 0): [ ['applyaction', [ ['addfield',[49, 'ffff0008']], ['output', [ST_EDGE_IN]] ]] ],
	('classfier_edge5', 0): [ ['applyaction', [ ['output', [ST_CORE]] ]] ],

	('classfier_core1', 0): [ ['applyaction', [ ['output', [ST_CORE]] ]] ],#match tag


	('classfier_edge6', 0): [ ['applyaction', [ ['addfield',[49, 'ffff0002']], ['output', [ST_EDGE_IN]] ]] ],
	('classfier_edge6', 1): [ ['applyaction', [ ['addfield',[49, 'ffff0007']], ['output', [ST_EDGE_OUT]] ]] ],

	('classfier_edge7', 0): [ ['applyaction', [ ['addfield',[49, 'ffff0002']], ['output', [ST_CORE]] ]] ],

	('classfier_edge8', 0): [ ['applyaction', [ ['output', [9] ]] ]],
	('classfier_edge8', 1): [ ['applyaction', [ ['addfield',[49, 'ffff0001']], ['output', [ST_EDGE_IN]] ]] ],
	('classfier_edge8', 2): [ ['applyaction', [ ['output', [18] ]] ]],
	
	('pipe_edge8', 0): [ ['applyaction', [ ['output', [19]] ]] ],#match

	('classfier_edge9', 0): [ ['applyaction', [ ['output', [SERVER_ST_STAT]] ]] ],
	('classfier_edge9', 1): [ ['applyaction', [ ['output', [PTP]] ]] ],
#	('classfier_edge9', 2): [ ['applyaction', [ ['output', [ST_EDGE_IN_TEST1]] ]] ],
#	('classfier_edge9', 3): [ ['applyaction', [ ['output', [ST_EDGE_IN_TEST2]] ]] ],
#	('classfier_edge9', 4): [ ['applyaction', [ ['output', [ST_EDGE_IN_TEST3]] ]] ],
	('classfier_edge9', 2): [ ['applyaction', [ ['addfield',[49, 'fffa0005']], ['output', [ST_EDGE_IN_TEST]] ]] ],
	('classfier_edge9', 3): [ ['applyaction', [ ['addfield',[49, 'fffa0006']], ['output', [ST_EDGE_IN_TEST]] ]] ],
	('classfier_edge9', 4): [ ['applyaction', [ ['addfield',[49, 'fffa0007']], ['output', [ST_EDGE_IN_TEST]] ]] ],
	
	('pipe_edge9', 0): [ ['applyaction', [ ['output', [3]] ]] ],#match
	('pipe_edge9', 1): [ ['applyaction', [ ['output', [2]] ]] ],#match


	('sync_reply1', 0): [ ['applyaction', [ ['output', [ST_REPLY]] ]] ],
	('sync_reply1', 1): [ ['applyaction', [ ['output', [PTP]] ]] ],
	('sync_reply1', 2): [ ['applyaction', [ ['output', [8]] ]] ],
	

	('sync_edge1', 0): [ ['applyaction', [ ['output', [ST_EDGE_IN]] ]] ],
	('sync_edge1', 1): [ ['applyaction', [ ['output', [PTP]] ]] ],

	('pipe_sync_edge1', 0): [ ['applyaction', [ ['output', [8]] ]] ],
	('pipe_sync_send1', 0): [ ['applyaction', [ ['output', [SERVER_PIPE_STAT]] ]] ],
	('pipe_sync_reply1', 0): [ ['applyaction', [ ['output', [PIPE_REPLY]] ]] ],

	('sync_send1', 0): [ ['applyaction', [ ['output', [SERVER_ST_STAT]] ]] ],
	('sync_send1', 1): [ ['applyaction', [ ['output', [PTP]] ]] ],
	('sync_send1', 2): [ ['applyaction', [ ['output', [SERVER_PIPE_STAT]] ]] ],
	
	('new_st_edge', 0): [ ['applyaction', [ ['output', [ST_EDGE_IN]] ]] ],
	('new_st_edge', 1): [ ['applyaction', [ ['output', [PTP]] ]] ],
	('new_st_edge', 2): [ ['applyaction', [ ['output', [ST_EDGE_IN]] ]] ],
	('new_st_edge', 3): [ ['applyaction', [ ['output', [ST_EDGE_OUT]] ]] ],

	('new_st_core', 0): [ ['applyaction', [ ['output', [ST_CORE]] ]] ],
	('new_st_core', 1): [ ['applyaction', [ ['output', [PTP]] ]] ],
	('new_st_core', 2): [ ['applyaction', [ ['output', [ST_CORE]] ]] ],


}

#########################################
# 同步传输使用以下资源
########################################

SYNC_MAX_TIME_SLOT_NUM = (100)
# format{ 'flow name': [tag, port, slot_num]}
tslot_edge1 = {'flow1':[1,12,2], 'flow2':[2,1,2]}
tslot_edge2 = {'flow1':[1,12,0], 'flow2':[2,18,100]}
tslot_core0 = {'flow1':[1,8,0], 'flow2':[2,9,0]}

tslot_edge3 = {'flow1':[8,7,99]}

tslot_edge4 = {'flow1':[8,18,50]}
tslot_edge5 = {'flow1':[8,6,50]}

tslot_core1 = {'flow1':[1,4,0], 'flow2':[6,7,0]}

tslot_edge6 = {'flow1':[1,2,30], 'flow2':[2,2,30], 'flow3':[3, 2, 30]}

tslot_send1 = {'flow1':[1,8,30], 'flow2':[2,8,30], 'flow3':[3, 8, 30], 'flow4':[4,8,30], 'flow5':[5,8,30]}
#tslot_sync_edge1 = {'flow1':[1,12,30], 'flow2':[2,12,30], 'flow3':[3, 12, 30]}
tslot_sync_edge1 = {'flow1':[1,8,30], 'flow2':[2,8,30], 'flow3':[3, 8, 30], 'flow4':[4,8,30], 'flow5':[5,8,30]}
#tslot_sync_edge1 = {'flow1':[1,8,100]}

tslot_reply1 = {'flow1':[1,1,1]}

#tslot_edge8 = { 'flow1':[1,8,99],'flow2':[2,3,1]}
tslot_edge8 = { 'flow1':[1,8,1], 'flow2':[2,8,100]}

tslot_edge9 = { 'flow1':[1,8,20], 'flow2':[2,8,20],'flow3':[5,2,5],'flow4':[6,2,5], 'flow5':[7,2,5]}

tslot_new_st_edge = {'flow1':[1,9,2]}#'flow2':[2,9,50]}
tslot_new_st_edge_out = {'flow1':[1,0,2]}
#tslot_new_st_send = {'flow1':[1,8,10], 'flow2':[2,8,10], 'flow3':[3, 8, 10], 'flow4':[4,8,10], 'flow5':[5,8,10]}
#tslot_new_st_core1 = {'flow1':[1,9,10], 'flow2':[2,9,10], 'flow3':[3, 9, 10], 'flow4':[4,9,10], 'flow5':[5,9,10]}
#tslot_new_st_core2 = {'flow1':[1,0,10], 'flow2':[2,0,10], 'flow3':[3, 0, 10], 'flow4':[4,0,10], 'flow5':[5,0,10]}
tslot_new_st_send = {'flow1':[1,8,20], 'flow2':[2,8,20]}
tslot_new_st_core1 = {'flow1':[1,9,20], 'flow2':[2,4,20]}
tslot_new_st_core2 = {'flow1':[1,0,20], 'flow2':[2,0,20]}

tslot_unused = range(SYNC_MAX_TIME_SLOT_NUM)

'''
tslot_unused = range(0,SYNC_MAX_TIME_SLOT_NUM,5)
tslot_unused += range(1,SYNC_MAX_TIME_SLOT_NUM,5)
tslot_unused += range(2,SYNC_MAX_TIME_SLOT_NUM,5)
tslot_unused += range(3,SYNC_MAX_TIME_SLOT_NUM,5)
	
tslot_unused += range(4,SYNC_MAX_TIME_SLOT_NUM,5)
'''



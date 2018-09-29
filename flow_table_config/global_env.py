# coding:utf-8

import sys
sys.path.append('../../')

import pox.openflow.libopenflow_01 as of
import read_rules as r


##############################################
# 用来配置全局资源，如常用的匹配域，流表
##############################################
mask_2byte = "ffff"
mask_4byte = "ffffffff"
mask_6byte = "ffffffffffff"

ethsrc = 6*8
ethdst = 0
mac_len = 48

eth_type = 12*8

arp_dip_no_vlan = 38 * 8
arp_dip_with_vlan = arp_dip_no_vlan + 16

ip_dip_no_vlan = 30*8
ip_sip_no_vlan = 26*8
ip_sip_with_vlan = ip_sip_no_vlan + 16
ip_dip_with_vlan = ip_dip_no_vlan + 16
ip_len = 32

ttl_no_vlan = 22*8
ttl_with_vlan = ttl_no_vlan + 16

checksum_no_vlan = 24*8
checksum_with_vlan = checksum_no_vlan + 16

counter_id = 0

# packet_in reason
TSND_MEASURE = 7


# logical port
OFPP_PKT_OUT      = 0x0fff #octeon work->word2.s.inport only 12bit

OFPP_MAX          = 0xff00
OFPP_PTP          = 0xffe0
OFPP_ST_EDGE_IN   = 0xffe1
OFPP_ST_EDGE_OUT  = 0xffe2
OFPP_STAT      = 0xffe3
OFPP_PIPELINE     = 0xffe4
OFPP_TSN          = 0xffe5
OFPP_TSND_REPLY   = 0xffe6

# Reserved OpenFlow Port (fake output "ports").
# Output port not set in action-set.used only in OXM_OF_ACTSET_OUTPUT.
OFPP_UNSET      = 0xfff7
'''
Send the packet out the input port.  This
reserved port must be explicitly used
in order to send back out of the inputport.
'''
OFPP_IN_PORT    = 0xfff8
'''
Submit the packet to the first flow table
NB: This destination port can only be
used in packet-out messages.
'''
OFPP_TABLE      = 0xfff9
OFPP_NORMAL     = 0xfffa  # Forward using non-OpenFlow pipeline.
OFPP_FLOOD      = 0xfffb  # Flood using non-OpenFlow pipeline.
OFPP_ALL        = 0xfffc  # All standard ports except input port.
OFPP_CONTROLLER = 0xfffd  # Send to controller. */
OFPP_LOCAL      = 0xfffe  # Local openflow "port". */
OFPP_ANY        = 0xffff
# Special value used in some requests when
#no port is specified (i.e. wildcarded).

null = 0


##############################################
# 流表-匹配域设置
##############################################

# match field format:{ 'field_name':[id, offset, length, mask]}
field_config = {'not_used' : null,# for file field map
		'input_port' : [0x0, 0, 32, mask_4byte],# input port
		'eth_type' : [47, eth_type, 16, mask_2byte],# eth type
		'dst_mac' : [48, ethdst, mac_len, mask_6byte],# dst mac
		'src_mac' : [49, ethsrc, mac_len, mask_6byte],# src mac
		'dip_no_vlan' : [50, ip_dip_no_vlan, ip_len, mask_4byte], #dst ip no vlan
}


########################################################
# 通过文件来添加表项，主要包括文件路径，分离规则
########################################################
# e.g: test_file = "../bgp20021201f.pref"
# map the file field with table field

# field : file_field_index
# if the file field not used, field_name = NOT_used
# if the mask field == -1,read mask not from file but from the field config
# flag: the value need to be changed the format
# filed = {field_name : value, mask, flag}
# e.g: file_field = {'eth_type':[0, 1, 'no_change','no_change'], 'not_used':null}

# e.g: split_rules = '/|\t'

# file = {file_name:[split_rules,file_field_map]}

# ins_args = {'ins' : [the file value index]}

# ****************** e.g : one file config  **********
file1 = "bgp20021201f.pref"
rule1 = '/|\t'
field_map1 = {'not_used': null,
		'dip_no_vlan': [0, 1, 'ip_addr_s', 'mask_num'],
}
ins_set1 = ['output']
ins_args1 = { 'output' : [2],
		}

flags = {'no_change': null,
	'ip_addr_s': r.list_ip_string_to_hex_string,#ip format:'192.168.8.42'
	'ip_int_s':r.list_ip_intnum_to_hex_string,#ip format:'77347772332'
	
	'mask_default':r.list_use_field_config_mask,# file not tell the mask
	'mask_num':r.list_generate_mask_string,# tell the bits of the mask: 24
	}
# ****************   all file config  *******************
files = {file1: [rule1, field_map1, ins_set1, ins_args1],
}


#############################################################
#  通过自己手动配置流表
#############################################################
###########  add  table  #######################

# table format:{'tname':[tid, type, tsize, [match_field]]
table = {'L3table':[0, of.OF_MM_TABLE, 128, ['dip_no_vlan']],
	'classifier':[0xfd, of.OF_MM_TABLE, 128, ['input_port']],
	'classifier1':[0xfd, of.OF_MM_TABLE, 128, ['dst_mac']],
	'classifier2':[0xfd, of.OF_MM_TABLE, 128, ['eth_type']],
}

# matchx format: { (field_name):[value, mask]}
# ps.value is hex string default
matchx1 = { 'dip_no_vlan' : [ '0800', mask_4byte ],
}

matchx2 = { 'input_port' : [ '0000', mask_4byte ],
}

matchx3 =[ {'dst_mac':['ffffffffffaa',mask_6byte]},#tsnd_req_flow
	{'dst_mac':['ffffffffffbb',mask_6byte]},#tsnd_reply_flow
]


matchx4 = [{ 'eth_type' : [ '88f7', mask_2byte ]},
	{'eth_type' : [ 'ffff', mask_2byte ]},
]



# insrtuction
'''
instruction format = {
		instruction: args format
		'gototable':  [next_table_id]
		'setoffset': [offsettype, [value]] ps: [0, [value]] or [1, [field_name]]
		'movoffset': [dir, valuetype, [value]] ps:[0,[value]] or [1, [field_name]]
		'tocp':[reasontype,app_act_flag,endflag,max_len,meta_pos,meta_len,reasonvalue/field_name] 
		'applyaction': [act1, act2, act3,..] ps: act = [act name, act args]
		'addfield': [field_name] 
		'delfield':  [offset, length]
		'modfield': [field_name, increment]
		'setfield': [field_name, value, mask]
		'output':  [port_id]
		'drop': [reason]
		'calchecksum':  [store_pos_type, [args1], cal_pos_type, [args2]]
		'counter': [counterId]
}
'''
# instruction format{(ins1:[args]}
ins_setx1 =[ {'gototable': [1],}
]

ins_setx2 =[ {'applyaction': [['output',[OFPP_TSN]], ]},
]

ins_setx3 =[ {'applyaction': [['output',[OFPP_TSND_REPLY]], ]},
	{'applyaction': [['output',[OFPP_TSN]], ]},
]

ins_setx4 =[ {'applyaction': [['output',[OFPP_PTP]], ]},
	{'applyaction': [['output',[OFPP_TSN]], ]},
	{'applyaction': [['output',[OFPP_STAT]], ]},
]


# entry format:{(tname, index):[priority, [matchx_field], [ins_sets]}
entry = {('L3table', 0): [10, matchx1, ins_setx1[0]],
	('classifier', 0): [0, matchx2, ins_setx2[0]],
	('classifier1', 0): [0, matchx3[0], ins_setx3[1]],
	('classifier1', 1): [0, matchx3[1], ins_setx3[0]],
	('classifier2', 0): [0, matchx4[0], ins_setx4[0]],
	('classifier2', 1): [0, matchx4[1], ins_setx4[1]],
	('classifier2', 2): [0, matchx4[1], ins_setx4[2]],
}

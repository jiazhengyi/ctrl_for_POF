#coding:utf-8

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

# logic port
PTP = 0xffe0
ST_EDGE_IN = 0xffe1
ST_EDGE_OUT = 0xffe2
ST_CORE = 0xffe3
PIPELINE = 0xffe4


null = 0

##############################################
# 流表-匹配域设置
##############################################

# match field format:{ 'field_name':[id, offset, length, mask]}
field_config = {'not_used' : null, # for file field map 
		'input_port' : [0xffff, 0, 32, mask_4byte],# input port 
		'eth_type' : [47, eth_type, 16, mask_2byte],# eth type
		'dst_mac' : [48, ethdst, mac_len, mask_6byte],# dst mac
		'src_mac' : [49, ethsrc, mac_len, mask_6byte],# src mac
		'dip_no_vlan' : [50, ip_dip_no_vlan, ip_len, mask_4byte], #dst ip no vlan
}


##########  add  table  #######################
# table format:{'tname':[tid, type, tsize, [match_field]]
table = {'L3table': [ 0, of.OF_MM_TABLE, 128, ['dip_no_vlan'] ],
}

########################################################
#通过文件来添加表项，主要包括文件路径，分离规则
########################################################
#e.g: test_file = "../bgp20021201f.pref"
# map the file field with table field

# field : file_field_index
# if the file field not used, field_name = NOT_used
# if the mask field == -1,read mask not from file but from the field config
# flag: the value need to be changed the format
# filed = {field_name : value, mask, flag} 
# e.g: file_field = {'eth_type':[0, 1, 'no_change','no_change'], 'not_used':null}

#e.g: split_rules = '/|\t'

#file = {file_name:[split_rules,file_field_map]}

#ins_args = {'ins' : [the file value index]}

#****************** e.g : one file config  **********
file1 = "bgp20021201f.pref"
rule1 = '/|\t'
field_map1 = {'not_used' : null,
		'dip_no_vlan' : [0, 1, 'ip_addr_s', 'mask_num'],
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
#****************   all file config  *******************
files = {file1: [rule1, field_map1, ins_set1, ins_args1],
}




#############################################################
#  通过自己手动配置流表
#############################################################
# matchx format: { ('tname', index, field_name):[value, mask]}
matchx1 = { 'dip_no_vlan' : [ '0800', mask_4byte ],
}


# insrtuction
'''
instruction format = {
		instruction: args format
		'gototable':  [next_table_id]
		'setoffset': [offsettype, [value]] ps: [0, [value]] or [1, [field_name]]
		'movoffset': [dir, valuetype, [value]] ps:[0,[value]] or [1, [field_name]]
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
ins_set1 = {'gototable': [1],
		}
	
# entry format:{(tname, index):[priority, [matchx_field], [ins_sets]}
entry = {('L3table', 0): [ 10, matchx1, ins_set1 ],
}



#!/usr/bin/python

import re
import socket
import struct
import global_env as g


#@param
#file:the file from which read value e.g:'/home/jiazy/pox_caozw/test.rules'
#field: the field need to be set value e.g:[0,47,48]
#split_rules:the file split rules e.g:',|.|;| |'

def read_field_value(file,split_rules):
	d_tem = {}

	f = open(file)
	line = f.readline()
	value = re.split(split_rules,line)
	n = len(value)
	#print n
	for i in range(0,n):# init d_tem
	 	d_tem[i] = []

	while line:
		i = 0
		#print value
		for v in value:
			d_tem[i].append(v)
			i = i+1

		line = f.readline()
		value = re.split(split_rules,line)

	f.close()

	return d_tem


def generate_mask_string(size, length):
	if 64 == size:
		i = (0xFFFFFFFFFFFFFFFF << (size - length)) & 0xFFFFFFFFFFFFFFFF
	elif 32 == size:
		i = (0xFFFFFFFF << (size - length)) & 0xFFFFFFFF
	elif 16 == size:
		i = (0xFFFF << (size - length)) & 0xFFFF
	elif 8 == size:
		i = (0xFF << (size - length)) & 0xFF
	else:
		assert 0
	return "%x" % i

def list_generate_mask_string(mask_list):
	list = []
	for i in mask_list:
		i = int(i,10)
		#print i
		list.append(generate_mask_string(32, i))
	return list

def change_ip_to_hex_string(ip_c):
	ip_n = int(socket.inet_aton(ip_c).encode('hex'),16)
	ret = hex(ip_n)
	
	#set_value(value),value need to be hex string without '0x'
	if ret.startswith('0x'):
		ret = ret[2:]

	return ret

def list_ip_string_to_hex_string(ip_list):
	list = []
	for i in ip_list:
		l = change_ip_to_hex_string(i)
		list.append(l)

	return list

def list_ip_intnum_to_hex_string(ip_list):
	list = []
	for i in ip_list:
		l = int(i,10)
		list.append(l)

	return list


def list_use_field_config_mask(fld_name, list_len):
	list = []
	mask = g.field_config[fld_name][2]
	for i in range(0,list_len):
		list.append(mask)

	return list


def change_value_format(flag, value):
	if 'no change' == flag:
		return value
	else:
		list = g.flags[flag](value)

	return list


def change_mask_format(fld, flag, mask):
	if 'no_change' == flag:
		return mask
	elif 'mask_default' == flag:
		list = g.flags[flag](fld, mask)
	else:
		list = g.flags[flag](mask)

	return list


def map_file_value_to_field_value(tname,file): # ret field value ,mask
	field_value = {}
	field_mask = {}
	field_map = {}
	fld_name_list = g.table[tname][3]
	file_value = read_field_value(file,g.files[file][0])
	field_map = g.files[file][1]

	for fld in field_map.keys():
		if 'not_used' == fld:
			continue
		else :
			v_key = field_map[fld][0] 
			m_key = field_map[fld][1]
			v_flag = field_map[fld][2]
			m_flag = field_map[fld][3]

			v_tem = file_value[v_key]
			m_tem = file_value[m_key]

			m_tem = change_mask_format(fld, m_flag, m_tem)
			v_tem = change_value_format(v_flag,v_tem)
	
			field_value[fld] = v_tem
			field_mask[fld] = m_tem

	return field_value, field_mask



if __name__ == '__main__':
	file = "bgp20021201f.pref"
	rules = '/|\t'
	file_field = {0:12,1:13,2:14}
	dic = read_field_value(file,rules)
	for k in dic[0]:
		print change_ip_to_hex_string(k)
	#print dic

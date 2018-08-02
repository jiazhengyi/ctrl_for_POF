
#coding:utf-8
import sys
sys.path.append('/home/jiazy/jiazy_pox_for_TSN/loop_IOA_NC_USTC_SUC/')

import pox.openflow.libopenflow_01 as of
import global_env as g
import table_config as tab_cfg
import re
import socket
import struct



def read_tsn_config(file):
	config_tem = {}

	f = open(file)
	line = f.readline()

	# jump comments 
	while line.startswith("#"):
		line = f.readline()

	# check file format
	value = line.split()
	n = len(value)
	if not line or n > 1:
		raise Exception, "invalid file format:no device ID at beginning!"
	
	# read config info
	while line:
		if 1 == n:# a new device config start
			devID = int(value[0])
			if config_tem.has_key(devID):
				print "write one dev config together"
			else:
				config_tem[devID] = []
		else:
			config_tem[devID].append(value)

		line = f.readline()
		value = line.split()
		n = len(value)

	f.close()

	return config_tem


def get_timeslot_list (tslot_str):
	tslot = tslot_str.split('|')
	#print tslot
	return tslot



#config format:['FlowID','PortID','TimeSlot','Queue']
def add_TSN_config (config) :# config can get by devID

	print ("call the function add_TSN_config()\n")

	flow_num = len(config)
	msg = of.ofp_experimenter()
	msg.type = of.TSN_CONFIG
	msg.tsn_cfg.cmd = 0 
	# todo: try to use 列表解析法
	for i in range(flow_num):
		flow_info = of.TSN_flow_info()
		flow_info.flowID = config[i][0]
		flow_info.port = config[i][1]
		flow_info.tslot = get_timeslot_list(config[i][2])
		flow_info.queue = config[i][3]
		msg.tsn_cfg.flow_info.append(flow_info)

	msg.tsn_cfg.flow_num = flow_num
	
	return msg


if __name__ == '__main__':
	
	file = "tsn_conf_file1"
	dic = {}
	try:
		dic = read_tsn_config(file)
	except Exception, err:
		print err

	print dic

	msg = add_TSN_config(dic[2])
	print msg


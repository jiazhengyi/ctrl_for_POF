
#coding:utf-8
import sys
sys.path.append('/home/naner/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of
import re
import socket
import struct


#default sending timeslot
send_tslot = 0

# TD-MIB format: { (sending_deviceID, sending_portID):[receiving_deviceID, receiving_portID, delay]}
TD_MIB ={}

#format:{deviceID:[streamID,portID,tslot,queueID]}
#queueID is unique in each device
init_flag = 1
config = {}

# TSN config file
conf_file = "/home/naner/jiazy/ctrl_for_POF/tsn_delay/tsn_conf_file1"

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
	#print config
	# todo: try to use 列表解析法
	for i in range(flow_num):
		flow_info = of.TSN_flow_info()
		flow_info.flowID = long(config[i][0],16)
		flow_info.port = int(config[i][1])
		flow_info.tslot = get_timeslot_list(config[i][2])
		flow_info.queue = int(config[i][3])
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


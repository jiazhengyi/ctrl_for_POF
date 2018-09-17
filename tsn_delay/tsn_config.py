
#coding:utf-8
import sys
sys.path.append('/home/naner/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of
import re
import socket
import struct
import tsn_handler as hlr

#default sending timeslot
send_tslot = 0
TSN_CYCLE = 100

# TD-MIB format: { sending_deviceID:[sending_portID,receiving_deviceID, receiving_portID, delay]}
TD_MIB ={}

#format:{deviceID:[streamID,portID,tslot,queueID]}
#queueID is unique in each device
config = {}

# TSN config file
conf_file = "/home/naner/jiazy/ctrl_for_POF/tsn_delay/tsn_conf_file1"


def init_TD_MIB(config):
	for dev in config.keys():
		c = config[dev]
		TD_MIB[dev] = []
		topy = []
		flow_num = len(c)
		for i in range(flow_num):
			port = int(c[i][3],16)
			if (port < 255):
				topy = [port,0,0,0]
				TD_MIB[dev].append(topy)
	return


def write_TD_MIB(tsnd_pkt):
	dev = tsnd_pkt.send_dev
	if (not TD_MIB.has_key(dev)):
		return;

	delay = (tsnd_pkt.rcvtime + TSN_CYCLE - tsnd_pkt.send_tslot)%TSN_CYCLE
	flag = 0
	for i in TD_MIB[dev]:
		if (tsnd_pkt.send_port == i[0]):
			if (flag == 1):
				raise Exception,\
				"send and recv port can only map one to one!"
			else :
				flag = 1
				i[1] = tsnd_pkt.recv_dev
				i[2] = tsnd_pkt.inport
				i[3] = delay
	return


def read_tsn_config(file):
	config_tem = {}
	#f = open(file)
	with open(file,'r')as f:
		line = f.readline()

		# jump comments
		while line.startswith("#"):
			line = f.readline()

		# check file format
		value = line.split()
		n = len(value)
		if not line or n > 1:
			raise Exception,\
			"invalid file format:no device ID at beginning!"
	
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

		#f.close()

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
		flow_info.port = int(config[i][3],16)
		flow_info.tslot = get_timeslot_list(config[i][2])
		flow_info.queue = int(config[i][4])
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

	tsnd_pkt = hlr.Tsnd_Packet();
	tsnd_pkt.rcvtime = 10
	tsnd_pkt.send_tslot = 20
	write_TD_MIB(tsnd_pkt)

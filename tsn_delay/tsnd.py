#coding:utf-8

import sys
sys.path.append('/home/naner/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of

import sync_trans.table_config as cfg
import tsn_config as tsn

log = core.getLogger()

def test_tsn_config(event):
	dpid = event.connection.dpid
	if (tsn.config.has_key(dpid)):
		msg = tsn.add_TSN_config(tsn.config[dpid])
		event.connection.send(msg)
	else :
		print ("the device:%d do not have config data!\n"%(dpid))


def test_tsn_switch (event):
	msg = cfg.add_classfier_table('classfier_edge')
	event.connection.send(msg)


	msg = cfg.add_classfier_entry('classfier_edge', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge', 1)
	event.connection.send(msg)


def _handle_ConnectionUp (event):
	if (tsn.init_flag):
		#init TSN global variant	
		tsn.config = tsn.read_tsn_config(tsn.conf_file)
		tsn.init_flag = 0
	else:
		pass

	test_tsn_config(event)	

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSN_CFG running.")

if __name__ == '__main__':
	event = 4
	if (tsn.init_flag):
		#init TSN global variant	
		tsn.config = tsn.read_tsn_config(tsn.conf_file)
		tsn.init_flag = 0
	else:
		pass
	print tsn.config

	test_tsn_config(event)	


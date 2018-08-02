
#coding:utf-8
'''
脚本用来配置同步传输的相应的信息
'''
from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

import sync_config as cfg
import table_config as tab_cfg
log = core.getLogger()

def test_time_slot_config(event): 
	msg = cfg.add_time_slot()
	event.connection.send(msg)

def test_edge_switch (event):
	msg = cfg.add_classfier_table('classfier_edge')
	event.connection.send(msg)


	msg = cfg.add_classfier_entry('classfier_edge', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge', 1)
	event.connection.send(msg)

def test_core_switch (event):

	msg = cfg.add_classfier_table('classfier_core')
	event.connection.send(msg)


	msg = cfg.add_classfier_entry('classfier_core', 2)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_core', 3)
	event.connection.send(msg)


def _handle_ConnectionUp (event):

	test_time_slot_config(event)
	
	if (event.connection.dpid < 2):
		print ("config edge switch: %d\n" %event.connection.dpid)
		test_edge_switch(event)
	else :
		print ("config core switch: %d\n" %event.connection.dpid)
		test_core_switch(event)

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSLOT_CFG running.")

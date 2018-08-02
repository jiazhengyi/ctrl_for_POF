
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
import global_env as g

log = core.getLogger()


def test_send_switch (event):
	'''
	msg = cfg.add_time_slot(g.tslot_new_st_send)
	event.connection.send(msg)


	msg = cfg.add_classfier_table('sync_send1')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_send1', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_send1', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_send1', 2)
	event.connection.send(msg)
	'''
	msg = cfg.add_time_slot(g.tslot_edge9)
	event.connection.send(msg)

	msg = tab_cfg.add_flow_table('pipe_edge9')
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_edge9', 0)
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_edge9', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('classfier_edge9')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge9', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge9', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge9', 2)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge9', 3)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge9', 4)
	event.connection.send(msg)


def test_reply_switch (event):
	msg = cfg.add_time_slot(g.tslot_new_st)
	event.connection.send(msg)


	msg = cfg.add_classfier_table('sync_reply1')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_reply1', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_reply1', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_reply1', 2)
	event.connection.send(msg)


def test_new_st_edge_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_new_st_edge)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('new_st_edge')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_edge', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_edge', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_edge', 2)
	event.connection.send(msg)



def test_new_st_edge_out_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_new_st_edge_out)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('new_st_edge')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_edge', 3)
	event.connection.send(msg)


def test_new_st_core1_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_new_st_core1)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('new_st_core')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_core', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_core', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_core', 2)
	event.connection.send(msg)

def test_new_st_core2_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_new_st_core2)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('new_st_core')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_core', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_core', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('new_st_core', 2)
	event.connection.send(msg)





def _handle_ConnectionUp (event):
	
	if ( 1 == event.connection.dpid ):
		print ("config send switch: %d\n" %event.connection.dpid)
		test_send_switch(event)
	if ( 2 == event.connection.dpid ):
		print ("config new_st_core1 switch: %d\n" %event.connection.dpid)
		test_new_st_core1_switch(event)
	if ( 3 == event.connection.dpid ):
		print ("config new_st_core2 switch: %d\n" %event.connection.dpid)
		test_new_st_core2_switch(event)

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSLOT_CFG running.")

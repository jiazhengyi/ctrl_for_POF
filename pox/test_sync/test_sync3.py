
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

def test_time_slot_config(event): 
	msg = cfg.add_time_slot()
	event.connection.send(msg)

def test_edge1_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_edge1)
	event.connection.send(msg)
	
	msg = tab_cfg.add_flow_table('pipe_edge1')
	event.connection.send(msg)

	msg = tab_cfg.add_flow_entry('pipe_edge1', 0)
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_edge1', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('classfier_edge1')
	event.connection.send(msg)
		

	msg = cfg.add_classfier_entry('classfier_edge1', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge1', 1)
	event.connection.send(msg)

def test_edge2_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_edge2)
	event.connection.send(msg)
	
	msg = tab_cfg.add_flow_table('pipe_edge2')
	event.connection.send(msg)

	msg = tab_cfg.add_flow_entry('pipe_edge2', 0)
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_edge2', 1)
	event.connection.send(msg)
	
	msg = cfg.add_classfier_table('classfier_edge2')
	event.connection.send(msg)


	msg = cfg.add_classfier_entry('classfier_edge2', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_edge2', 1)
	event.connection.send(msg)


def test_core1_switch (event):

	msg = cfg.add_time_slot(g.tslot_core1)
	event.connection.send(msg)

	msg = tab_cfg.add_flow_table('pipe_core1')
	event.connection.send(msg)

	msg = tab_cfg.add_flow_entry('pipe_core1', 0)
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_core1', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('classfier_core1')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_core1', 0)
	event.connection.send(msg)


def _handle_ConnectionUp (event):
	
	if ( 1 == event.connection.dpid ):
		print ("config edge1 switch: %d\n" %event.connection.dpid)
		test_edge1_switch(event)
	elif ( 2 == event.connection.dpid ):
		print ("config edge2 switch: %d\n" %event.connection.dpid)
		test_edge2_switch(event)
	elif ( 3 == event.connection.dpid ):
		print ("config core1 switch: %d\n" %event.connection.dpid)
		test_core1_switch(event)

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSLOT_CFG running.")

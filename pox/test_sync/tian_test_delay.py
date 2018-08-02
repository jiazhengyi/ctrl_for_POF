
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

def test_edge1_switch (event):
	
	msg = cfg.add_classfier_table('sync_send1')
	event.connection.send(msg)
		

	msg = cfg.add_classfier_entry('sync_send1', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_send1', 1)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_send1', 2)
	event.connection.send(msg)


'''
def test_edge2_switch (event):
	
	msg = cfg.add_time_slot(g.tslot_reply1)
	event.connection.send(msg)

	msg = tab_cfg.add_flow_table('pipe_sync_reply1')
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_sync_reply1', 0)
	event.connection.send(msg)



	msg = cfg.add_classfier_table('sync_reply1')
	event.connection.send(msg)


	msg = cfg.add_classfier_entry('sync_reply1', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('sync_reply1', 1)
	event.connection.send(msg)

	#msg = cfg.add_classfier_entry('sync_reply1', 2)
	#event.connection.send(msg)



def test_core0_switch (event):

	msg = cfg.add_time_slot(g.tslot_sync_edge1)
	event.connection.send(msg)

	msg = tab_cfg.add_flow_table('pipe_sync_edge1')
	event.connection.send(msg)
	msg = tab_cfg.add_flow_entry('pipe_sync_edge1', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('sync_edge1')
	event.connection.send(msg)
	msg = cfg.add_classfier_entry('sync_edge1', 0)
	event.connection.send(msg)
	msg = cfg.add_classfier_entry('sync_edge1', 1)
	event.connection.send(msg)
'''


def _handle_ConnectionUp (event):
	print ("config %d switch: send\n" %event.connection.dpid)
	test_edge1_switch(event)
'''
	if ( 1 == event.connection.dpid ):
		print ("config %d switch: send\n" %event.connection.dpid)
		test_edge1_switch(event)
	elif ( 2 == event.connection.dpid ):
		print ("config %d switch: reply\n" %event.connection.dpid)
		test_edge2_switch(event)
	elif ( 3 == event.connection.dpid ):
		print ("config %d switch: core0\n" %event.connection.dpid)
		test_core0_switch(event)
'''
def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("tianjj_test_caozw_delay running.")

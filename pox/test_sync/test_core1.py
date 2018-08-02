
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

def test_time_slot_config(event): 
	msg = cfg.add_time_slot()
	event.connection.send(msg)


def test_edge3_switch (event):

	msg = cfg.add_time_slot(g.tslot_core1)
	event.connection.send(msg)

	msg = cfg.add_classfier_table('classfier_core1')
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_core1', 0)
	event.connection.send(msg)


def _handle_ConnectionUp (event):
	
	if ( 2 == event.connection.dpid ):
		print ("config  switch: 2\n")
		test_edge3_switch(event)
	else:
		print ("the switch is : %d no configfile\n" %event.connection.dpid)

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSLOT_CFG running.")

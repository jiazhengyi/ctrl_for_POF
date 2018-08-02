
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


def test_edge9_switch (event):
	
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



def _handle_ConnectionUp (event):
	
	if ( 3 == event.connection.dpid ):
		print ("config edge9 switch: %d\n" %event.connection.dpid)
		test_edge9_switch(event)
def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSLOT_CFG running.")


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

import table_config as tab_cfg
log = core.getLogger()
import read_rules


# add_flow_entry (tname,index,pri,dict):
# add_flow_table (tname): 

def test_L2_L3_1(event):
	t1 = 'L3table'
	msg = tab_cfg.gen_add_table_msg(t1)
	event.connection.send(msg)
	
	msgs = tab_cfg.gen_add_entry_msgs_from_file(t1, g.file1)
	for m in msgs:
		event.connection.send(m)
	'''
def test_core_switch (event):
	msg = cfg.add_classfier_entry('classfier_core', 0)
	event.connection.send(msg)

	msg = cfg.add_classfier_entry('classfier_core', 1)
	event.connection.send(msg)
'''

def _handle_ConnectionUp (event):

	print ("test_L2_L3_1 running\n")
	test_L2_L3_1(event)
	

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

	log.info("test_TSLOT_CFG running.")


#coding:utf-8
'''
test_CONNECT
测试方案;
对于偶IP只对TTL域减1，不重新计算校验和，
对于奇数IP，对TTL域减1，重新计算校验和
现象;
ping 奇数IP，抓包看到TTL减1，但校验和出错
ping 偶数IP，抓包观察TTL减1。校验和正确
'''

from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

import table_config as cfg

log = core.getLogger()

def test_CONNECT(event):
	msg = cfg.add_flow_table('first table')
    	event.connection.send(msg)
	
	msg = cfg.add_flow_entry('first table', 0)
    	event.connection.send(msg)	
	msg = cfg.add_flow_entry('first table', 1)
    	event.connection.send(msg)
    	
	msg = cfg.add_flow_table('L2table')
	event.connection.send(msg)
	
	msg = cfg.add_flow_entry('L2table', 0)
    	event.connection.send(msg)
	msg = cfg.add_flow_entry('L2table', 1)
    	event.connection.send(msg)


	msg = cfg.add_flow_table('L3table')
    	event.connection.send(msg)
	
	msg = cfg.add_flow_entry('L3table', 0)
    	event.connection.send(msg)
	msg = cfg.add_flow_entry('L3table', 1)
    	event.connection.send(msg)

   
def _handle_ConnectionUp (event):
   	 test_CONNECT(event)


def launch ():
    	#ConnectionUp defined in __init__.py
    	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

    	log.info("test_CONNECT running.")

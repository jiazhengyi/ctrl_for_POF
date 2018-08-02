
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

import global_env as g

log = core.getLogger()

def test_CONNECT(event): 
    '''
    num = len(event.connection.phyports)
    msg = of.ofp_port_mod()
    portmessage = event.connection.phyports[g.input_port - 1]
    msg.setByPortState(portmessage)
    msg.desc.openflowEnable = 1
    event.connection.send(msg)
    '''
    ofmatch20_1 = of.ofp_match20()
    ofmatch20_1.fieldId = 0  #input port
    ofmatch20_1.offset = 0
    ofmatch20_1.length = 32

    ofmatch20_2 = of.ofp_match20()
    ofmatch20_2.fieldId = 47
    ofmatch20_2.offset = 96
    ofmatch20_2.length = 16

    ofmatch20_3 = of.ofp_match20()
    ofmatch20_3.fieldId = 12  #ip dest_ip
    ofmatch20_3.offset = 0
    ofmatch20_3.length = 32


    ###########################################
    #  table 0
    ###########################################
    msg = of.ofp_table_mod()

    msg.flowTable.matchFieldList.append(ofmatch20_2)
    msg.flowTable.command = 0    #OFPTC_ADD
    msg.flowTable.tableType = 0  #OF_MM_TABLE
    msg.flowTable.matchFieldNum = 1

    #msg.flowTable.matchFieldNum = len(msg.flowTable.matchFieldList)
    msg.flowTable.tableSize = 128
    msg.flowTable.tableId = 0
    msg.flowTable.tableName = "FirstEntryTable"
    msg.flowTable.keyLength = 16
    event.connection.send(msg)
   ##############################################################################
    #flow_mod 0-1
    ###############################################################################

    msg = of.ofp_flow_mod()
    msg.counterId = 1
    msg.cookie = 0
    msg.cookieMask = 0
    msg.tableId = 0
    msg.tableType = 0 #OF_MM_TABLE
    msg.priority = 0
    msg.index = 1

    tempmatchx = of.ofp_matchx()
    tempmatchx.fieldId = 47
    tempmatchx.offset = 96
    tempmatchx.length = 16
    tempmatchx.set_value("0800") #ipv4
    tempmatchx.set_mask("ffff")
    msg.matchx.append(tempmatchx)
   
    tempins=of.ofp_instruction_setpacketoffset()
    tempins.valueType = 0
    tempins.set_value = 14 # bytes
    msg.instruction.append(tempins)

    event.connection.send(msg)


   
def _handle_ConnectionUp (event):
    test_CONNECT(event)


def launch ():
    #ConnectionUp defined in __init__.py
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

    log.info("test_CONNECT running.")

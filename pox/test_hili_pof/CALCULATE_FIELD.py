
#coding:utf-8
'''
test_CALCULATE_FIELD
测试方案;
添加vlan。对于偶IP只对TTL域减1，不重新计算校验和，
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

def test_CALCULATE_FIELD(event): 
    '''
    num = len(event.connection.phyports)
    msg = of.ofp_port_mod()
    portmessage = event.connection.phyports[g.input_port - 1]
    msg.setByPortState(portmessage)
    msg.desc.openflowEnable = 1
    event.connection.send(msg)
    '''
    ofmatch20_1 = of.ofp_match20()
    ofmatch20_1.fieldId = 12
    #the last bit of dest IP
    ofmatch20_1.offset = 0
    ofmatch20_1.length = 32

    msg = of.ofp_table_mod()

    msg.flowTable.matchFieldList.append(ofmatch20_1)
    msg.flowTable.command = 0    #OFPTC_ADD
    msg.flowTable.tableType = 0  #OF_MM_TABLE
    msg.flowTable.matchFieldNum = 1

    #msg.flowTable.matchFieldNum = len(msg.flowTable.matchFieldList)
    msg.flowTable.tableSize = 128
    msg.flowTable.tableId = 0
    msg.flowTable.tableName = "FirstEntryTable"
    msg.flowTable.keyLength = 32
    event.connection.send(msg)

    ##############################################################################
    #flow_mod 0
    ###############################################################################

    msg = of.ofp_flow_mod()
    msg.counterId = 1
    msg.cookie = 0
    msg.cookieMask = 0
    msg.tableId = 0
    msg.tableType = 0 #OF_MM_TABLE
    msg.priority = 0
    msg.index = 0

    tempmatchx = of.ofp_matchx()
    tempmatchx.fieldId = 12
    tempmatchx.offset = 0
    tempmatchx.length = 32
    # even IP 
    tempmatchx.set_value("00")
    tempmatchx.set_mask("01")

    msg.matchx.append(tempmatchx)

    #instruction
    tempins = of.ofp_instruction_applyaction()

    action = of.ofp_action_modifyfield()
    action.matchfield.fieldId = 47
    action.matchfield.offset = 38 * 8 + 3 * 8
    action.matchfield.length = 8
    #  action.increment = -1 + 2**32
    action.increment = -1
    tempins.actionList.append(action)
  
    action = of.ofp_action_output()
    action.portId = g.output_port
    action.metadataOffset = 0
    action.metadataLength = 0
    action.packetOffset = 0    
    tempins.actionList.append(action)
    msg.instruction.append(tempins)

    event.connection.send(msg)

    ##############################################################################
    #flow_mod 1
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
    tempmatchx.fieldId = 12
    tempmatchx.offset = 0
    tempmatchx.length = 32
    #odd IP
    tempmatchx.set_value("01")
    tempmatchx.set_mask("01")

    msg.matchx.append(tempmatchx)

    tempins = of.ofp_instruction_applyaction()
    
    action = of.ofp_action_modifyfield()
    action.matchfield.fieldId = 47
    action.matchfield.offset = 38 * 8 + 3 * 8
    action.matchfield.length = 8
    #  action.increment = -1 + 2**32
    action.increment = -1
    tempins.actionList.append(action)

    action = of.ofp_action_calculatechecksum()
    action.checksumPosType = 0
    action.calcPosType = 1
    action.checksumPosition = 80 + 112
    action.checksumLength = 16
    action.calcStarPosition = 112
    action.calcLength = 160
    tempins.actionList.append(action) 

    action = of.ofp_action_output()
    action.portId = g.output_port
    action.metadataOffset = 0
    action.metadataLength = 0
    action.packetOffset = 0
    tempins.actionList.append(action)
    msg.instruction.append(tempins)

    event.connection.send(msg)


def _handle_ConnectionUp (event):
    test_CALCULATE_FIELD(event)


def launch ():
    #ConnectionUp defined in __init__.py
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

    log.info("test_CALCULATE_FIELD running.")

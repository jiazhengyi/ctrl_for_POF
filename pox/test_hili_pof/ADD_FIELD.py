#coding:utf-8
"""
test ADD_FIELD action 
测试方案;
添加vlan。对于偶IP不添加，对于奇数IP添加vlan
现象;
ping 奇数IP，抓包看到添加了valn,且vlan 号为15
ping 偶数IP，无添加。
"""

from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

import global_env as g

log = core.getLogger()

def test_ADD_FIELD(event): 
    '''
    num = len(event.connection.phyports)
    msg = of.ofp_port_mod()
    portmessage = event.connection.phyports[g.input_port - 1]
    msg.setByPortState(portmessage)
    msg.desc.openflowEnable = 1
    event.connection.send(msg)
    '''
    ofmatch20_1 = of.ofp_match20()
    ofmatch20_1.fieldId = 23
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
    tempmatchx.fieldId = 23
    tempmatchx.offset = 0
    tempmatchx.length = 32 
    # even IP 
    tempmatchx.set_value("00000000")
    tempmatchx.set_mask("00000001")

    msg.matchx.append(tempmatchx)

    #instruction
    tempins = of.ofp_instruction_applyaction()

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
    tempmatchx.fieldId = 23
    tempmatchx.offset = 0
    tempmatchx.length = 32
    #odd IP
    tempmatchx.set_value("00000001")
    tempmatchx.set_mask("00000001")

    msg.matchx.append(tempmatchx)

    tempins = of.ofp_instruction_applyaction()

    action = of.ofp_action_addfield()
    action.fieldId = 47
    action.fieldPosition = 96
    action.fieldLength = 32
    tempins.actionList.append(action)

    action=of.ofp_action_setfield()
    action.fieldSetting.fieldId=47 # vlan
    action.fieldSetting.offset=96
    action.fieldSetting.length=32
    action.fieldSetting.set_value("8001000f") # vlan id: 15
    action.fieldSetting.set_mask("ffffffff")
    tempins.actionList.append(action)

    action = of.ofp_action_output()
    action.portId = g.output_port
    action.metadataOffset = 0
    action.metadataLength = 0
    action.packetOffset = 0
    tempins.actionList.append(action)
    msg.instruction.append(tempins)

    event.connection.send(msg)


def _handle_Connection (event):
	#print ("in the %s !!!!!!!!!!!!!!!!\n"% __name__)
        test_ADD_FIELD(event)


def launch ():
    #ConnectionUp defined in __init__.py
    core.openflow.addListenerByName("ConnectionUp", _handle_Connection)

    log.info("test_ADD_FIELD running.")

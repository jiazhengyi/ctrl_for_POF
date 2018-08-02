
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
    #flow_mod 0-0
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
    tempmatchx.fieldId = 47
    tempmatchx.offset = 96
    tempmatchx.length = 16
    tempmatchx.set_value("0806")  #arp
    tempmatchx.set_mask("ffff")
    msg.matchx.append(tempmatchx)

 
    #instruction
   
    tempins=of.ofp_instruction_gototable()
    tempins.nextTableId=1
    msg.instruction.append(tempins)
    
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
   
    tempins=of.ofp_instruction_to_CP()
    tempins.reasonType = 0    #0: immediate value; 1: from field
    tempins.apply_action_flag = 0
    tempins.end_flag = 0
    tempins.max_len = 0xff 
    tempins.meta_pos = 0
    tempins.meta_len = 0
    tempins.reasonValue = 2
 
    msg.instruction.append(tempins)
  
    tempins=of.ofp_instruction_gototable()
    tempins.nextTableId= 2  
    msg.instruction.append(tempins)

    event.connection.send(msg)


    ###########################################
    #  table 1
    ###########################################
    msg = of.ofp_table_mod()

    msg.flowTable.matchFieldList.append(ofmatch20_1)
    msg.flowTable.command = 0    #OFPTC_ADD
    msg.flowTable.tableType = 0  #OF_MM_TABLE
    msg.flowTable.matchFieldNum = 1

    #msg.flowTable.matchFieldNum = len(msg.flowTable.matchFieldList)
    msg.flowTable.tableSize = 128
    msg.flowTable.tableId = 1
    msg.flowTable.tableName = "table1"
    msg.flowTable.keyLength = 32
    event.connection.send(msg)

    ##############################################################################
    #flow_mod 1-0
    ###############################################################################

    msg = of.ofp_flow_mod()
    msg.counterId = 1
    msg.cookie = 0
    msg.cookieMask = 0
    msg.tableId = 1  
    msg.tableType = 0 #OF_MM_TABLE
    msg.priority = 0
    msg.index = 0

    tempmatchx = of.ofp_matchx()
    tempmatchx.fieldId = 0
    tempmatchx.offset = 0
    tempmatchx.length = 32
    # even IP 
    tempmatchx.set_value("00000001")
    tempmatchx.set_mask("0000000f")

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
    #flow_mod 1-1
    ###############################################################################

    msg = of.ofp_flow_mod()
    msg.counterId = 1
    msg.cookie = 0
    msg.cookieMask = 0
    msg.tableId = 1 
    msg.tableType = 0 #OF_MM_TABLE
    msg.priority = 0
    msg.index = 1

    tempmatchx = of.ofp_matchx()
    tempmatchx.fieldId = 0
    tempmatchx.offset = 0
    tempmatchx.length = 32
    #odd IP
    tempmatchx.set_value("00000007")
    tempmatchx.set_mask("0000000f")

    msg.matchx.append(tempmatchx)

    #instructions
    tempins = of.ofp_instruction_applyaction()
    
    action = of.ofp_action_output()
    action.portId = 1
    action.metadataOffset = 0
    action.metadataLength = 0
    action.packetOffset = 0

    tempins.actionList.append(action)
    msg.instruction.append(tempins)

    event.connection.send(msg)


    ###################################################
    # table 2
    ##################################################
    msg = of.ofp_table_mod()

    msg.flowTable.matchFieldList.append(ofmatch20_3)
    msg.flowTable.command = 0    #OFPTC_ADD
    msg.flowTable.tableType = 0  #OF_MM_TABLE
    msg.flowTable.matchFieldNum = 1
    msg.flowTable.tableSize = 128
    msg.flowTable.tableId = 2 
    msg.flowTable.tableName = "table2"
    msg.flowTable.keyLength = 32
    event.connection.send(msg)
    
    ##############################################################################
    #flow_mod 2-0
    ###############################################################################

    msg = of.ofp_flow_mod()
    msg.counterId = 1
    msg.cookie = 0
    msg.cookieMask = 0
    msg.tableId = 2
    msg.tableType = 0 #OF_MM_TABLE
    msg.priority = 0
    msg.index = 0

    tempmatchx = of.ofp_matchx()
    tempmatchx.fieldId = 12
    tempmatchx.offset = 0
    tempmatchx.length = 32
    tempmatchx.set_value("00000001")  # even ip last bit
    tempmatchx.set_mask("00000001")

    msg.matchx.append(tempmatchx)
  
    #instruction
    '''
    tempins = of.ofp_instruction_applyaction()
    action=of.ofp_action_setfield()
    action.fieldSetting.fieldId=49 # ip offset 32
    action.fieldSetting.offset=32
    action.fieldSetting.length=16
    action.fieldSetting.set_value("ffaa")
    action.fieldSetting.set_mask("ffff")
    tempins.actionList.append(action)
    msg.instruction.append(tempins)
     
    tempins = of.ofp_instruction_applyaction()
    action = of.ofp_action_modifyfield()
    action.matchfield.fieldId = 48
    action.matchfield.offset = 26*8
    action.matchfield.length = 32
    action.increment = 1
    tempins.actionList.append(action)
    msg.instruction.append(tempins)
    '''   
    tempins = of.ofp_instruction_applyaction()
    
    action=of.ofp_action_setfield()
    action.fieldSetting.fieldId=47 # ip offset 32
    action.fieldSetting.offset=64
    action.fieldSetting.length=8
    action.fieldSetting.set_value("3f")
    action.fieldSetting.set_mask("ff")
    tempins.actionList.append(action)
 
    action=of.ofp_action_setfield()
    action.fieldSetting.fieldId=48 # ip offset 32
    action.fieldSetting.offset=80
    action.fieldSetting.length=16
    action.fieldSetting.set_value("dace")
    action.fieldSetting.set_mask("ffff")
    tempins.actionList.append(action)
    msg.instruction.append(tempins)
    
    tempins=of.ofp_instruction_gototable()
    tempins.nextTableId=1
    msg.instruction.append(tempins)
    
    event.connection.send(msg)

    ##############################################################################
    #flow_mod 2-1
    ###############################################################################

    msg = of.ofp_flow_mod()
    msg.counterId = 1
    msg.cookie = 0
    msg.cookieMask = 0
    msg.tableId = 2
    msg.tableType = 0 #OF_MM_TABLE
    msg.priority = 0
    msg.index = 1

    tempmatchx = of.ofp_matchx()
    tempmatchx.fieldId = 12
    tempmatchx.offset = 0
    tempmatchx.length = 32
    tempmatchx.set_value("00000000")  # odd ip last bit
    tempmatchx.set_mask("00000001")

    msg.matchx.append(tempmatchx)

    #instruction
    tempins = of.ofp_instruction_applyaction()
    action = of.ofp_action_modifyfield()
    action.matchfield.fieldId = 48
    action.matchfield.offset = 22 * 8
    action.matchfield.length = 8
    action.increment = -1
    tempins.actionList.append(action)

    action=of.ofp_action_setfield()
    action.fieldSetting.fieldId=49 # ip_checksum
    action.fieldSetting.offset=192
    action.fieldSetting.length=16
    action.fieldSetting.set_value("0000")
    action.fieldSetting.set_mask("ffff")
    tempins.actionList.append(action) 
    
    action = of.ofp_action_calculatechecksum()
    action.checksumPosType = 0
    action.calcPosType = 0
    action.checksumPosition = 80 + 112
    action.checksumLength = 16
    action.calcStarPosition = 112
    action.calcLength = 160
    tempins.actionList.append(action) 
    
    msg.instruction.append(tempins)
    
    tempins=of.ofp_instruction_gototable()
    tempins.nextTableId=1
  
    msg.instruction.append(tempins)

    event.connection.send(msg)


   
def _handle_ConnectionUp (event):
    test_CONNECT(event)


def launch ():
    #ConnectionUp defined in __init__.py
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

    log.info("test_CONNECT running.")

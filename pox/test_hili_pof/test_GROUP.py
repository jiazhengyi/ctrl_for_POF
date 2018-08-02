from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct



"""
test OUTPUT action 
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

log = core.getLogger()


  ##############################################################################
  #flow_mod 1
  ###############################################################################
def test_GROUP(event): 
  out_port = 2
  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[3]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  
   
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=1;
  ofmatch20_1.offset=0;
  ofmatch20_1.length=48;
  
  ###############################################################
  #table mode
  #################################################################
  
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=48
  event.connection.send(msg)

  ##########################################################################
  #group mode
  ##########################################################################

  msg = of.ofp_group_mod()
  msg.command = 0 #add
  msg.groupType = 0 #all
  msg.actionNum = 1 
  msg.groupId = 1
  msg.counterId = 2

  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=1
  action.fieldSetting.offset=0
  action.fieldSetting.length=48
  action.fieldSetting.set_value("00ff00abc0ff")
  action.fieldSetting.set_mask("ffffffffffff")
  msg.actions.append(action)

  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=1
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=0
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=1
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("00") #  null 
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()

  action=of.ofp_action_group()
  action.groupId=1
  
  tempins.actionList.append(action)
  
  action=of.ofp_action_output()
  action.portId=out_port
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)

    
def _handle_ConnectionUp (event):
    test_GROUP(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_GROUP running.")

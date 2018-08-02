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
def test_OUTPUT(event):
  print "we are really doing\n" 
  out_port = 1 
  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[1]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  
   
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=46;
  ofmatch20_1.offset=0;
  ofmatch20_1.length=48;
  
 
  msg = of.ofp_table_mod()  
  msg.flowTable.command=0 #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=48
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
  msg.index=1
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=46
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("0000") #  null 
  tempmatchx.set_mask("0000")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  '''
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=46
  action.fieldSetting.offset=0
  action.fieldSetting.length=48
  action.fieldSetting.set_value("0000000000ff")
  action.fieldSetting.set_mask("ffffffffffff")
  tempins.actionList.append(action)

  action=of.ofp_action_addfield()
  action.fieldId = 47
  action.fieldPosition = 96
  action.fieldLength = 16
  tempins.actionList.append(action)
  
  action=of.ofp_action_deletefield()
  action.tagPosition = 0
  action.tagLengthValueType = 0
  action.tagLengthValue = 48
  tempins.actionList.append(action)
  '''
  action=of.ofp_action_output()
  action.portId=out_port
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  tempins.actionList.append(action)
  
  msg.instruction.append(tempins)
  
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 2 
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.command =3 
  msg.counterId=1
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=0
  msg.index=1
  
  tempins=of.ofp_instruction_applyaction()
  
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=46
  action.fieldSetting.offset=0
  action.fieldSetting.length=48
  action.fieldSetting.set_value("0000000000ff")
  action.fieldSetting.set_mask("ffffffffffff")
  tempins.actionList.append(action)
  
  msg.instruction.append(tempins)
  
 
  event.connection.send(msg)
      
def _handle_ConnectionUp (event):
  print "we are adding flow table\n"  
  test_OUTPUT(event)
   

def launch ():
  print "in launch test output\n"
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_OUTPUT running.")

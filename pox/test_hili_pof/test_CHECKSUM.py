from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct



"""
test test_CHECKSUM action 
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

log = core.getLogger()


  ##############################################################################
  #flow_mod 1
  ###############################################################################
def test_CHECKSUM(event): 
  out_port = 2
  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[3]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[1]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)

  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=1;
  ofmatch20_1.offset=0;
  ofmatch20_1.length=48;
  
  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=-1;
  ofmatch20_2.offset=16;
  ofmatch20_2.length=8;

  ofmatch20_3 =of.ofp_match20()
  ofmatch20_3.fieldId=3;
  ofmatch20_3.offset=96;
  ofmatch20_3.length=16;

  ofmatch20_4 =of.ofp_match20() #TTL
  ofmatch20_4.fieldId=4;
  ofmatch20_4.offset=64;
  ofmatch20_4.length=8;

  ###############################################################################
  # table_mode 1
  ###############################################################################
  print " config flowTable 1"
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=16
  event.connection.send(msg)

   ##############################################################################
  #flow_mod 1-1
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
  tempmatchx.fieldId=3
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0800") #  null 
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)
  
  #instruction

  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 16
  tempins.indexType = 0
  tempins.packetOffset= 112
  tempins.indexValue = 0
  msg.instruction.append(tempins)
  event.connection.send(msg)

  ##############################################################################
  #flow_mod 1-2
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=2
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=0
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0806") #  null 
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)
  
  #instruction

  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId=1
  
  tempins.packetOffset=0
  tempins.matchList.append(ofmatch20_2)
  
  msg.instruction.append(tempins)
  event.connection.send(msg)
  ###############################################################################
  # table_mode 2
  ###############################################################################
  print " config flowTable 2"
  msg =of.ofp_table_mod()

  msg.flowTable.matchFieldList=[]
  msg.flowTable.matchFieldList.append(ofmatch20_2) #input_port 8bit

  msg.flowTable.command=0  #OFPTC_ADD
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=1
  msg.flowTable.tableName="Table 2"
  msg.flowTable.keyLength=8
  event.connection.send(msg)
  
 ##############################################################################
  #flow_mod 2-1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=3
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=1
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=0
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=-1
  tempmatchx.offset=16
  tempmatchx.length=8
  tempmatchx.set_value("02") #  null 
  tempmatchx.set_mask("ff")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  
  action=of.ofp_action_output()
  action.portId=4
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

  event.connection.send(msg)
 ##############################################################################
  #flow_mod 2-2
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=4
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=1
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=0
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=-1
  tempmatchx.offset=16
  tempmatchx.length=8
  tempmatchx.set_value("04") #  null 
  tempmatchx.set_mask("ff")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  
  action=of.ofp_action_output()
  action.portId=2
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

  event.connection.send(msg)

####################################################################
#table mode 3 DT table
####################################################################
  msg =of.ofp_table_mod()

  msg.flowTable.command=0  #OFPTC_ADD
  msg.flowTable.tableType=3 #OF_MM_TABLE
 
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="Table 3"
  msg.flowTable.keyLength= 0

  event.connection.send(msg)
  
 ##############################################################################
  #flow_mod 3-1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId= 5
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=3 #OF_LINER_TABLE
  msg.priority=0
  msg.index=0
 
  #instruction
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_modifyfield() #TTL
  action.matchfield.fieldId=4
  action.matchfield.offset=64
  action.matchfield.length=8
  action.increment=1
  tempins.actionList.append(action)

  action = of.ofp_action_calculatechecksum()
  action.checksumPosType = 0
  action.calcPosType = 0
  action.checksumPosition = 80
  action.checksumLength = 16
  action.calcStarPosition = 0
  action.calcLength = 80
  tempins.actionList.append(action) 
  msg.instruction.append(tempins)
    
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId=1
  tempins.packetOffset=0
  tempins.matchList.append(ofmatch20_1)
  msg.instruction.append(tempins)

  event.connection.send(msg)
    
def _handle_ConnectionUp (event):
    test_CHECKSUM(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_CHECKSUM running.")

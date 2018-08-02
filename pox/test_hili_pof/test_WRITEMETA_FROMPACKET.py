from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct



"""
test test_GOTO_TABLE action 
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

log = core.getLogger()


  ##############################################################################
  #flow_mod 1
  ###############################################################################
def test_WRITE_METADATA(event): 
  out_port = 2
  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[3]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  
   
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=1
  ofmatch20_1.offset=0
  ofmatch20_1.length=48
  
  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=-1
  ofmatch20_2.offset=24
  ofmatch20_2.length=8

  ###############################################################################
  # table_mode 1
  ###############################################################################
  print " config flowTable 1"
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
  tempins=of.ofp_instruction_writemetadatafrompacket()  #Total length to UDP_length
  tempins.metadataOffset= 24
  tempins.packetOffset = 0
  tempins.writeLength = 8
  msg.instruction.append(tempins)

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
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  print ofmatch20_2
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
  #flow_mod 1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=2
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=1
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=0
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=-1
  tempmatchx.offset=24
  tempmatchx.length=8
  tempmatchx.set_value("ff") #  null 
  tempmatchx.set_mask("ff")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  
  action=of.ofp_action_output()
  action.portId=out_port
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

  event.connection.send(msg)

    
def _handle_ConnectionUp (event):
    test_WRITE_METADATA(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_WRITE_METADATA running.")

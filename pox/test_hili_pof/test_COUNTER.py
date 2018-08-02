from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct



"""
test COUNTER action 
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

log = core.getLogger()


def test_COUNTER(event): 
  '''
  out_port = 2
  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[3]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  '''
   
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=47
  ofmatch20_1.offset=0
  ofmatch20_1.length=48
  
  ##############################################################################
  # table mode 1
  ###############################################################################
  
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
  
  '''
  ##############################################################################
  #counter_mod 1
  ###############################################################################
  msg =of.ofp_counter_mod()
  msg.counter.counterID=3
  msg.counter.command=0
  msg.counter.couterValue=0
  msg.counter.byteValue=0
  event.connection.send(msg)
  '''
  ##############################################################################
  #flow_mod 1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=1
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=1
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=47
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("00") #  null 
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  '''
  action=of.ofp_action_counter()
  action.counterId=1
  tempins.actionList.append(action)
  '''
  action=of.ofp_action_output()
  action.portId=2
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  tempins.actionList.append(action)
  
  msg.instruction.append(tempins)
  
  event.connection.send(msg)

def test_counter_mod (event):
  print "send counter mod msg\n"
  msg =of.ofp_counter_mod()
  msg.counter.counterID=1
  msg.counter.command=0
  msg.counter.couterValue=125
  msg.counter.byteValue=521
  event.connection.send(msg)

   
def _handle_ConnectionUp (event):
    test_COUNTER(event)
    test_counter_mod(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_COUNTER running.")

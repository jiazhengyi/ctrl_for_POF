from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct



"""
test test_DROP action 
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

import binascii
import global_env as g

log = core.getLogger()


  ##############################################################################
  #flow_mod 1
  ###############################################################################
def test_DROP(event): 
  num = len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[g.input_port - 1]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[g.output_port - 1]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)

  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=47;
  ofmatch20_2.offset=g.arp_dest_ip_offset;
  ofmatch20_2.length=g.arp_dest_ip_length;
  
  ##########################################################
  #table mode 1
  ##########################################################
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=g.arp_dest_ip_length
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
  msg.priority=1
  msg.index=0
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=47
  tempmatchx.offset=g.arp_dest_ip_offset
  tempmatchx.length=g.arp_dest_ip_length
  tempmatchx.set_value("01") #  null 
  tempmatchx.set_mask("01")
  msg.matchx.append(tempmatchx)
  
  tempins=of.ofp_instruction_writemetadatafrompacket()
  tempins.metadataOffset= 24
  # get dest IP
  tempins.packetOffset = 38 * 8
  tempins.writeLength = 4 * 8
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_applyaction()

  action=of.ofp_action_packetin()
  action.reason=0  
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

  event.connection.send(msg)
    
  ##############################################################################
  #flow_mod 1-2
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
  tempmatchx.fieldId=47
  tempmatchx.offset=g.arp_dest_ip_offset
  tempmatchx.length=g.arp_dest_ip_length
  tempmatchx.set_value("00") #  null 
  tempmatchx.set_mask("01")
  msg.matchx.append(tempmatchx)

  tempins=of.ofp_instruction_writemetadatafrompacket()
  tempins.metadataOffset= 24
  # get dest IP
  tempins.packetOffset = 38 * 8
  tempins.writeLength = 4 * 8
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_applyaction()
  
  action=of.ofp_action_output()
  action.portId=g.output_port
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

  event.connection.send(msg)
  
def _handle_ConnectionUp (event):
  print "Connection up."
  test_DROP(event)
   

def test_PacketIn(event):
  packet = event.parsed
  print "received PACKETIN packet, inport " + str(event.port)
  print "packet data: " + binascii.hexlify(packet.pack())
  print "parsed src mac: " + str(packet.src)
  print "parsed dst mac: " + str(packet.dst)
  print ""
  print "buffer ID: " + str(event.ofp.bufferId)
  
  msg=of.ofp_packet_out()

  msg._buffer_id = event.ofp.bufferId
  msg.inport = 2
  print "_buffer_ID send: " + str(msg._buffer_id)

  action=of.ofp_action_output()
  action.portId= 7 
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
 
  msg.actions.append(action)
 
  event.connection.send(msg)

def _handle_PacketIn (event):
    test_PacketIn(event)

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

  log.info("test_DROP running.")

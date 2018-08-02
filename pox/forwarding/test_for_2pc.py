# Copyright 2012 James McCauley
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX.  If not, see <http://www.gnu.org/licenses/>.
from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct



"""
Turns your complex OpenFlow switches into stupid hubs.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

log = core.getLogger()


  ##############################################################################
  #flow_mod 1
  ###############################################################################
def test_huawei_flow(event): 

  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[1]
  print portmessage.desc.portId
  print "test for two pc"
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable=1
  print msg.desc.portId
  event.connection.send(msg)
  
  '''
  msg = of.ofp_port_mod()
  msg.desc.portId=2
  msg.desc.openflowEnable=1
  event.connection.send(msg)
  '''
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=1;
  ofmatch20_1.offset=0;
  ofmatch20_1.length=48;
  
  
  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=2;
  ofmatch20_2.offset=48;
  ofmatch20_2.length=48;
  
  ofmatch20_3 =of.ofp_match20()
  ofmatch20_3.fieldId=3;
  ofmatch20_3.offset=96;
  ofmatch20_3.length=16;
  
  
  ofmatch20_4 =of.ofp_match20()
  ofmatch20_4.fieldId=4;
  ofmatch20_4.offset=208;
  ofmatch20_4.length=32;
  
  ofmatch20_4 =of.ofp_match20()
  ofmatch20_4.fieldId=4;
  ofmatch20_4.offset=112;
  ofmatch20_4.length=64;
  
  ofmatch20_5 =of.ofp_match20()
  ofmatch20_5.fieldId=5;
  ofmatch20_5.offset=176;
  ofmatch20_5.length=64;
  
  ofmatch20_6 =of.ofp_match20()
  ofmatch20_6.fieldId=6;
  ofmatch20_6.offset=240;
  ofmatch20_6.length=16;
  
  msg =of.ofp_table_mod()

    
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  msg.flowTable.matchFieldList.append(ofmatch20_4)
    
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 4
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=144
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
  tempmatchx.set_value("90b11c5a5298") #90:b1:1c:5a:52:98 
  #tempmatchx.set_mask("ffffffffffff")
  tempmatchx.set_mask("0")
  msg.matchx.append(tempmatchx)
  
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=2
  tempmatchx.offset=48
  tempmatchx.length=48
  tempmatchx.set_value("70f96d594742")  #70:f9:6d:59:47:42 
  tempmatchx.set_mask("0")
  #tempmatchx.set_mask("ffffffffffff")
  msg.matchx.append(tempmatchx)
  
  
  
  #need to new a ofp_matchx
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0800")
  #tempmatchx.set_mask("ffff")
  tempmatchx.set_mask("0")
  msg.matchx.append(tempmatchx) 
  
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=4
  tempmatchx.offset=208
  tempmatchx.length=32
  tempmatchx.set_value("da6afe68")
  #tempmatchx.set_mask("ffffffff")
  tempmatchx.set_mask("0")
  msg.matchx.append(tempmatchx) 
  
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  
  
  action=of.ofp_action_output()
  action.portId=4
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  
  '''    
  action=of.ofp_action_write()
  action.io_type=1
  '''
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)

    
def _handle_ConnectionUp (event):
    test_huawei_flow(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("Hub running2.")

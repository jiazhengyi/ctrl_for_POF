
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

"""
Turns your complex OpenFlow switches into stupid hubs.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
log = core.getLogger()

def test_for_ipv6(event):    
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
  
  ##############################################################################
  #table_mod 0
  ###############################################################################
  
  msg =of.ofp_table_mod()
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=144
  event.connection.send(msg)

  ##############################################################################
  #table_mod 1
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.tableId=0
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 3
  msg.flowTable.tableSize = 128
  msg.flowTable.keyLength=144
  msg.flowTable.tableName="CC"
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 1
  ###############################################################################
 
  msg=of.ofp_flow_mod()
  msg.counterId = 0
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 0 #OF_MM_TABLE
  msg.priority = 0
  msg.index = 0
  
  #matchx 1
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=1
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("000000000001")
  tempmatchx.set_mask("ffffffffffff")
  msg.matchx.append(tempmatchx)
  
  #instruction writemetadatafrompacket 7
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset= 32
  tempins.value= [1,1,1,1,1,1]
  tempins.writeLength = 48
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 16
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 0
  msg.instruction.append(tempins)

  event.connection.send(msg)
  
  
  ##############################################################################
  #flow_mod 2
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 4
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 3
  msg.priority = 0
  msg.index = 0
  
  
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_deletefield() 
  action.tagPosition = 0
  action.tagLengthValueType = 0
  action.tagLengthValue = 48
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  
  
  #instruction writemetadata 2
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=0
  tempins.writeLength=0
  tempins.value = []
  #msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_output()
  action.portId=0x10045
  action.metadataOffset=32
  action.metadataLength=48
  action.packetOffset=0
  tempins.actionList.append(action) 
  msg.instruction.append(tempins)
  
  event.connection.send(msg)
  
def _handle_ConnectionUp (event):
    test_for_ipv6(event)
    #test_query(event)
    
def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

  log.info("Hub running2.")

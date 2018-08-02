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

def test_all_flow(event):    
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
  #table_mod
  ###############################################################################
  
  msg =of.ofp_table_mod()
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=0 #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 2
  

  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=64
  event.connection.send(msg)
  #print ('Table_mod')
  #print (msg)
  #sleep(10)
  
  
  ##############################################################################
  #flow_mod 1
  ###############################################################################
 
  msg=of.ofp_flow_mod()
  msg.counterId = 1
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
  tempmatchx.set_value("00")
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx)
  
  #matchx 2
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("00")
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx) 
  
  #instruction gototable 1
  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId=0
  tempins.packetOffset=0
  #msg.instruction.append(tempins)
  
  #instruction gotodirecttable 8
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId=0
  tempins.indexType = 0
  tempins.packetOffset=0
  tempins.indexValue = 0
  #msg.instruction.append(tempins)
  
  #instruction meter 6
  tempins=of.ofp_instruction_meter()
  tempins.meterId=0
  #msg.instruction.append(tempins)
  
  #instruction writemetadata 2
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=0
  tempins.writeLength=0
  tempins.value = []
  #msg.instruction.append(tempins)
  
  #instruction writemetadatafrompacket 7
  tempins=of.ofp_instruction_writemetadatafrompacket()
  tempins.metadataOffset=0
  tempins.packetOffset=0
  tempins.writeLength = 48
  msg.instruction.append(tempins)
  
  #instruction conditionaljmp 9
  tempins=of.ofp_instruction_conditionaljmp()
  #msg.instruction.append(tempins)
  
  event.connection.send(msg)
  #sleep(10)
  #print ('Flow_mod_1')
  #print (msg)
  '''
  
  ##############################################################################
  #flow_mod 2
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=0
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=1
  msg.index=0
  
  #matchx 1
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=1
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("1111")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)
  
  #matchx 3
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("11")
  tempmatchx.set_mask("ff")
  msg.matchx.append(tempmatchx) 
  
  #instruction applyaction 4
  tempins=of.ofp_instruction_applyaction()
  #tempins.actionNum = 6
  
  ##action  output 0
  action=of.ofp_action_output()
  #tempins.actionList.append(action)
  
  ##action  setfield 1
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=0
  action.fieldSetting.offset=0
  action.fieldSetting.length=0
  action.fieldSetting.set_value("4437e64855db")
  action.fieldSetting.set_mask("ffffffffffff")
  #tempins.actionList.append(action)
  
  ##action  setfieldfrommetadata 2
  action=of.ofp_action_setfieldfrommetadata()
  action.fieldsetting = of.ofp_match20()
  action.metadataoffset = 0
  tempins.actionList.append(action)
  
  ##action  modifyfield 3
  action=of.ofp_action_modifyfield()
  action.matchfield = of.ofp_match20()
  action.increment = 0
  #tempins.actionList.append(action)
  
  ##action   addfield 4
  action=of.ofp_action_addfield()
  #tempins.actionList.append(action)
  
  ##action  deletefield 5
  action=of.ofp_action_deletefield()
  action.matchfield = of.ofp_match20()
  action.increment = 0
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  #instruction calculatefiled 10
  tempins=of.ofp_instruction_calculatefiled()
  #msg.instruction.append(tempins)
  
  #instruction movepacketoffset 11
  tempins=of.ofp_instruction_movepacketoffset()
  #msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_applyaction()
  #tempins.actionNum = 5
  
  ##action  calculatechecksum 6
  action=of.ofp_action_calculatechecksum()
  #tempins.actionList.append(action)
  #tempins.actionList.append(action)  
  ##action  group 7
  action=of.ofp_action_group()
  #tempins.actionList.append(action)
  
  ##action  drop 8
  action=of.ofp_action_drop()
  #tempins.actionList.append(action)
  
  ##action  packetin 9
  action=of.ofp_action_packetin()
  #tempins.actionList.append(action)
  
   ##action  counter 10
  action=of.ofp_action_counter()
  #tempins.actionList.append(action)
  #msg.instruction.append(tempins)
  event.connection.send(msg)  
  '''
    
def test_query(event):
    msg=of.ofp_queryall_request()
    event.connection.send(msg)
      
def _handle_ConnectionUp (event):
    test_all_flow(event)
    #test_query(event)
    
def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

  log.info("Hub running2.")

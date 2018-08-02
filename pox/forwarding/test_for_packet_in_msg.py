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


# These next two imports are common POX convention
from pox.core import core
import pox.openflow.libopenflow_01 as of


# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()

def test_huawei_flow(event): 
   
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
  
  ofmatch20_4=of.ofp_match20()
  ofmatch20_4.fieldId=4
  ofmatch20_4.offset=184
  ofmatch20_4.length=8
  
  ofmatch20_5 =of.ofp_match20()
  ofmatch20_5.fieldId=5;
  ofmatch20_5.offset=208;
  ofmatch20_5.length=32;
  
    
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  msg.flowTable.matchFieldList.append(ofmatch20_4)
  msg.flowTable.matchFieldList.append(ofmatch20_5)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 5
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=1
  msg.flowTable.tableName="SecondEntryTable"
  msg.flowTable.keyLength=152
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 1
  ###############################################################################
  index_list=range(0,10)
  name_list=["name0","name1","name2","name3","name4","name5","name6","name7","name8","name9"]
  for i in range(len(index_list)):
                            msg=of.ofp_flow_mod()
                            msg.counterId=1
                            msg.cookie=0
                            msg.cookieMask=0
                            msg.tableId=1
                            msg.tableType=0 #OF_MM_TABLE
                            msg.priority=index_list[i]
                            msg.index=index_list[i]
 
                            tempmatchx=of.ofp_matchx()
                            tempmatchx.fieldId=1
                            tempmatchx.offset=0
                            tempmatchx.length=48
                            tempmatchx.set_value("90b11c5a5299") #90:b1:1c:5a:52:99
                            tempmatchx.set_mask("ffffffffffff")
                            msg.matchx.append(tempmatchx)
  
  
                            tempmatchx=of.ofp_matchx()
                            tempmatchx.fieldId=2
                            tempmatchx.offset=48
                            tempmatchx.length=48
                            tempmatchx.set_value("90b11c5a618d")  #90:b1:1c:5a:61:8d 
                            tempmatchx.set_mask("ffffffffffff")
                            msg.matchx.append(tempmatchx)
  
  
  
                            #need to new a ofp_matchx
                            tempmatchx=of.ofp_matchx()
                            tempmatchx.fieldId=3
                            tempmatchx.offset=96
                            tempmatchx.length=16
                            tempmatchx.set_value("0800")
                            tempmatchx.set_mask("ffff")
                            msg.matchx.append(tempmatchx) 
  
  
                            tempmatchx=of.ofp_matchx()
                            tempmatchx.fieldId=4
                            tempmatchx.offset=184
                            tempmatchx.length=8
                            tempmatchx.set_value("01")
                            tempmatchx.set_mask("ffff")
                            msg.matchx.append(tempmatchx) 
  
  
                            tempmatchx=of.ofp_matchx()
                            tempmatchx.fieldId=5
                            tempmatchx.offset=208
                            tempmatchx.length=32
                            tempmatchx.set_value("c0a80103")
                            tempmatchx.set_mask("ffffffff")
                            msg.matchx.append(tempmatchx) 
  
  
                            #instruction
                            tempins=of.ofp_instruction_applyaction()
     
                            '''
                            action=of.ofp_action_write()
                            action.io_type =1
                            action.name_len=5
                            action.name=name_list[i]
                            action.enable_flag=1
                            '''
  
                            action=of.ofp_action_packetin()
                            action.reason=0
                            
                            tempins.actionList.append(action)
                            msg.instruction.append(tempins)
  
                            event.connection.send(msg)

# Handle messages the switch has sent us because it has no
# matching rule.
def _handle_PacketIn (event):
    test_huawei_flow(event)
    
def launch ():
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Handle PacketIn Msg running.")

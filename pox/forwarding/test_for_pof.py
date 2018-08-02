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

def set_data(hexstring):
#     if not isdigit(hexstring):
#         print ("hexstring can't change to ")
#         return 0
  packed =b""
  if (len(hexstring)%2):
    hexstring +='0'
  if (len(hexstring)>2048*2 ):
    hexstring=hexstring[:2048*2]
  value=[]
  for i in xrange(0,len(hexstring)/2):
    int_c=int(hexstring[i*2:i*2+2],16)    
        #print (hexstring[i*2:i*2+2]),int_c
    value.append(int_c)
  for i in value:
        packed += struct.pack("!B" ,i)  
  return packed

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
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 2
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=64
  event.connection.send(msg)
  
  #sleep(1)
  '''
  msg.flowTable.matchFieldList=[]
  msg.flowTable.matchFieldList.append(ofmatch20_4)
  msg.flowTable.matchFieldList.append(ofmatch20_5)
  msg.flowTable.matchFieldList.append(ofmatch20_6)
  msg.flowTable.tableId=1
  msg.flowTable.matchFieldNum = 3
  msg.flowTable.keyLength=144
  msg.flowTable.tableName="FP Parse Flow Table"
  event.connection.send(msg)
  #sleep(1)
  
  msg.flowTable.matchFieldList=[]
  msg.flowTable.matchFieldList.append(ofmatch20_4)

  msg.flowTable.tableId=0
  msg.flowTable.matchFieldNum = 1
  msg.flowTable.keyLength= 64
  msg.flowTable.tableName="FP Flow Table"  
  msg.flowTable.tableType=1  #OF_LPM_TABLE
  event.connection.send(msg)
  #sleep(1)
  '''
  ##############################################################################
  #flow_mod 1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId=3
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=1
  msg.index=0
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=1
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("00")
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx)
  
  #need to new a ofp_matchx
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0888")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx) 
  
  #instruction
  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId=1
  
  tempins.packetOffset=0
  tempins.matchList.extend([ofmatch20_4,ofmatch20_5,ofmatch20_6])
  
  msg.instruction.append(tempins)
  #print "Flow_mod 1"
  #print msg.pack().encode("hex")
  event.connection.send(msg)
  #log.info("Flow_Mod:succeed1")
  #sleep(1)
  '''
  ##############################################################################
  #flow_mod 2
  ###############################################################################
  msg=None
  msg=of.ofp_flow_mod()
  msg.counterId=2
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=1
  msg.tableType=0 #OF_MM_TABLE
  msg.priority=1
  msg.index=0
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=4
  tempmatchx.offset=112
  tempmatchx.length=64
  tempmatchx.set_value("00")
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx)
  
  #need to new a ofp_matchx
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=5
  tempmatchx.offset=176
  tempmatchx.length=64
  tempmatchx.set_value("00")
  tempmatchx.set_mask("00")
  msg.matchx.append(tempmatchx) 
  
    #need to new a ofp_matchx
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=6
  tempmatchx.offset=240
  tempmatchx.length=16
  tempmatchx.set_value("0901")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx) 
  
  #instruction
  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId=10
  
  tempins.packetOffset=0
  tempins.matchList.append(ofmatch20_4)
  
  msg.instruction.append(tempins)
  #print "Flow_mod 2"
  #print msg.pack().encode("hex")
  event.connection.send(msg)
  #log.info("Flow_Mod:succeed2")  
  #sleep(1)
  
  ##############################################################################
  #flow_mod 3
  ###############################################################################
  
  msg=None
  msg=of.ofp_flow_mod()
  msg.counterId=1
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=0
  msg.tableType=1  #OF_LPM_TABLE
  
  msg.priority=1
  msg.index=0
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=4
  tempmatchx.offset=112
  tempmatchx.length=64
  tempmatchx.set_value("1122334455667788")
  tempmatchx.set_mask("ffffffffffffffff")
  msg.matchx.append(tempmatchx)
  

  #instruction 1 
  tempins=of.ofp_instruction_applyaction()
  tempins.actionNum = 1
  
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=1
  action.fieldSetting.offset=0
  action.fieldSetting.length=48
  action.fieldSetting.set_value("0023243d92b4")
  action.fieldSetting.set_mask("ffffffffffff")
  #tempins.actionList.append(action)
  
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=2
  action.fieldSetting.offset=48
  action.fieldSetting.length=48
  action.fieldSetting.set_value("4437e64855db")
  action.fieldSetting.set_mask("ffffffffffff")
  tempins.actionList.append(action)
  
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=4
  action.fieldSetting.offset=112
  action.fieldSetting.length=64
  action.fieldSetting.set_value("0123456789abcdef")
  action.fieldSetting.set_mask("ffffffffffffffff")
  #tempins.actionList.append(action)
  
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=5
  action.fieldSetting.offset=176
  action.fieldSetting.length=64
  action.fieldSetting.set_value("1122334455667788")
  action.fieldSetting.set_mask("ffffffffffffffff")
  #tempins.actionList.append(action)
  
  msg.instruction.append(tempins)
  
  #instruction 2
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_output()
  action.portId=1
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  tempins.actionList.append(action)
  
  
  msg.instruction.append(tempins)
  #print "Flow_mod 3"
  #print msg.pack().encode("hex")
  event.connection.send(msg)  
  #log.info("Flow_Mod:succeed3")
  '''

def test_port_mod(event):  
    msg = of.ofp_port_mod()
    portmessage = event.connection.phyports[0]
    msg.setByPortState(portmessage)
    msg.desc.openflowEnable = 1 
    msg.reason = 2
    event.connection.send(msg)
     
def test_meter_mod(event):
    msg=of.ofp_meter_mod()  
    msg.command = 0
    msg.reverse = 0
    msg.rate = 200
    msg.meterID = 1
    event.connection.send(msg)

def test_group_mod(event):
    msg=of.ofp_group_mod()
    msg.command = 0
    msg.groupType = 0
    #msg.actionNum = 4
    msg.padding = 0
    msg.groupId = 1
    msg.counterId = 4
    msg.padding = 0    
    msg.actions = []
    
    action_1 = of.ofp_action_setfield()
    action_1.ofActionType = 1
    action_1.length = 44
    action_1.fieldSetting = of.ofp_matchx()
    action_1.fieldSetting.fieldId = 0
    action_1.fieldSetting.offset = 0
    action_1.fieldSetting.length = 0
    action_1.fieldSetting.padding = 0
    action_1.fieldSetting.set_value("00")
    action_1.fieldSetting.set_mask("00")
    msg.actions.append(action_1)
    
    
    
    
    
    action_2 = of.ofp_action_addfield()
    action_2.length = 20
    action_2.fieldId = 0
    action_2.fieldPosition = 0
    action_2.fieldLength = 0
    action_2.set_fieldValue("00")
    msg.actions.append(action_2)
    
    action_3 = of.ofp_action_group()
    action_3.length = 12
    action_3.groupId = 0
    msg.actions.append(action_3)
    
    action_4 = of.ofp_action_drop()
    action_4.length = 12
    action_4.reason = 0
    msg.actions.append(action_4)
    
    event.connection.send(msg)

'''    
def test_counter_request(event):
  msg = of.ofp_counter_request() 
  msg.counter = of.ofp_counter()
  msg.counter.command = 3
  msg.counter.reverse = 0
  msg.counter.counterID = 0
  msg.counter.value = 0 
  event.connection.send(msg)
''' 
    
def test_packet_out(event):
    msg=ofp_packet_out()
    msg.actions.append(ofp_action_output(portId = 1))
    msg.data=set_data("20dce69c54e868172904afe2080045000028181840008006f474ac100164da3a669410160050c7061e660264875f5010ff3742c30000")
    msg._data=set_data("20dce69c54e868172904afe2080045000028181840008006f474ac100164da3a669410160050c7061e660264875f5010ff3742c30000")
    msg.inPort=1 
    #msg.bufferId=0
    #print msg.pack().encode("hex")
    event.connection.send(msg)
    
def test_query_all(event):
    msg=of.ofp_queryall_request()
    event.connection.send(msg)
    
def _handle_ConnectionUp (event):
    test_huawei_flow(event)
    #test_port_mod(event)
    #test_meter_mod(event)
    #test_group_mod(event)
    #test_query_all(event)
    #test_packet_out(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

  log.info("Hub running2.")

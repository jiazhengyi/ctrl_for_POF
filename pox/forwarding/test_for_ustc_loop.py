
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
#######################################################################
#test for ustc single loop,
#10043 input(pc) ---VxLanEncap--> 10045 output(switch) ->10049 input(switch) ---VxLanDecap---> 10047 output(pc)         
#######################################################################
def test_for_single_vxlan(event):    
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=0
  ofmatch20_1.offset=0
  ofmatch20_1.length=48
  
  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=-1
  ofmatch20_2.offset=272
  ofmatch20_2.length=32
  
  ofmatch20_3 =of.ofp_match20()
  ofmatch20_3.fieldId= -1
  ofmatch20_3.offset= 336
  ofmatch20_3.length= 16
  
  ofmatch20_4 =of.ofp_match20()
  ofmatch20_4.fieldId= -1
  ofmatch20_4.offset= 160
  ofmatch20_4.length= 16
  
  ofmatch20_5 =of.ofp_match20()
  ofmatch20_5.fieldId= 2
  ofmatch20_5.offset= 96
  ofmatch20_5.length=16
  
  ofmatch20_6 =of.ofp_match20()
  ofmatch20_6.fieldId=7
  ofmatch20_6.offset=184
  ofmatch20_6.length=8
  
  ofmatch20_7 =of.ofp_match20()
  ofmatch20_7.fieldId= 12
  ofmatch20_7.offset= 288
  ofmatch20_7.length=16
  
  ##############################################################################
  #table_mod 0
  ###############################################################################
  
  msg =of.ofp_table_mod()
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  #msg.flowTable.matchFieldList.append(ofmatch20_3)
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=48
  event.connection.send(msg)

  ##############################################################################
  #table_mod 16
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.tableId=0
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 3
  msg.flowTable.tableSize = 128
  msg.flowTable.keyLength= 0
  msg.flowTable.tableName="VNI"
  event.connection.send(msg)
  
  ##############################################################################
  #table_mod 17
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.tableId=1
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 3
  msg.flowTable.tableSize = 128
  msg.flowTable.keyLength= 0
  msg.flowTable.tableName="VxLanEncap"
  event.connection.send(msg)
  
   ##############################################################################
  #table_mod 8
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.tableId=0
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 1
  msg.flowTable.tableSize = 100
  msg.flowTable.keyLength= 32
  msg.flowTable.tableName="FIB"
  event.connection.send(msg)
  
   ##############################################################################
  #table_mod 20
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.tableId=4
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 3
  msg.flowTable.tableSize = 100
  msg.flowTable.keyLength= 0
  msg.flowTable.tableName="FIB_DT"
  event.connection.send(msg)
  
   ##############################################################################
  #table_mod 18
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.tableId=2
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 3
  msg.flowTable.tableSize = 100
  msg.flowTable.keyLength= 0
  msg.flowTable.tableName="EPAT"
  event.connection.send(msg)
  
  ##############################################################################
  #table_mod 10
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.matchFieldList.append(ofmatch20_5)
  msg.flowTable.tableId=0
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 2
  msg.flowTable.tableSize = 100
  msg.flowTable.keyLength= 16
  msg.flowTable.tableName="L2PA"
  event.connection.send(msg)
  
  
   ##############################################################################
  #table_mod 11
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.matchFieldList.append(ofmatch20_6)
  msg.flowTable.matchFieldList.append(ofmatch20_7)
  msg.flowTable.tableId=1
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 2
  msg.flowTable.tableSize = 100
  msg.flowTable.keyLength= 24
  msg.flowTable.tableName="L3PA"
  event.connection.send(msg)
  
   ##############################################################################
  #table_mod 19
  ###############################################################################
  msg =of.ofp_table_mod()
  msg.flowTable.tableId=3
  msg.flowTable.command=0 #OFPTC_ADD
  msg.flowTable.tableType = 3
  msg.flowTable.tableSize = 100
  msg.flowTable.keyLength= 0
  msg.flowTable.tableName="VxLanDecap"
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 0-0
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
  tempmatchx.fieldId=0
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("000000000001")
  tempmatchx.set_mask("ffffffffffff")
  msg.matchx.append(tempmatchx)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 16
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 0
  msg.instruction.append(tempins)

  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 0-1
  ###############################################################################
 
  msg=of.ofp_flow_mod()
  msg.counterId = 1
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0  
  msg.tableType = 0 #OF_MM_TABLE
  msg.priority = 0
  msg.index = 1
  
  #matchx 1
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=0
  tempmatchx.offset=0
  tempmatchx.length=48
  tempmatchx.set_value("112233445566")
  tempmatchx.set_mask("ffffffffffff")
  msg.matchx.append(tempmatchx)

  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId= 10
  tempins.packetOffset=0
  tempins.matchList.extend([ofmatch20_5])
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 16-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 2
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 3
  msg.priority = 0
  msg.index = 0
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=240
  tempins.set_value('03030303')
  tempins.writeLength = 32
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=272
  tempins.set_value('04040404')
  tempins.writeLength = 32
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset= 400
  tempins.set_value('000001')
  tempins.writeLength = 24
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 17
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 0
  msg.instruction.append(tempins)
  
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 17-0
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId = 3
  msg.cookie = 1
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 3
  msg.priority = 0
  msg.index = 0
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=128
  tempins.set_value('0800')
  tempins.writeLength = 16
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=144
  tempins.set_value('4500')
  tempins.writeLength = 16
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=208
  tempins.set_value('4011')
  tempins.writeLength = 16
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=320
  tempins.set_value('12b5')
  tempins.writeLength = 16
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 17
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 1
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 17-1
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId = 4
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 1
  msg.tableType = 3
  msg.priority = 0
  msg.index = 1
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=368
  tempins.set_value('80')
  tempins.writeLength = 8
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadatafrompacket()
  tempins.metadataOffset= 336
  tempins.packetOffset = 128
  tempins.writeLength = 16
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_writemetadatafrompacket()
  tempins.metadataOffset= 160
  tempins.packetOffset = 128
  tempins.writeLength = 16
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 17
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 2
  msg.instruction.append(tempins)
  event.connection.send(msg)

  ##############################################################################
  #flow_mod 17-2
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId = 5
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 1
  msg.tableType = 3
  msg.priority = 0
  msg.index = 2
  
  tempins=of.ofp_instruction_calculatefiled()
  tempins.calcType = 0
  tempins.src_valueType = 0    #0: use srcField_Value; 1: use srcField;
  tempins.des_field = ofmatch20_3
  tempins.src_value = 30
  #tempins.src_field = ofp_match20()
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_calculatefiled()
  tempins.calcType = 0
  tempins.src_valueType = 0    #0: use srcField_Value; 1: use srcField;
  tempins.des_field = ofmatch20_4
  tempins.src_value = 50
  #tempins.src_field = ofp_match20()
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 17
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 3
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 17-3
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId = 6
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 1
  msg.tableType = 3
  msg.priority = 0
  msg.index = 3
  
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=304
  tempins.set_value('04d2')
  tempins.writeLength = 16
  msg.instruction.append(tempins)
    
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 17
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 4
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 17-4
  ###############################################################################
  
  msg=of.ofp_flow_mod()
  msg.counterId = 7
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 1
  msg.tableType = 3
  msg.priority = 0
  msg.index = 4
  
  tempins=of.ofp_instruction_applyaction()
  action = of.ofp_action_calculatechecksum()
  action.checksumPosType = 1
  action.calcPosType = 1
  action.checksumPosition = 224
  action.checksumLength = 16
  action.calcStarPosition = 144
  action.calcLength = 160
  tempins.actionList.append(action) 
  msg.instruction.append(tempins)
    
  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId= 8
  tempins.packetOffset=0
  tempins.matchList.extend([ofmatch20_2])
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  
  ##############################################################################
  #flow_mod 8-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 8
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 1
  msg.priority = 0
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId= -1
  tempmatchx.offset= 272
  tempmatchx.length= 32
  tempmatchx.set_value("00000000")
  tempmatchx.set_mask("00000000")
  msg.matchx.append(tempmatchx)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 20
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 0
  msg.instruction.append(tempins)

  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 20-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 9
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 4
  msg.tableType = 3
  msg.priority = 0
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=32
  tempins.set_value('112233445566')
  tempins.writeLength = 48
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 18
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 0
  msg.instruction.append(tempins)

  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 18-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 10
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 2
  msg.tableType = 3
  msg.priority = 0
  
  tempins=of.ofp_instruction_writemetadata()
  tempins.metaDataOffset=80
  tempins.set_value('665544332211')
  tempins.writeLength = 48
  msg.instruction.append(tempins)
  
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_output()
  action.portId=0x10045
  action.metadataOffset=32
  action.metadataLength=400
  action.packetOffset=0
  tempins.actionList.append(action) 
  msg.instruction.append(tempins)
  
  event.connection.send(msg)
  
  
  ##############################################################################
  #flow_mod 10-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 6
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 2
  msg.priority = 0
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=2
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0800")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)
  
  tempins=of.ofp_instruction_gototable()
  tempins.nextTableId= 11
  tempins.packetOffset=0
  tempins.matchList.extend([ofmatch20_6,ofmatch20_7])
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  
  ##############################################################################
  #flow_mod 11-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 6
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 1
  msg.tableType = 2
  msg.priority = 0
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=7
  tempmatchx.offset=184
  tempmatchx.length=8
  tempmatchx.set_value("11")
  tempmatchx.set_mask("ff")
  msg.matchx.append(tempmatchx)
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=12
  tempmatchx.offset= 288
  tempmatchx.length=16
  tempmatchx.set_value("12b5")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)
  
  tempins=of.ofp_instruction_gotodirecttable()
  tempins.nextTableId = 19
  tempins.indexType = 0
  tempins.packetOffset= 0
  tempins.indexValue = 0
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  ##############################################################################
  #flow_mod 19-0
  ###############################################################################
  msg=of.ofp_flow_mod()
  msg.counterId = 6
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 3
  msg.tableType = 3
  msg.priority = 0
  
  ''' 
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_output()
  action.portId=0x10047
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  tempins.actionList.append(action) 
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  '''
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_deletefield()
  action.tagPosition = 0
  action.tagLengthValueType = 0
  action.tagLengthValue = 128
  tempins.actionList.append(action)
  tempins.actionList.append(action)
  tempins.actionList.append(action)
  
  action=of.ofp_action_deletefield()
  action.tagPosition = 0
  action.tagLengthValueType = 0
  action.tagLengthValue = 16
  tempins.actionList.append(action)
  
  action=of.ofp_action_output()
  action.portId=0x10047
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  tempins.actionList.append(action) 
  msg.instruction.append(tempins)
  event.connection.send(msg)
  
  
def _handle_ConnectionUp (event):
    test_for_single_vxlan(event)
    #test_query(event)
    
def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

  log.info("Hub running2.")

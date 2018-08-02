
from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct


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
  portmessage = event.connection.phyports[1]       #make eth1 openflow_enable
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  
   
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=1;
  ofmatch20_1.offset=0;
  ofmatch20_1.length=48;
  
  
  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=2;
  ofmatch20_2.offset=96;
  ofmatch20_2.length=16;
  
  ofmatch20_3 =of.ofp_match20()
  ofmatch20_3.fieldId=3;
  ofmatch20_3.offset=112;
  ofmatch20_3.length=16;
  
  ofmatch20_4 =of.ofp_match20()
  ofmatch20_4.fieldId=4;
  ofmatch20_4.offset=144; 
  ofmatch20_4.length=40;                           #length of ContentName
   
    
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  msg.flowTable.matchFieldList.append(ofmatch20_4)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 4                    #match num
  
 
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=120                        #match field length
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
  tempmatchx.set_value("90b11c5a5299")  #90:b1:1c:5a:52:99,192.168.1.2
  tempmatchx.set_mask("ffffffffffff")
  msg.matchx.append(tempmatchx)
  
  
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=2
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0011")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)        #0011 means a new protocol
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=112
  tempmatchx.length=16
  tempmatchx.set_value("0001")
  tempmatchx.set_mask("ffff")          #0001 means it is a Interest Packet
  msg.matchx.append(tempmatchx)
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=4
  tempmatchx.offset=144
  tempmatchx.length=40
  name='name1'
  value=""
  for i in range(0,len(name)):
    value += str(hex(ord(name[i]))[2:])
  tempmatchx.set_value(value)
  tempmatchx.set_mask("ffffffffff")          #6e 61 6d 65 31 means Name 'name1'
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
     
  action=of.ofp_action_op_cache()
  action.io_type =1
  action.name_len=10
  action.name="helloworld"
  action.enable_flag=1
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)

    
def _handle_ConnectionUp (event):
    test_huawei_flow(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("Hub running2.")

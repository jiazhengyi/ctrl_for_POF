
#coding:utf-8

'''
test_to_CP action 
测试方案:
通过匹配目的IP的最后一位，对奇数地址的ip, 转发包给控制器
对偶数IP地址，转发
现象：
通过ping 奇/偶 IP，观察打印信息。
Ping 偶数ip， 转发
ping 奇数IP， 转给控制器
'''



from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
import global_env as g

log = core.getLogger()

  ##############################################################################
  #flow_mod 1
  ###############################################################################
def test_to_CP(event): 
  out_port = g.output_port
  '''
  num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[7]
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)
  '''
   
  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=23; # dest_ip addr
  ofmatch20_1.offset=0;
  ofmatch20_1.length=32;
  
  
  
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  
  msg.flowTable.command=0  #OFPTC_ADD
  
  msg.flowTable.tableType=0  #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 1
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
  msg.flowTable.tableSize=128
  msg.flowTable.tableId=0
  msg.flowTable.tableName="FirstEntryTable"
  msg.flowTable.keyLength=32
  event.connection.send(msg)

  ##############################################################################
  #flow_mod 0
  ###############################################################################

  msg = of.ofp_flow_mod()
  msg.counterId = 1
  msg.cookie = 0
  msg.cookieMask = 0
  msg.tableId = 0
  msg.tableType = 0 #OF_MM_TABLE
  msg.priority = 0
  msg.index = 0

  tempmatchx = of.ofp_matchx()
  tempmatchx.fieldId = 23
  tempmatchx.offset = 0
  tempmatchx.length = 32
  # even IP 
  tempmatchx.set_value("00000000")
  tempmatchx.set_mask("00000001")

  msg.matchx.append(tempmatchx)

  #instruction
  tempins = of.ofp_instruction_applyaction()

  action = of.ofp_action_toCP()
  action.portId = g.output_port
  action.metadataOffset = 0
  action.metadataLength = 0
  action.packetOffset = 0    
  tempins.actionList.append(action)
  msg.instruction.append(tempins)

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
  msg.index=1
 
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=23
  tempmatchx.offset=0
  tempmatchx.length=32
  tempmatchx.set_value("00000001") #  奇数IP
  tempmatchx.set_mask("00000001")
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
  action=of.ofp_action_setfield()
  action.fieldSetting.fieldId=24 # src_mac
  action.fieldSetting.offset=0
  action.fieldSetting.length=48
  action.fieldSetting.set_value("ffaaffaaffaa")
  action.fieldSetting.set_mask("ffffffffffff")
  tempins.actionList.append(action)
  
  action=of.ofp_action_output()
  action.portId=out_port
  action.metadataOffset=0
  action.metadataLength=0
  action.packetOffset=0
  
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)

    
def _handle_ConnectionUp (event):
    test_SET_FIELD(event)
   

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_SET_FIELD running.")


from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct


from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
import Common
import CS_MATCH_ContentPacket


log = core.getLogger()

IPacket_index=0
CPacket_index=0
#CS_List=["zuimeishiguang-1","zuimeishiguang-2","zuimeishiguang-3","zuimeishiguang-4","zuimeishiguang-5","zuimeishiguang-6","zuimeishiguang-7","zuimeishiguang-8","zuimeishiguang-9"]
#CS_List=["zuimeishiguang-6","zuimeishiguang-7","zuimeishiguang-8"]
CS_List=[]
CSIP_COMMAND=0
CSIP_NAME="CS_MATCH_InterestPacket"
#we should choose EM(2) ,rather than MM(0)
CSIP_TYPE=2
CSIP_ID=0
#CSIP_SIZE=50000
CSIP_NAME_LEN=16                                    #Matched ContentName len

def  get_cache_file_list():
    CacheList=[]
    file1=open("/tmp/CacheListName/list.txt","r")
    all_lines=file1.readlines()
    for line in all_lines:
        CacheList.append(line.split("\n")[0].strip())
    return CacheList

def  send_port_mod(event):  
        msg = of.ofp_port_mod()
        num =  len(event.connection.phyports)
        for i in range(0,num):
            portmessage = event.connection.phyports[i]
            msg.setByPortState(portmessage)
            msg.desc.openflowEnable = 1 
            msg.reason = 2
            event.connection.send(msg)

def  modify_port_status(event,port):
    #num =  len(event.connection.phyports)
    msg = of.ofp_port_mod()
    portmessage = event.connection.phyports[port]       #make eth1 openflow_enable
    msg.setByPortState(portmessage)
    msg.desc.openflowEnable = 1 
    event.connection.send(msg)
  
  
def create_cache_table(event): 

  ofmatch20_1 =of.ofp_match20()
  ofmatch20_1.fieldId=1;
  ofmatch20_1.offset=96;
  ofmatch20_1.length=16;                          #a new protocol,CCN,0x0011
  
  ofmatch20_2 =of.ofp_match20()
  ofmatch20_2.fieldId=2;
  ofmatch20_2.offset=112;
  ofmatch20_2.length=16;                          #0x0001:Interest Packet,0x0002:Content Packet
  
  ofmatch20_3 =of.ofp_match20()
  ofmatch20_3.fieldId=3;
  ofmatch20_3.offset=144; 
  ofmatch20_3.length=CSIP_NAME_LEN*8;                          #ContentName's length,bits unit
   
    
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=CSIP_COMMAND                         #OFPTC_ADD
  msg.flowTable.tableType=CSIP_TYPE                       #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 3                 #match num
  msg.flowTable.tableSize=Common.CSIP_SIZE
  msg.flowTable.tableId=CSIP_ID
  msg.flowTable.tableName=CSIP_NAME
  msg.flowTable.keyLength=32+CSIP_NAME_LEN*8                      #match field length
  event.connection.send(msg)
  

def create_cache_table_flow(event,index,io_type,name,name_len,enable_flag,counterId):
  
  msg=of.ofp_flow_mod()
  msg.counterId=counterId
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=CSIP_ID
  msg.tableType=CSIP_TYPE                                 #OF_MM_TABLE
  msg.priority=0
  msg.index=index
  msg.hardTimeout=10
  msg.idleTimeout=10
   
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=1
  tempmatchx.offset=96
  tempmatchx.length=16
  tempmatchx.set_value("0011")
  tempmatchx.set_mask("ffff")
  msg.matchx.append(tempmatchx)        #0011 means a new protocol
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=2
  tempmatchx.offset=112
  tempmatchx.length=16
  tempmatchx.set_value("0001")         #0001 means it is a Interest Packet
  tempmatchx.set_mask("ffff")           
  msg.matchx.append(tempmatchx)
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=144
  tempmatchx.length=name_len*8         #notice this must be bit length
  value=""
  for i in range(0,len(name)):
    value += str(hex(ord(name[i]))[2:])
  mask=b'ff'
  tempmatchx.set_value(value)
  tempmatchx.set_mask(mask*name_len)         
  msg.matchx.append(tempmatchx)
  
  #instruction
  tempins=of.ofp_instruction_applyaction()
     
  
 
  action=of.ofp_action_op_cache()
  action.io_type =io_type
  action.name_len=name_len
  action.name=name
  action.enable_flag=enable_flag
 
 
  '''
  action=of.ofp_action_output()
  action.portId = 4
  '''
    
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)


def _handle_ConnectionUp (event):
    global IPacket_index,CS_List,CPacket_index
    #modify_port_status(event,1)
    #modify_port_status(event,2)
    #modify_port_status(event,3)
    create_cache_table(event)
    
    CS_List=get_cache_file_list()
    #maybe CacheList have some contents in initialise
    for i in range(0,len(CS_List)):
         #print "%s:%d" % (CS_List[i],len(CS_List[i])),maybe we do not need counter
         create_cache_table_flow(event,IPacket_index,1,CS_List[i],len(CS_List[i]),1,0)
         IPacket_index=IPacket_index+1
         Common.COUNTERID=Common.COUNTERID+1  
         
    
    CS_MATCH_ContentPacket.create_CSCP_table(event)
    for i in range(0,len(CS_List)):
         CS_MATCH_ContentPacket.create_CSCP_flow(event,CPacket_index,CS_List[i],len(CS_List[i]),0)
         CPacket_index=CPacket_index+1
         Common.COUNTERID=Common.COUNTERID+1
  


def _handle_PacketIn(event):
     global IPacket_index
     ofp=event.ofp
     packetData=ofp.packetData  
     if ofp.reason==5:
         log.info("Now begin to add new entry in CS_MATCH_InterestPacketTable")
         total_len=len(packetData)
         tmp1,match_name_len,tmp2=struct.unpack("!20sH%ds" %(total_len-22),packetData)
         tmp1,match_name_value,tmp2=struct.unpack("!22s%ds%ds" %(match_name_len,total_len-22-match_name_len),packetData) 
         if match_name_len==CSIP_NAME_LEN:
             create_cache_table_flow(event,IPacket_index,1,match_name_value,match_name_len,1,Common.COUNTERID)
             IPacket_index=IPacket_index+1 
             Common.COUNTERID=Common.COUNTERID+1                             


def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Create CS_MATCH_InterestPacket Table...")

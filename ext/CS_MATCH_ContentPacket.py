
from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct


from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
import Common

log = core.getLogger()
CurIndex=0
#CS_List=["zuimeishiguang-1","zuimeishiguang-2","zuimeishiguang-3","zuimeishiguang-4","zuimeishiguang-5","zuimeishiguang-6","zuimeishiguang-7","zuimeishiguang-8","zuimeishiguang-9"]
#CS_List=["zuimeishiguang-6","zuimeishiguang-7","zuimeishiguang-8"]
CS_List=[]
#Information of Match ContentPacket Table
CSCP_MATCH_NAME_LEN=16
CSCP_COMMAND=0
#we should choose EM(2) ,rather than MM(0)
CSCP_TYPE=2
#CSCP_SIZE=50000
CSCP_ID=3
CSCP_NAME="CS_MATCH_ContentPacket"

def  get_cache_file_list():
    CacheList=[]
    file1=open("/tmp/CacheListName/list.txt","r")
    all_lines=file1.readlines()
    for line in all_lines:
        CacheList.append(line.split("\n")[0].strip())
    return CacheList

def create_CSCP_table(event): 

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
  ofmatch20_3.offset=176; 
  ofmatch20_3.length=CSCP_MATCH_NAME_LEN*8;                          #ContentName's length
   
    
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=CSCP_COMMAND                        #OFPTC_ADD
  msg.flowTable.tableType=CSCP_TYPE                         #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 3                           #match num
  msg.flowTable.tableSize=Common.CSCP_SIZE
  msg.flowTable.tableId=CSCP_ID
  msg.flowTable.tableName=CSCP_NAME
  msg.flowTable.keyLength=32+CSCP_MATCH_NAME_LEN*8          #match field length
  event.connection.send(msg)
  
def create_CSCP_flow(event,index,name,name_len,counterId):
  
  msg=of.ofp_flow_mod()
  msg.counterId=counterId
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=CSCP_ID
  msg.tableType=CSCP_TYPE                                 #OF_MM_TABLE
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
  tempmatchx.set_value("0002")         #0002 means it is a Content Packet
  tempmatchx.set_mask("ffff")           
  msg.matchx.append(tempmatchx)
  
  tempmatchx=of.ofp_matchx()
  tempmatchx.fieldId=3
  tempmatchx.offset=176
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
         
  action_drop=of.ofp_action_drop()
  action_drop.reason=1                #have store matched Content Object
  
  tempins.actionList.append(action_drop)
  msg.instruction.append(tempins)
  event.connection.send(msg)


def _handle_ConnectionUp (event):
    global CurIndex,CS_List
    '''
    #realise in CS_MATCH_ContentPacket.py
    create_CSCP_table(event)
    
    CS_List=get_cache_file_list()
    #maybe this is included in process of initialise
    for i in range(0,len(CS_List)):
         #print "%s:%d" % (CS_List[i],len(CS_List[i]))
         create_CSCP_flow(event,CurIndex,CS_List[i],len(CS_List[i]),Common.COUNTERID)
         CurIndex=CurIndex+1
         Common.COUNTERID=Common.COUNTERID+1
    '''
    
def _handle_PacketIn(event):
     global CurIndex
     ofp=event.ofp
     packetData=ofp.packetData 
      
     #Content Packet is coming,Need to Add a new entry
     if ofp.reason==5:
         log.info("Now begin to Add new entry in CS_MATCH_ContentPacketTable")
         total_len=len(packetData)
         tmp1,match_name_len,tmp2=struct.unpack("!20sH%ds" %(total_len-22),packetData)
         tmp1,match_name_value,tmp2=struct.unpack("!22s%ds%ds" %(match_name_len,total_len-22-match_name_len),packetData) 
         if match_name_len==CSCP_MATCH_NAME_LEN:
             create_CSCP_flow(event,CurIndex,match_name_value,match_name_len,Common.COUNTERID) 
             CurIndex=CurIndex+1
             Common.COUNTERID=Common.COUNTERID+1   
             Common.add_content_arrive_port(match_name_value,event.port)
             Common.print_route_table()                        

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Create ContentTable...")

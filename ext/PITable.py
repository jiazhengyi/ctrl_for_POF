from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
from setuptools.command import install_scripts
from ContentInterestPairTable import *
from Common import *
import struct
import time

log = core.getLogger()


Forwarding_Strategy=1
PITable_Current_Index=0
Match_Name_list=[]
CS_List=["name1","name2"]
PIT_COMMAND=0
PIT_NAME="PITable"
#we should choose EM(2) ,rather than MM(0)
PIT_TYPE=2
PIT_ID=1
#PIT_SIZE=128
PIT_NAME_LEN=16                                    #Matched ContentName len

def modidy_port_status(event):
  #num =  len(event.connection.phyports)
  msg = of.ofp_port_mod()
  portmessage = event.connection.phyports[3]       #make eth1 openflow_enable
  msg.setByPortState(portmessage)
  msg.desc.openflowEnable = 1 
  event.connection.send(msg)

def create_PIT_table(event): 

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
  ofmatch20_3.length=PIT_NAME_LEN*8;                          #ContentName's length
   
    
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=PIT_COMMAND                         #OFPTC_ADD
  msg.flowTable.tableType=PIT_TYPE                       #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 3                 #match num
  msg.flowTable.tableSize=Common.PIT_SIZE
  msg.flowTable.tableId=PIT_ID
  msg.flowTable.tableName=PIT_NAME
  msg.flowTable.keyLength=32+PIT_NAME_LEN*8                      #match field length
  event.connection.send(msg)
  
def create_PIT_table_flow(event,index,name,name_len,operation_type,counterId):
  
  msg=of.ofp_flow_mod()
  msg.counterId=counterId
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=PIT_ID
  msg.tableType=PIT_TYPE                                 #OF_MM_TABLE
  msg.priority=0
  msg.index=index
   
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
       
  
  action=of.ofp_action_modify()
  action.current_table_id=PIT_ID
  action.current_table_type=PIT_TYPE
  action.current_index=index
  
  action.related_table_id=2
  action.related_table_type=0
  action.related_index=index
  action.operation_type=operation_type
  
  
  
  '''
  action=of.ofp_action_output()
  action.portId = 4
  '''
  
  tempins.actionList.append(action)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)
    
def _handle_ConnectionUp (event):
    modidy_port_status(event)
    create_PIT_table(event)
    create_ContentInterestPairTable(event)
    

def _handle_PacketIn (event):
    global Forwarding_Strategy,PITable_Current_Index
    ofp=event.ofp
    packetData=ofp.packetData
    
    #Interest Packet don't match PITable
    if ofp.reason==4:
        total_len=len(packetData)
        tmp1,match_name_len,tmp2=struct.unpack("!16sH%ds" %(total_len-18),packetData)
        tmp1,match_name_value,tmp2=struct.unpack("!18s%ds%ds" %(match_name_len,total_len-18-match_name_len),packetData)
        output_interest_port=look_for_path(match_name_value)
        if output_interest_port==0:
            Forwarding_Strategy=1
        else:
            Forwarding_Strategy=0
        #print ofp.show()
        if Forwarding_Strategy==0:
            log.info("%s,%d,%s" %("begin to decide forward path for",match_name_len,match_name_value))
            log.info("forward %s to port %d" %(match_name_value,output_interest_port))
            
            create_PIT_table_flow(event,PITable_Current_Index,match_name_value,match_name_len,1,Common.COUNTERID)
            Common.COUNTERID=Common.COUNTERID+1
            create_ContentInterest_table_flow(event,match_name_value,match_name_len,0,PITable_Current_Index,2,0,PITable_Current_Index,1,0,event.port,Common.COUNTERID)
            Common.COUNTERID=Common.COUNTERID+1
            add_forwarding_name_list(match_name_value,match_name_len,event.port)
            #just let index add 1,further we need to get the least unused index
            PITable_Current_Index=PITable_Current_Index+1
            
            log.info("PIT related table has been generated!")
            
            msg = of.ofp_packet_out()
            msg.bufferId = event.ofp.bufferId
            msg.inPort = event.port
            msg.actions.append(of.ofp_action_output(portId = output_interest_port)) 
            msg.data = packetData
            event.connection.send(msg)
            
            log.info("packet out message has been sent to switch")
            
        elif Forwarding_Strategy==1:
            
            log.info("%s,%d,%s" %("flood this Interest Packet,because we have no info",match_name_len,match_name_value))
            
            #after we forward this packet,we need to record it in PITable        
            create_PIT_table_flow(event,PITable_Current_Index,match_name_value,match_name_len,1,Common.COUNTERID)
            Common.COUNTERID=Common.COUNTERID+1
            create_ContentInterest_table_flow(event,match_name_value,match_name_len,0,PITable_Current_Index,2,0,PITable_Current_Index,1,0,event.port,Common.COUNTERID)
            Common.COUNTERID=Common.COUNTERID+1
            
            #record we have forward this kind of packet,when a same packet comes in,we need to judge if coming from same port
            add_forwarding_name_list(match_name_value,match_name_len,event.port)
            
            #just let index add 1,further we need to get the least unused index
            PITable_Current_Index=PITable_Current_Index+1 
                
            log.info("PIT related table has been generated!")
            
            #now begin to flood this Interest Packet
            portMaxNum=len(event.connection.phyports)
            for OutportId in range(1,portMaxNum+1):
                if OutportId==2:
                    #this is openflow port,just pass
                    pass
                else:
                    if OutportId==event.port:
                        pass
                    else:
                        msg = of.ofp_packet_out()
                        msg.bufferId = event.ofp.bufferId
                        msg.inPort = event.port
                        msg.actions.append(of.ofp_action_output(portId = OutportId)) 
                        msg.data = packetData
                        event.connection.send(msg)
            log.info("packet out message has been sent to switch")
            
            '''
            msg = of.ofp_packet_out()
            msg.bufferId = event.ofp.bufferId
            msg.inPort = event.port
            msg.actions.append(of.ofp_action_drop()) 
            msg.actions.append(of.ofp_action_output(portId = 2)) 
            msg.data = packetData
            event.connection.send(msg)
            '''
                               
def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

  log.info("Create PITable...")

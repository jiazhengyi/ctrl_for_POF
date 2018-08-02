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
from pox.lib.revent import *
from pox.lib.util import hexdump
import struct
import Common
# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()

CIPT_MATCH_NAME_LEN=16
CIPT_COMMAND=0
#we should choose EM(2) ,rather than MM(0)
CIPT_TYPE=2
#CIPT_SIZE=128
CIPT_ID=2
CIPT_NAME="ContentInterestTable"

NAME_PORT_LIST=[]


def judge_same_Interest_Packet(match_name_value,match_name_len,port):
    count=0
    if  len(NAME_PORT_LIST)>0:
            for item in NAME_PORT_LIST:
                if  (match_name_value==item[0] and match_name_len==item[1] and port==item[2]):
                    return 1
                else:
                    count=count+1
                if  count==len(NAME_PORT_LIST):
                    break
    count=0
    samename_port_list=[]
    if  len(NAME_PORT_LIST)>0:
            for item in NAME_PORT_LIST:
                if (match_name_value==item[0] and match_name_len==item[1]):
                    samename_port_list.append(item[2])
                count=count+1
                if(count==len(NAME_PORT_LIST)):
                    break
    count=0
    for i in range(0,len(samename_port_list)):
        if port!=samename_port_list[i]:
            count=count+1
    if count==len(samename_port_list):
        #port is not in samename_port_list
        return 2
    return 0

def lookup_ori_port(match_name_value,match_name_len):
    port_list=[]
    count=0
    if len(NAME_PORT_LIST)>0:
        for item in NAME_PORT_LIST:
            if  (match_name_value==item[0] and match_name_len==item[1]):
                port_list.append(item[2])
            count=count+1
            if count==len(NAME_PORT_LIST):
                break  
    return port_list
                    
def add_forwarding_name_list(match_name_value,match_name_len,port):
    global NAME_PORT_LIST
    NAME_PORT_LIST.append((match_name_value,match_name_len,port))

def create_ContentInterestPairTable(event): 

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
  ofmatch20_3.length=CIPT_MATCH_NAME_LEN*8;                          #ContentName's length
   
    
  msg =of.ofp_table_mod()
  
  msg.flowTable.matchFieldList.append(ofmatch20_1)
  msg.flowTable.matchFieldList.append(ofmatch20_2)
  msg.flowTable.matchFieldList.append(ofmatch20_3)
  
  msg.flowTable.command=CIPT_COMMAND                        #OFPTC_ADD
  msg.flowTable.tableType=CIPT_TYPE                       #OF_MM_TABLE
  msg.flowTable.matchFieldNum = 3                 #match num
  msg.flowTable.tableSize=Common.CIPT_SIZE
  msg.flowTable.tableId=CIPT_ID
  msg.flowTable.tableName=CIPT_NAME
  msg.flowTable.keyLength=32+CIPT_MATCH_NAME_LEN*8                      #match field length
  event.connection.send(msg)

def create_ContentInterest_table_flow(event,name,name_len,operation_type,index,table_id,table_type,related_index,related_table_id,related_type,port_id,counterId):
  
  msg=of.ofp_flow_mod()
  msg.counterId=counterId
  msg.cookie=0
  msg.cookieMask=0
  msg.tableId=table_id
  msg.tableType=table_type                                 #OF_MM_TABLE
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
         
 
  
  action_output=of.ofp_action_output()
  action_output.portId=port_id
  
  '''
  action=of.ofp_action_modify()
  action.current_table_id=table_id
  action.current_table_type=table_type
  action.current_index=index
  action.related_table_id=related_table_id
  action.related_table_type=related_type
  action.related_index=related_index
  action.operation_type=operation_type
  
  action_delete_self=of.ofp_action_modify()
  action_delete_self.current_table_id=table_id
  action_delete_self.current_table_type=table_type
  action_delete_self.current_index=index
  action_delete_self.related_table_id=table_id
  action_delete_self.related_table_type=table_type
  action_delete_self.related_index=index
  action_delete_self.operation_type=operation_type
  '''
    
  tempins.actionList.append(action_output)
  #tempins.actionList.append(action)
  #tempins.actionList.append(action_delete_self)
  msg.instruction.append(tempins)
  
  event.connection.send(msg)

# Handle messages the switch has sent us because it has no
# matching rule.

def modify_ContentInterest_table_flow(event,name,name_len,operation_type,index,table_id,table_type,related_index,related_table_id,related_type,port_id,port_list,counterId):
    msg=of.ofp_flow_mod()
    msg.counterId=counterId
    msg.command=1
    msg.cookie=0
    msg.cookieMask=0
    msg.tableId=table_id
    msg.tableType=table_type                                 #OF_MM_TABLE
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
         
 
    action_output=of.ofp_action_output()
    action_output.portId=port_id
    tempins.actionList.append(action_output)
    
    for i in range(len(port_list)):
        action_output_other=of.ofp_action_output()
        action_output_other.portId=port_list[i]
        tempins.actionList.append(action_output_other)
  
    action_delete_related=of.ofp_action_modify()
    action_delete_related.current_table_id=table_id
    action_delete_related.current_table_type=table_type
    action_delete_related.current_index=index
    action_delete_related.related_table_id=related_table_id
    action_delete_related.related_table_type=related_type
    action_delete_related.related_index=related_index
    action_delete_related.operation_type=operation_type
  
    action_delete_self=of.ofp_action_modify()
    action_delete_self.current_table_id=table_id
    action_delete_self.current_table_type=table_type
    action_delete_self.current_index=index
    action_delete_self.related_table_id=table_id
    action_delete_self.related_table_type=table_type
    action_delete_self.related_index=index
    action_delete_self.operation_type=operation_type
    
    tempins.actionList.append(action_delete_related)
    tempins.actionList.append(action_delete_self)
    msg.instruction.append(tempins)
  
    event.connection.send(msg)


def _handle_PacketIn (event):
    global Create_Flag,CIPT_MATCH_NAME_LEN,CIPT_COMMAND,CIPT_TYPE,CIPT_SIZE,CIPT_ID,CIPT_NAME
    global NAME_PORT_LIST
    ofp=event.ofp
    packetData=ofp.packetData
    
    #Need Controller to Add a new entry
    if ofp.reason==3:
        curr_index,curr_table_id,curr_table_type,related_index,related_table_id,related_type=struct.unpack("!LBBLBB", packetData[60:])
        total_len=len(packetData)
        tmp1,match_name_len,tmp2=struct.unpack("!16sH%ds" %(total_len-18),packetData)
        tmp1,match_name_value,tmp2=struct.unpack("!18s%ds%ds" %(match_name_len,total_len-18-match_name_len),packetData)
        #print match_name_value,match_name_len
        
        if  len(NAME_PORT_LIST)>0:
            ret=judge_same_Interest_Packet(match_name_value,match_name_len,event.port)
            if ret==1:
                log.info("recv a same InterestPacket from same port")
            elif ret==2:
                log.info("Now begin to modify ContentInterestPairTable")
                ori_port=lookup_ori_port(match_name_value, match_name_len)
                '''
                for i in range(0,len(ori_port)):
                    print "original input port is %d" %(ori_port[i])
                '''
                modify_ContentInterest_table_flow(event, match_name_value, match_name_len, 0, curr_index,curr_table_id,curr_table_type,\
                                                  related_index,related_table_id,related_type,event.port,ori_port,Common.COUNTERID)
                Common.COUNTERID=Common.COUNTERID+1
                add_forwarding_name_list(match_name_value,match_name_len,event.port)
            else:
                create_ContentInterest_table_flow(event,match_name_value,match_name_len,0,curr_index,curr_table_id,curr_table_type,\
                                related_index,related_table_id,related_type,event.port,Common.COUNTERID)
                Common.COUNTERID=Common.COUNTERID+1
                #NAME_PORT_LIST.append((match_name_value,match_name_len,event.port))
                add_forwarding_name_list(match_name_value,match_name_len,event.port)
        else:
            create_ContentInterest_table_flow(event,match_name_value,match_name_len,0,curr_index,curr_table_id,curr_table_type,\
                                related_index,related_table_id,related_type,event.port,Common.COUNTERID)
            Common.COUNTERID=Common.COUNTERID+1
            #NAME_PORT_LIST.append((match_name_value,match_name_len,event.port))
            add_forwarding_name_list(match_name_value,match_name_len,event.port)
    
    
def launch ():
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Handle PacketIn Msg running.")

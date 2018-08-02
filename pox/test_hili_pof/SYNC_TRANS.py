
#coding:utf-8
'''
test OUTPUT action 
测试方案:
匹配包进入的端口：input port
ping input port 同网段的 ip
现象：
包只能单向传输，即在input port 抓包只能收到arp请求，收不到响应
'''
from pox.openflow.libopenflow_01 import ofp_packet_out, ofp_action_output
import struct

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep

import sync_config as cfg
import table_config as t_cfg
log = core.getLogger()

def test_TSLOT_CFG(event): 
	msg = cfg.add_time_slot()

	event.connection.send(msg)

def test_CLASSFIER_TABLE (event):
	ofmatch20_1 = of.ofp_match20()
	ofmatch20_1.fieldId = 23
	#the last bit of dest IP
	ofmatch20_1.offset = 0
	ofmatch20_1.length = 32


	table = of.sync_flow_table()
	
	table.matchFieldList.append(ofmatch20_1)
	table.command = 0    #OFPTC_ADD
	table.tableType = of.OF_EM_TABLE  #OF_MM_TABLE
	#table.matchFieldNum = 1

	table.matchFieldNum = len(table.matchFieldList)
	table.tableSize = 128
	table.tableId = 0xfd 
	table.tableName = "Classfier_Table"
	table.keyLength = 16
	

	msg = of.ofp_experimenter()
	msg.type = of.CLASSFIER_TABLE
	msg.ctab.type = of.SYNC_TABLE
	msg.ctab.table = table

	event.connection.send(msg)
	entry = of.sync_flow_entry()
	entry.command = 0
	entry.counterId = 1
	entry.cookie = 0
	entry.cookieMask = 0
	entry.tableId = 0xfd
	entry.tableType = of.OF_EM_TABLE #OF_MM_TABLE
	entry.priority = 0
	entry.index = 1

	tempmatchx = of.ofp_matchx()
	tempmatchx.fieldId = 47
	tempmatchx.offset = 12 *8
	tempmatchx.length = 16
	#odd IP
	tempmatchx.set_value("0806")
	tempmatchx.set_mask("ffff")

	entry.matchx.append(tempmatchx)

	tempins = of.ofp_instruction_applyaction()

	action = of.ofp_action_addfield()
	action.fieldId = 48
	action.fieldPosition = 96
	action.fieldLength = 32
	action.set_fieldValue("ffff0001")
	tempins.actionList.append(action)
	
	action = of.ofp_action_output()
	action.portId = 0xffe1
	action.metadataOffset = 0
	action.metadataLength = 0
	action.packetOffset = 0
	tempins.actionList.append(action)
	entry.instruction.append(tempins)

	msg = of.ofp_experimenter()
	msg.type = of.CLASSFIER_TABLE
	msg.ctab.type = of.SYNC_ENTRY
   	msg.ctab.entry = entry

	event.connection.send(msg)



def _handle_ConnectionUp (event):
	print ("connect up up up !!!!\n")
	print event.connection.dpid
	if (event.connection.dpid > 0):
		test_TSLOT_CFG(event)
	else :
		test_CLASSFIER_TABLE(event)

def handle_SyncTransUp (event):
	print ("synctrans up!!!!!!\n")
	print ("the devid:", event.dpid)

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
	#ConnectionUp define in  __init__py

	log.info("test_TSLOT_CFG running.")

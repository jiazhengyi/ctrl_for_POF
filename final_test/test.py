# coding:utf-8

import sys
sys.path.append('/home/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of
from pox.core import core

import time
import flow_table_config.table_config as table
import flow_table_config.global_env as g
import tsn_delay.tsn_config as conf

log = core.getLogger()
 
      
def add_tsn_test_config(event):
        # add PTP config
        msg = conf.add_TSN_config_multi_slot(1,'0x0',0,'1|2|60|70|80|90',1)
        #msg = conf.add_TSN_config_multi_all_add_1(1,'0x0',0,'1',1)
        event.connection.send(msg)

        if (event.dpid == 1):
            add_tsn_1_config(event)
        elif (event.dpid == 2):
            add_tsn_2_config(event)
        elif (event.dpid == 3):
            add_tsn_3_config(event)
        elif (event.dpid == 4):
            add_tsn_4_config(event)

def add_tsn_1_config(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)
 
        msg = table.add_classfier_entry('classifier2', 1)
        event.connection.send(msg)
 
        msg = conf.add_TSN_config_multi_slot(1,'0xffffffffff00',0x6,'13',6)
        event.connection.send(msg)
         
def add_tsn_2_config(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)
 
        msg = table.add_classfier_entry('classifier2', 1)
        event.connection.send(msg)
 
        msg = conf.add_TSN_config_multi_slot(1,'0xffffffffff00',0x6,'25',6)
        event.connection.send(msg)
 
def add_tsn_3_config(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)
 
        msg = table.add_classfier_entry('classifier2', 1)
        event.connection.send(msg)
 
        msg = conf.add_TSN_config_multi_slot(1,'0xffffffffff00',0x6,'33',6)
        event.connection.send(msg)

def add_tsn_4_config(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)
 
        msg = table.add_classfier_entry('classifier2', 2)
        event.connection.send(msg)
 
        msg = conf.add_TSN_config_multi_slot(1,'0xffffffffff00',0x6,'3',3)
        event.connection.send(msg)
 

def _handle_ConnectionUp(event):
        add_tsn_test_config(event)
        #add_timer_test(event)

def launch():
        core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        #core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        log.info("add_tsn_test running.")


if __name__ == '__main__':
        add_tsn_config(event)


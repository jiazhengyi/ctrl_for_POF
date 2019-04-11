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
 
      
def add_timer_test(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)
        
        if  (event.dpid == 2):
            msg = table.add_classfier_entry('classifier2', 2)
        else :
            msg = table.add_classfier_entry('classifier2', 1)
        
        event.connection.send(msg)

def add_tsn_config(event):
        # add PTP config
        msg = conf.add_TSN_config_multi_all_add_1(1,'0x0',0,'1',1)
        event.connection.send(msg)

        if (event.dpid == 4):
            msg = conf.add_TSN_config_multi_all_add_x(10,2,'0xffffffffff00',0x4,'5',3)
            event.connection.send(msg)
            
            msg = conf.add_TSN_config_multi_all_add_1(1,'0xffffffffff14',0x4,'20',20)
            event.connection.send(msg)
            
            msg = conf.add_TSN_config_multi_all_add_1(1,'0xffffffffff1e',0x4,'40',21)
            event.connection.send(msg)
            
            msg = conf.add_TSN_config_multi_all_add_1(1,'0xffffffffff28',0x4,'55',22)
            event.connection.send(msg)
 
        else :
            msg = conf.add_TSN_config_multi_all_add_x(10,5,'0xffffffffff00',0x2,'5',3)
            event.connection.send(msg)



def add_tsn_config_bw(event):
        # add PTP config
        #msg = conf.add_TSN_config_multi_all_add_1(1,'0x0',0,'1',1)
        #event.connection.send(msg)

        msg = table.add_classfier_table('classifier4')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier4', 0)
        event.connection.send(msg)
 
        msg = table.add_classfier_entry('classifier4', 1)
        event.connection.send(msg)
 
        msg = conf.add_TSN_config_multi_slot(1,'0xffffffffff00',0x2,'1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19',3)
        event.connection.send(msg)
         


def _handle_ConnectionUp(event):
        add_tsn_config_bw(event)
        #add_timer_test(event)

def launch():
        core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        #core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        log.info("add_timer_test running.")


if __name__ == '__main__':
        add_tsn_config(event)


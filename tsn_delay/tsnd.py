# coding:utf-8

import sys
sys.path.append('/home/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of
from pox.core import core

import time
import flow_table_config.table_config as table
import tsn_config as conf
import tsn_handler as hlr
import flow_table_config.global_env as g

log = core.getLogger()
 
TSN_CYCLE = 100

# TD-MIB format: { sending_deviceID:[{sending_portID:[receiving_deviceID, receiving_portID, delay]},{}]
TD_MIB = {}

def init_TD_MIB(config):
    for dev in config.keys():
        c = config[dev]
        TD_MIB[dev] = {}
        flow_num = len(c)
        for i in range(flow_num):
            port = int(c[i][3],16)
            if (port < 255):
                TD_MIB[dev][port] = []
    return


def write_TD_MIB(tsnd_pkt):
    dev = tsnd_pkt.send_dev
    if (not TD_MIB.has_key(dev)):
        print("no such device:",dev)
        return
    delay = (tsnd_pkt.rcvtime + TSN_CYCLE - tsnd_pkt.send_tslot)%TSN_CYCLE
    d = TD_MIB[dev]
    if (not d.has_key(tsnd_pkt.send_port)):
        print ("TD-MIB not has send port:",tsnd_pkt.send_port)
        return
    else :
        d[tsnd_pkt.send_port].append([tsnd_pkt.recv_dev,tsnd_pkt.inport,delay,tsnd_pkt.var])
    
    return

       
def add_tsn_switch(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)

        if  (event.dpid == 2):
            msg = table.add_classfier_entry('classifier2', 2)
        else :
            msg = table.add_classfier_entry('classifier2', 1)
        
        event.connection.send(msg)


def _handle_ConnectionUp(event):
        add_tsn_switch(event)
        # add PTP config
        msg = conf.add_TSN_config_multi_auto1(1,'0x0',0,'1',1)
        event.connection.send(msg)

        if (event.dpid == 2):
            msg = conf.add_TSN_config_multi_auto2(90,'0xffffffffff00',0x2,'3',3)
            event.connection.send(msg)

        else :
            msg = conf.add_TSN_config_multi_auto1(90,'0xffffffffff00',0x6,'3',3)
            event.connection.send(msg)
        '''
        # add tsnd reply config
        msg = conf.add_TSN_config_multi_auto(1,'0xffffffffffbb',0x6,'2',2)
        event.connection.send(msg)
        # add tsnd request config
        msg = conf.add_TSN_config_multi_auto(1,'0xffffffffff00',0x2,'3',3)
        event.connection.send(msg)
        '''

        #msg = conf.add_TSN_config_by_file(event.dpid,'tsn_conf_file1')
        #event.connection.send(msg)
        '''
        msg = conf.add_TSN_config_by_file(event.dpid,conf.conf_file3)
        event.connection.send(msg)
        '''

def handle_tsnd_measure(e):
        print ("handle tsnd measure by jiazy!")
        tsnd = hlr.Tsnd_Packet()
        tsnd.inport = e.ofp.port_id
        tsnd.recv_dev = e.dpid
        #print map(ord, e.ofp.packetData)
        tsnd.unpack(e.ofp.packetData)
        write_TD_MIB(tsnd)
        #print (tsnd.show())


def _handle_PacketIn(event):
        print("handle PacketIn event by jiazy!")
        reason = event.ofp.reason
        if (g.TSND_MEASURE == reason):
                handle_tsnd_measure(event)
                print (TD_MIB)


def launch():
        # init TSN global variant
        config = conf.read_tsn_config(conf.conf_file3)
        init_TD_MIB(config)
        print (TD_MIB)

        core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        log.info("add_TSN_CFG running.")


if __name__ == '__main__':
        if (conf.init_flag):
                # init TSN global variant
                conf.config = conf.read_tsn_config(conf.conf_file)
                tsn.init_flag = 0
        else:
                pass
        print(conf.config)
        add_tsn_config(event)


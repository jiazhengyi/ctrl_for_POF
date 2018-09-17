# coding:utf-8

import sys
sys.path.append('/home/naner/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of
from pox.core import core

import flow_table_config.table_config as table
import tsn_config as conf
import tsn_handler as hlr
import flow_table_config.global_env as g

log = core.getLogger()


def add_tsn_config(event):
        dpid = event.connection.dpid
        if (dpid in conf.config):
                msg = conf.add_TSN_config(conf.config[dpid])
                event.connection.send(msg)
        else:
                print("the device:%d do not have config data!" % (dpid))


def add_tsn_switch(event):
        msg = table.add_classfier_table('classifier2')
        event.connection.send(msg)

        msg = table.add_classfier_entry('classifier2', 0)
        event.connection.send(msg)
        msg = table.add_classfier_entry('classifier2', 1)
        event.connection.send(msg)


def _handle_ConnectionUp(event):
        add_tsn_config(event)
        add_tsn_switch(event)
        hlr.send_tsnd_pkt(event)

def _handle_PacketIn(event):
        print("handle PacketIn event by jiazy!")
        reason = event.ofp.reason
        if (g.TSND_MEASURE == reason):
                hlr.handle_tsnd_measure(event)


def launch():
        # init TSN global variant
        conf.config = conf.read_tsn_config(conf.conf_file)
        hlr.tsnd_pkts = conf.config
        conf.init_TD_MIB(conf.config)
        #print (conf.TD_MIB)

        core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
        core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
        log.info("add_TSN_CFG running.")


if __name__ == '__main__':
        event = 4
        if (conf.init_flag):
                # init TSN global variant
                conf.config = conf.read_tsn_config(conf.conf_file)
                tsn.init_flag = 0
        else:
                pass
        print(conf.config)
        add_tsn_config(event)


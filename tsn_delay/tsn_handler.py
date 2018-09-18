#coding:utf-8
'''
Created on Aug,29,2018

@author: jiazy

tsn_handler Module
'''
import sys
sys.path.append('/home/naner/jiazy/ctrl_for_POF/')

import time
import struct
import threading
import pox.openflow.libopenflow_01 as of
import pox.lib.util
from pox.openflow import ErrorIn
from pox.openflow import PacketIn

from pox.core import core
from pox.openflow.libopenflow_01 import UnderrunError
import flow_table_config.global_env as g
import flow_table_config.table_config as cfg
import tsn_config as c

log = core.getLogger()

def _read (data, offset, length):
  if (len(data)-offset) < length:
    raise UnderrunError("wanted %s bytes but only have %s"
                        % (length, len(data)-offset))
  return (offset+length, data[offset:offset+length])

def _unpack (fmt, data, offset):
  size = struct.calcsize(fmt)
  #print (size, len(data), offset)
  if (len(data)-offset) < size: raise UnderrunError()
  return (offset+size, struct.unpack_from(fmt, data, offset))

def _skip (data, offset, num):
  offset += num
  if offset > len(data): raise UnderrunError()
  return offset

def _unpad (data, offset, num):
  (offset, o) = _read(data, offset, num)
  assert len(o.replace("\x00", "")) == 0
  return offset


def handle_PACKET_IN (con, msg):   # type: 10
    print ("jiazy: receive PACKET_IN message\n")
    e = con.ofnexus.raiseEventNoErrors(PacketIn, con, msg)
    if e is None or e.halt != True:
        con.raiseEventNoErrors(PacketIn, con, msg)

class Ins_ToCP_Data ():
    _MIN_LENGTH = 8
    def __init__ (self, **kw):
        self.msg = of.ofp_packet_in()
        self.reason = 0
        self.metalen = 0
        self.metaData = b''
        self.packetData = b''
    def unpack (self, raw, offset=0):
        offset,(self.reason, self.metalen) = _unpack("!LH", raw, offset)
        offset = _skip(raw, offset, 2)
        offset,self.metaData = _read(raw, offset, self.metalen)
        offset,self.packetData = _read(raw, offset, self.msg.totalLength-self.metalen-self._MIN_LENGTH)
        return
    def show (self):
        outstr = ''
        outstr += 'reason:'+ str(self.reason) + '\n'

        return outstr


class Tsnd_Packet ():
    _TSND_PKT_LEN = 70
    def __init__(self, **kw):
        self.inport = 0
        self.recv_dev = 0
        self.toctrl_reason = 0
        self.rcvtime = 0
        self.flowID = 0
        self.srcMAC = 0
        self.ethtype = 0x8100
        self.vlan = 0xd000
        self.send_dev = 0
        self.send_port = 0
        self.send_tslot = 0

    def pack(self):
        flowID = struct.pack('!Q',self.flowID)[2:]
        srcMAC = struct.pack('!Q',self.srcMAC)[2:]
        #print map(ord,flowID),map(ord, srcMAC)
        seq = [flowID, srcMAC,
        struct.pack("!HHHLH",
          self.ethtype, self.vlan, self.send_dev,self.send_port,self.send_tslot)]

        data = b''
        data = b''.join(seq)
        data += '\x00' * (self._TSND_PKT_LEN - len(data))
        #print (map(ord,data))
        return data


    def unpack (self, raw, offset = 0):
        offset,(self.rcvtime,) = _unpack("!H", raw, offset)
        offset = _skip (raw, offset, 16)
        offset,(self.send_dev,self.send_port,self.send_tslot) = _unpack("!HLH",raw, offset)
        return

    def show(self):
        outstr = ''
        outstr += 'the input port(switch):' + str(self.inport) + '\n'
        outstr += 'the receive timeslot:' + str(self.rcvtime) + '\n'
        outstr += 'the send dev id:' + str(self.send_dev) + '\n'
        outstr += 'the send timeslot:' + str(self.send_tslot) + '\n'

        return outstr


tsnd_acts = {'output':[g.OFPP_TABLE],}
def encap_packet_out_msg(pkt):
    msg = of.ofp_packet_out()
    msg.in_port = g.OFPP_PKT_OUT

    for i in tsnd_acts.keys():
        args = tsnd_acts[i]
        act = cfg.insmap[i](args)
        msg.actions.append(act)
    msg.data = pkt
    return msg


TSND_REQ_FLOWID = 0xffffffffffaa
tsnd_pkts = {}
# pkt format:['FlowID','srcMAC','ethType','vlanID','send_timeslot']
def send_tsnd_pkt (event) :#  pkt can get by devID
    print ("call the function send_TSND_pkt()\n")
    pkts = tsnd_pkts[event.dpid]
    #pkts = tsnd_pkts[event]
    pkt_num = len(pkts)
    # todo: try to use 列表解析法
    for i in range(pkt_num):
        pkt_info = Tsnd_Packet()
        pkt_info.flowID = long(pkts[i][0],16)
        if (pkt_info.flowID != TSND_REPLY_FLOWID):
            pkt_info.srcMAC = long(pkts[i][1],16)
            pkt_info.send_tslot = int(pkts[i][2])
            pkt_info.send_port = int(pkts[i][3],16)
            pkt_info.send_dev = event.dpid
            msg = encap_packet_out_msg(pkt_info.pack())
            #print map(ord,msg.pack())
            event.connection.send(msg)

    return

def handle_tsnd_measure(e):
        print ("handle tsnd measure by jiazy!")
        tsnd = Tsnd_Packet()
        tsnd.inport = e.ofp.port_id
        tsnd.recv_dev = e.dpid
        #print map(ord, e.ofp.packetData)
        tsnd.unpack(e.ofp.packetData)
        c.write_TD_MIB(tsnd)
        #print (tsnd.show())
        print (c.TD_MIB)


if __name__ == '__main__':
    print("tsnd_handler module test!")
    tsnd_pkts = c.read_tsn_config('tsn_conf_file1')
    send_tsnd_pkt(2)

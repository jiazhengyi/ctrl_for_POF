
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

import global_env as g

log = core.getLogger()

def test_TSLOT_CFG(event): 
  msg = of.ofp_experimenter()
  msg.type = of.TIME_SLOT_CONFIG

  msg.tslot_cfg.cmd = 0
  msg.tslot_cfg.tag_num = 1
  
  tag_info = of.sync_tag_info()
  tag_info.tag = 0
  tag_info.tslot = [1,2,3,4,5,6,7] 
  
  msg.tslot_cfg.data.append(tag_info)
  
  event.connection.send(msg)


def _handle_ConnectionUp (event):
  test_TSLOT_CFG(event)


def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)    #ConnectionUp define in  __init__py

  log.info("test_TSLOT_CFG running.")


#coding:utf-8
import sys
sys.path.append('/home/jiazy/ctrl_for_POF/')

import pox.openflow.libopenflow_01 as of
import re
import socket
import struct
import tsn_handler as hlr


#format:{deviceID:[streamID,portID,tslot,queueID]}
#queueID is unique in each device
config = {}

# TSN config file
conf_file1 = "/home/jiazy/ctrl_for_POF/tsn_delay/tsn_conf_file1"
conf_file2 = "/home/jiazy/ctrl_for_POF/tsn_delay/tsn_conf_file2"
conf_file3 = "/home/jiazy/ctrl_for_POF/tsn_delay/tsn_conf_file3"


def read_tsn_config(file):
    config_tem = {}
    #f = open(file)
    with open(file,'r')as f:
        line = f.readline()

        # jump comments
        while line.startswith("#"):
            line = f.readline()

        # check file format
        value = line.split()
        n = len(value)
        if not line or n > 1:
            raise Exception,\
            "invalid file format:no device ID at beginning!"
    
        # read config info
        while line:
            if 1 == n:# a new device config start
                devID = int(value[0])
                if config_tem.has_key(devID):
                    print "write one dev config together"
                else:
                    config_tem[devID] = []
            else:
                config_tem[devID].append(value)

            line = f.readline()
            value = line.split()
            n = len(value)

        #f.close()

        return config_tem


def get_timeslot_list (tslot_str):
    tslot = tslot_str.split('|')
    #print tslot
    return tslot


#config format:['FlowID','PortID','TimeSlot','Queue']
def add_TSN_config (config) :# config can get by devID
    print ("call the function add_TSN_config()\n")
    flow_num = len(config)
    msg = of.ofp_experimenter()
    msg.type = of.TSN_CONFIG
    msg.tsn_cfg.cmd = 0 
    #print config
    # todo: try to use 列表解析法
    for i in range(flow_num):
        flow_info = of.TSN_flow_info()
        flow_info.flowID = long(config[i][0],16)
        flow_info.port = int(config[i][3],16)
        flow_info.tslot = get_timeslot_list(config[i][2])
        flow_info.queue = int(config[i][4])
        msg.tsn_cfg.flow_info.append(flow_info)
            
    msg.tsn_cfg.flow_num = flow_num 
    return msg

def add_TSN_config_by_file(dev_id,file):
    dic = read_tsn_config(file)
    if (not dic.has_key(dev_id)):
              print("the device:%d do not have config data!" % (dev_id))
    c = dic[dev_id]
    return add_TSN_config(c)

# dmac and tslot and queue add by 1 step
# config format:['FlowID','PortID','TimeSlot','Queue']
# dmac format:string "0xfffffffxx"
# tslot format: string "2"
def add_TSN_config_multi_auto1(flow_num, dmac, port, tslot, queue):
    print ("add tsn config auto()\n")
    msg = of.ofp_experimenter()
    msg.type = of.TSN_CONFIG
    msg.tsn_cfg.cmd = 0
    dmac_n = long(dmac, 16)
    tslot_n = int(tslot)
    # todo: try to use 列表解析法
    for i in range(flow_num):
        flow_info = of.TSN_flow_info()
        flow_info.flowID = dmac_n
        flow_info.port = port
        flow_info.tslot = get_timeslot_list(str(tslot_n))
        flow_info.queue = queue
        msg.tsn_cfg.flow_info.append(flow_info)
        
        dmac_n = dmac_n + 1
        tslot_n = tslot_n + 1
        queue = queue + 1

    msg.tsn_cfg.flow_num = flow_num 

    return msg

# dmac add by 1 and tslot and queue not change
# config format:['FlowID','PortID','TimeSlot','Queue']
# dmac format:string "0xfffffffxx"
# tslot format: string "2"
def add_TSN_config_multi_auto2(flow_num, dmac, port, tslot, queue):
    print ("add tsn config auto()\n")
    msg = of.ofp_experimenter()
    msg.type = of.TSN_CONFIG
    msg.tsn_cfg.cmd = 0
    dmac_n = long(dmac, 16)
    tslot_n = int(tslot)
    # todo: try to use 列表解析法
    for i in range(flow_num):
        flow_info = of.TSN_flow_info()
        flow_info.flowID = dmac_n
        flow_info.port = port
        flow_info.tslot = get_timeslot_list(str(tslot_n))
        flow_info.queue = queue
        msg.tsn_cfg.flow_info.append(flow_info)
        
        dmac_n = dmac_n + 1
        #tslot_n = tslot_n + 1
        #queue = queue + 1

    msg.tsn_cfg.flow_num = flow_num 

    return msg


def add_TSN_config_ptp():
    print ("add ptp config ()\n")
    msg = of.ofp_experimenter()
    msg.type = of.TSN_CONFIG
    msg.tsn_cfg.cmd = 0
    
    flow_info = of.TSN_flow_info()
    flow_info.flowID = 0xfffffffffffdd
    flow_info.port = 0
    flow_info.tslot = get_timeslot_list('1')
    flow_info.queue = 1
    msg.tsn_cfg.flow_info.append(flow_info)
    msg.tsn_cfg.flow_num = 1 

    return msg


   
if __name__ == '__main__':
     
    file = "tsn_conf_file2"
    dic = {}
    try:
        dic = read_tsn_config(file)
    except Exception, err:
        print err

    print dic
    dpid = 2
    
    print add_TSN_config_multi_auto(10, '0xffffffffaa',2,1,1)
    '''
    cnt = 0
    init_TD_MIB(dic)
    print TD_MIB
    msg = add_TSN_config(dic[2])
    print msg
    for i in range(10):
        pkts = tsnd_pkts[dpid]
            #pkts = tsnd_pkts[event]
            pkt_num = len(pkts)
            # todo: try to use 列表解析法
            for i in range(pkt_num):
            cnt += 1
                pkt = hlr.Tsnd_Packet()
                pkt.flowID = long(pkts[i][0],16)
                if (pkt.flowID == hlr.TSND_REQ_FLOWID):
                        pkt.srcMAC = long(pkts[i][1],16)
                        pkt.send_tslot = cnt
                        pkt.send_port = int(pkts[i][3],16)
                        pkt.send_dev = dpid
                pkt.rcvtime = cnt
                write_TD_MIB(pkt)

    print TD_MIB
    '''

    

'''
Created on Nov 4, 2014

@author: cc

ByPassManager Module
'''
import time
import threading
#import pox.openflow.libpof_01 as of
import pox.openflow.libopenflow_01 as of
import pox.lib.util
from pox.openflow import SyncTransUp
from pox.openflow import FeaturesReceived
from pox.openflow import ConnectionUp
from pox.openflow import PortStatus
from pox.openflow import GetConfigReply
from pox.openflow import ResourceReport
from pox.openflow import ErrorIn
from pox.openflow import PacketIn
from pox.openflow import ConnectionReady

from pox.core import core
from pox.openflow.libopenflow_01 import ofp_echo_request

log = core.getLogger()

def add_first_table(connection):
    msg =of.ofp_table_mod()  
    ofmatch20_1 =of.ofp_match20()
    ofmatch20_1.fieldId=1;
    ofmatch20_1.offset=0;
    ofmatch20_1.length=48;

    ofmatch20_3 =of.ofp_match20()
    ofmatch20_3.fieldId=3;
    ofmatch20_3.offset=96;
    ofmatch20_3.length=16;
   
    msg.flowTable.matchFieldList.append(ofmatch20_1)
    msg.flowTable.matchFieldList.append(ofmatch20_3)
  
    msg.flowTable.command=  0 #OFPTC_ADD
  
    msg.flowTable.tableType= 0 #OF_MM_TABLE
    
    #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
    msg.flowTable.tableSize=128
    msg.flowTable.tableId=0
    msg.flowTable.tableName="FirstEntryTable"
    msg.flowTable.keyLength=64  
    connection.send(msg)

def send_port_mod(connection):
    print"send port mod msg!\n" 
    msg = of.ofp_port_mod()
    num =  len(connection.phyports)
    for i in range(0,num):
	#print ('+++++++++++++++++++++') 
        portmessage = connection.phyports[i]
        msg.setByPortState(portmessage)
        msg.desc.openflowEnable = 1 
        msg.reason = 2
        connection.send(msg)


def handle_FEATURES_REPLY (con, msg):    #type:6
    print "receive Features_Reply message\n"
    connecting = con.connect_time == None       #connect_time = None as default, so connecting = ture
    #print ("con.connect_time:",con.connect_time)
    con.features = msg
    #con.dpid = msg.dev_id
    con.dpid=msg.deviceId   #according to tianye
    con.port_num_received = 0

    if not connecting:
        con.ofnexus._connect(con)
        e = con.ofnexus.raiseEventNoErrors(FeaturesReceived, con, msg)
        if e is None or e.halt != True:
            con.raiseEventNoErrors(FeaturesReceived, con, msg)
        return

    #OpenFlowConnectionArbiter is defined and registered in openflow.__init__.py
    nexus = core.OpenFlowConnectionArbiter.getNexus(con)    # nexus = core.openflow (class OpenFlowNexus)
    #print ('fun handle_FEATURES_REPLY --> nexus', nexus)    # cc
    if nexus is None:
        # Cancel connection
        con.info("No OpenFlow nexus for " + pox.lib.util.dpidToStr(msg.dev_id))
        con.disconnect()
        return
    con.ofnexus = nexus
    con.ofnexus._connect(con)    # self._connections[con.dpid] = con (in class OpenFlowNexus)
    #connections[con.dpid] = con

    #barrier = of.ofp_barrier_request()
    #con.send(barrier)
    getGonfigReq = of.ofp_get_config_request()

    listeners = []

    def finish_connecting (event):
        if event.xid != getGonfigReq.xid:
            con.dpid = None
            con.err("failed connect")
            con.disconnect()
        else:
            """
            con.info("connected")
            con.connect_time = time.time()
            e = con.ofnexus.raiseEventNoErrors(ConnectionUp, con, msg)
            if e is None or e.halt != True:
                con.raiseEventNoErrors(ConnectionUp, con, msg)
            """
            e = con.ofnexus.raiseEventNoErrors(FeaturesReceived, con, msg)
            if e is None or e.halt != True:
                con.raiseEventNoErrors(FeaturesReceived, con, msg)
        con.removeListeners(listeners)
    listeners.append(con.addListener(GetConfigReply, finish_connecting))
    
    def also_finish_connecting (event):
        if event.xid != getGonfigReq.xid: return
        if event.ofp.type != of.OFPET_BAD_REQUEST: return
        if event.ofp.code != of.OFPBRC_BAD_TYPE: return
        # Okay, so this is probably an HP switch that doesn't support barriers
        # (ugh).  We'll just assume that things are okay.
        finish_connecting(event)
    listeners.append(con.addListener(ErrorIn, also_finish_connecting))

    #TODO: Add a timeout for finish_connecting
    
    #print ('con.ofnexus.miss_send_len',con.ofnexus.miss_send_len)  #cc
    if con.ofnexus.miss_send_len is not None:
        #con.send(of.ofp_set_config(miss_send_len = con.ofnexus.miss_send_len))
        con.send(of.ofp_set_config(miss_send_len = 0xffff))

    con.send(getGonfigReq)

def handle_PORT_STATUS (con, msg):    # type:12
    print "receive PORT_STATUS message\n"
    if msg.reason == of.OFPPR_DELETE:
        con.ports._forget(msg.desc)
    else:
        con.ports._update(msg.desc)
        con.phyports.append(msg)
    e = con.ofnexus.raiseEventNoErrors(PortStatus, con, msg)
    if e is None or e.halt != True:
        con.raiseEventNoErrors(PortStatus, con, msg)
    
    con.port_num_received += 1
    if con.port_num_received == con.features.portNum:
        con.info("connected")
        con.connect_time = time.time()
        #add_first_table(con)
        #send_port_mod(con)
        #e = con.ofnexus.raiseEventNoErrors(ConnectionReady, con)  # modify by lsr
        #if e is None or e.halt != True:
        #   con.raiseEventNoErrors(ConnectionReady, con)
        print "connectionUp!!!\n"
        f = con.ofnexus.raiseEventNoErrors(ConnectionUp, con, msg)    # add by lsr
        if f is None or f.halt != True:
            con.raiseEventNoErrors(ConnectionUp, con, msg)

def send_echo_request(con):
    def send():
        con.send(ofp_echo_request())
        #print 'send echo request'
        #global t #Notice: use global variable!
        t = threading.Timer(2.0, send)
        t.start()
    t = threading.Timer(2.0, send)
    t.start()
    
def handle_RESOURCE_REPORT (con, msg):      # type:13
    print " receive RESOURCE_REPORT message\n"
    send_echo_request(con)
    e = con.ofnexus.raiseEventNoErrors(ResourceReport, con, msg)
    if e is None or e.halt != True:
        con.raiseEventNoErrors(ResourceReport, con, msg)
    pass


def handle_PACKET_IN (con, msg):   # type: 10
    print "CC: receive PACKET_IN message\n", msg
    
    e = con.ofnexus.raiseEventNoErrors(PacketIn, con, msg)
    if e is None or e.halt != True:
        con.raiseEventNoErrors(PacketIn, con, msg)


def handle_ERROR_MSG (con, msg):   # type: 1
    print "CC: receive RESOURCE_REPORT message\n",msg
    err = ErrorIn(con, msg)
    e = con.ofnexus.raiseEventNoErrors(err)
    if e is None or e.halt != True:
        con.raiseEventNoErrors(err)
    if err.should_log:
        log.error(str(con) + " OpenFlow Error:\n" +
              msg.show(str(con) + " Error: ").strip())

def handle_COUNTER_REPLY (con, msg):
    print "CC: receive COUNTER_REPLY message\n",msg


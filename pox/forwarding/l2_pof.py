# Copyright 2011 James McCauley
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

"""
An L2 learning switch.

It is derived from one written live for an SDN crash course.
It is somwhat similar to NOX's pyswitch in that it installs
exact-match rules for each flow.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import struct
import time

log = core.getLogger()

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0

def add_match_flow(l2,event,port,packet):
#trying to install a flow entry
   msg = of.ofp_flow_mod()
   msg.idle_timeout = 10
   msg.hard_timeout = 30
   
   #matchx :dst
   tempmatchx=of.ofp_matchx()
   tempmatchx.fieldId=1
   tempmatchx.offset=0
   tempmatchx.length=48        
   temps=packet.dst.toStr()        
   temps="".join(temps.split(':'))          
   tempmatchx.set_value(temps)        
   tempmatchx.set_mask("ff"*6)
   msg.matchx.append(tempmatchx)

   #need to new a ofp_matchx  do we need this???
   tempmatchx=of.ofp_matchx()
   tempmatchx.fieldId=3
   tempmatchx.offset=96
   tempmatchx.length=16
   tempmatchx.set_value("0000")
   tempmatchx.set_mask("0000")
   msg.matchx.append(tempmatchx) 
   
   #instruction
   tempins=of.ofp_instruction_applyaction()
   action=of.ofp_action_output()
   action.portId=port
   action.metadataOffset=0
   action.metadataLength=0
   action.packetOffset=0
   
   tempins.actionList.append(action)  
   msg.instruction.append(tempins)                
   #msg.match = of.ofp_match.from_packet(packet, event.port)

   #msg.actions.append(of.ofp_action_output(port = port))
   msg.data = event.ofp # 6a
   #print "6a:install table entry"
   l2.connection.send(msg) 
   
def add_drop_flow(l2,event,duration,packet):
   msg = of.ofp_flow_mod()
   #msg.match = of.ofp_match.from_packet(packet)
   msg.idle_timeout = duration[0]
   msg.hard_timeout = duration[1]
   msg.bufferId = event.ofp.bufferId
   #matchx
   tempmatchx=of.ofp_matchx()
   tempmatchx.fieldId=1
   tempmatchx.offset=0
   tempmatchx.length=48
   temps=packet.dst.toStr()
   temps="".join(temps.split(':'))  
   tempmatchx.set_value(temps)                
   tempmatchx.set_mask("ff"*6)
   msg.matchx.append(tempmatchx)

   tempmatchx=of.ofp_matchx()
   tempmatchx.fieldId=2
   tempmatchx.offset=48
   tempmatchx.length=48
   temps=packet.src.toStr()
   temps="".join(temps.split(':'))  
   tempmatchx.set_value(temps)                
   tempmatchx.set_mask("ff"*6)
   msg.matchx.append(tempmatchx)

   #need to new a ofp_matchx  do we need this???
   tempmatchx=of.ofp_matchx()
   tempmatchx.fieldId=3
   tempmatchx.offset=96
   tempmatchx.length=16
   tempmatchx.set_value("00")
   tempmatchx.set_mask("ff")
   msg.matchx.append(tempmatchx)
         


   tempins=of.ofp_instruction_applyaction()
   action=of.ofp_action_drop()                
   tempins.actionList.append(action)
   msg.instruction.append(tempins)        
   l2.connection.send(msg)    

def send_table_mod(event):
    msg =of.ofp_table_mod()  
    ofmatch20_1 =of.ofp_match20()
    ofmatch20_1.fieldId=1;
    ofmatch20_1.offset=0;
    ofmatch20_1.length=48;
  
    ofmatch20_2 =of.ofp_match20()
    ofmatch20_2.fieldId=2;
    ofmatch20_2.offset=48;
    ofmatch20_2.length=48;
  
    ofmatch20_3 =of.ofp_match20()
    ofmatch20_3.fieldId=3;
    ofmatch20_3.offset=96;
    ofmatch20_3.length=16;
  
    ofmatch20_4 =of.ofp_match20()
    ofmatch20_4.fieldId=4;
    ofmatch20_4.offset=112;
    ofmatch20_4.length=64;
  
    ofmatch20_5 =of.ofp_match20()
    ofmatch20_5.fieldId=5;
    ofmatch20_5.offset=176;
    ofmatch20_5.length=64;
  
    ofmatch20_6 =of.ofp_match20()
    ofmatch20_6.fieldId=6;
    ofmatch20_6.offset=240;
    ofmatch20_6.length=16;
  
    msg.flowTable.matchFieldList.append(ofmatch20_1)
    msg.flowTable.matchFieldList.append(ofmatch20_3)
  
    msg.flowTable.command=of.OFPTC_ADD
  
    msg.flowTable.tableType=of.OF_MM_TABLE
    
    #test_port_mod(event)
  
  #msg.flowTable.matchFieldNum=len(msg.flowTable.matchFieldList)
    msg.flowTable.tableSize=128
    msg.flowTable.tableId=0
    msg.flowTable.tableName="FirstEntryTable"
    msg.flowTable.keyLength=64  
    event.connection.send(msg)
    
    
def send_port_mod(event):  
    msg = of.ofp_port_mod()
    num =  len(event.connection.phyports)
    for i in range(0,num):
        portmessage = event.connection.phyports[i]
        msg.setByPortState(portmessage)
        msg.desc.openflowEnable = 1 
        msg.reason = 2
        event.connection.send(msg)



class LearningSwitch (object):
  """
  The learning switch "brain" associated with a single OpenFlow switch.

  When we see a packet, we'd like to output it on a port which will
  eventually lead to the destination.  To accomplish this, we build a
  table that maps addresses to ports.

  We populate the table by observing traffic.  When we see a packet
  from some source coming from some port, we know that source is out
  that port.

  When we want to forward traffic, we look up the desintation in our
  table.  If we don't know the port, we simply send the message out
  all ports except the one it came in on.  (In the presence of loops,
  this is bad!).

  In short, our algorithm looks like this:

  For each packet from the switch:
  1) Use source address and switch port to update address/port table
  2) Is transparent = False and either Ethertype is LLDP or the packet's
     destination address is a Bridge Filtered address?
     Yes:
        2a) Drop packet -- don't forward link-local traffic (LLDP, 802.1x)
            DONE
  3) Is destination multicast?
     Yes:
        3a) Flood the packet
            DONE
  4) Port for destination address in our address/port table?
     No:
        4a) Flood the packet
            DONE
  5) Is output port the same as input port?
     Yes:
        5a) Drop packet and similar ones for a while
  6) Install flow table entry in the switch so that this
     flow goes out the appopriate port
     6a) Send the packet out appropriate port
  """
  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Our table
    self.macToPort = {}

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)

    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    #log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))

  def _handle_PacketIn (self, event):
    """
    Handle packet in messages from the switch to implement above algorithm.
    """
    #print "receive a packetin msg."
     
    packet = event.parsed
    def flood (message = None):
      """ Floods the packet """
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        # Only flood if we've been connected for a little while...

        if self.hold_down_expired is False:
          # Oh yes it is!
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
        # OFPP_FLOOD is optional; on some switches you may need to change
        # this to OFPP_ALL.
        msg.actions.append(of.ofp_action_output(portId = 255))
      else:
        pass
        #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
      msg.data = event.ofp
      #msg.in_port = event.port
      msg.inPort = event.port
      self.connection.send(msg)

    def drop (duration = None):
      """
      Drops this packet and optionally installs a flow to continue
      dropping similar ones for a while
      """
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        add_drop_flow(self,event, duration, packet)
        
      elif event.ofp.bufferId is not None:
        #print ('-----------------------')
        msg = of.ofp_packet_out()
        msg.bufferId = event.ofp.bufferId
        msg.inPort = event.port
        msg.actions.append(of.ofp_action_drop())  #need to add?
        self.connection.send(msg)
    
    if packet.type == packet.LLDP_TYPE or packet.type == 0x0980:
        self.macToPort[packet.src] = event.port # 1
        
        if not self.transparent: # 2
          if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
            #print "2a:LLDP_TYPE or Bridge"
            drop() # 2a
            return
    
        if packet.dst.is_multicast:
          #print ("Src: %s---Dst: %s---Port: %s" % (packet.src, packet.dst,event.port))
          #print "3a:dst.is_multicast"
          #addflow(self, event, 3, packet)
          flood() # 3a
        else:
          if packet.dst not in self.macToPort: # 4
            #print ("Port for %s unknown -- flooding" % (packet.dst,))
            flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
          else:
            port = self.macToPort[packet.dst]
            if port == event.port: # 5
              # 5a
              log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
                  % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
              drop(3000)
              return
            # 6
            log.debug("installing flow for %s.%i -> %s.%i" %
                      (packet.src, event.port, packet.dst, port))
            #print ("installing flow for %s.%i -> %s.%i" %
                      #(packet.src, event.port, packet.dst, port))
            add_match_flow(self,event, port, packet)
            '''
            we need ofp_packet_out to forward the message after(or before)
            installing the match flow entry, because it will match the flow
            entry at the next time when recieves the similar message, and
            then forwards the message.
            '''
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(portId = port))
            msg.data = event.ofp
            msg.inPort = event.port
            self.connection.send(msg)
    

class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,)) 
    #send_table_mod(event)
    #send_port_mod(event)   
    LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))

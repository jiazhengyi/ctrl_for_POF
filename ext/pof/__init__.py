
"""
This allows you to easily run POFDesk.
"""
from BaseHTTPServer import *
from pox.core import core
import os.path
from pox.web.webcore import *
import cgi
import template
from pox.lib.util import dpidToStr
from pox.openflow.gui_to_pofmanager import *

import string
###################################################################
global ovs_switches
global links
global protocol#just to sava a protocol
global protocols#to save all protocols
global protocol_name
global table_matchs
global offset
global Metadata
#global entry_id
global table_match
#global table_id
global Tables
global ports
global showtables
global portsinfo
ports=[]
Tables={}
#entry_id=0
Metadata=[]
offset=0
table_matchs=[]
protocol=[]
protocols={}
protocol_name=""
table_match={}
#table_id={}
Tables={}
showtables={}

###################################################
# Metadata=[('Packet length', 16, 0), ('Input port', 8, 16), ('Rsvd', 8, 24), ('VpnID', 16, 32)]
# protocol_name='ETH'
# protocols={'ETH+IPv4': [('Dmac', 48, 0), ('Smac', 48, 48), ('Type', 16, 96), ('V', 4, 112), ('IHL', 4, 116), ('TOS', 8, 120), ('TotalLength', 16, 128), ('TTL', 8, 144), ('protocol', 16, 152), ('checksum', 16, 168), ('SIP', 32, 184), ('DIP', 32, 216)], 'ETH': [('Dmac', 48, 0), ('Smac', 48, 48), ('Type', 16, 96)]}
# table_matchs=[{'table_type': 'OF_MM_TABLE', 'protocol_name': 'ETH', 'table_name': 'aaa', 'entry_id': 1, 'match': [('Smac', 48, 48, 'AAAAAAAAAAAA', 'ffffffffffff'), ('VpnID', 16, 32, 'AAAA', 'ffff')]}, {'table_type': 'OF_LMP_TABLE', 'protocol_name': 'ETH', 'table_name': 'bbb', 'entry_id': 1, 'match': [('Type', 16, 96, 'BBBB', 'ffff'), ('VpnID', 16, 32, 'BBBB', 'ffff')]}]
# table_match={'table_type': 'OF_MM_TABLE', 'protocol_name': 'ETH', 'table_name': 'aaa', 'entry_id': 1, 'match': [('Smac', 48, 48, 'AAAAAAAAAAAA', 'ffffffffffff'), ('VpnID', 16, 32, 'AAAA', 'ffff')]}
# Tables={'1106784049': [{'instruction': {'apply_action': {'output': [{'output': '1', 'packet_offset': '', 'metadata_offset': '', 'metadata_length': ''}]}}, 'priority': '11', 'table_id': 1, 'entry_name': '11', 'Table_entry': {'table_type': 'OF_MM_TABLE', 'protocol_name': 'ETH', 'table_name': 'aaa', 'entry_id': 1, 'match': [('Smac', 48, 48, 'AAAAAAAAAAAA', 'ffffffffffff'), ('VpnID', 16, 32, 'AAAA', 'ffff')]}, 'size': '11'}, {'instruction': {'goto_table': [{'table_id': '1:11', 'offset': ''}]}, 'priority': '22', 'table_id': 2, 'entry_name': '22', 'Table_entry': {'table_type': 'OF_MM_TABLE', 'protocol_name': 'ETH', 'table_name': 'aaa', 'entry_id': 1, 'match': [('Smac', 48, 48, 'AAAAAAAAAAAA', 'ffffffffffff'), ('VpnID', 16, 32, 'AAAA', 'ffff')]}, 'size': '22'}], '1106950613': [{'instruction': {'write_metadata': [{'value': 'AAAA', 'metadata': 'Packet length;16'}]}, 'priority': '33', 'table_id': 1, 'entry_name': '33', 'Table_entry': {'table_type': 'OF_MM_TABLE', 'protocol_name': 'ETH+IPv4', 'table_name': 'aaa', 'entry_id': 1, 'match': [('V', 4, 112, 'A', 'f'), ('checksum', 16, 168, 'AAAA', 'ffff')]}, 'size': '33'}, {'instruction': {'goto_table': [{'table_id': '1:33', 'offset': ''}]}, 'priority': '44', 'entry_name': '44', 'table_id': 2, 'Table_entry': {'table_type': 'OF_MM_TABLE', 'protocol_name': 'ETH', 'table_name': 'aaa', 'entry_id': 1, 'match': [('Smac', 48, 48, 'AAAAAAAAAAAA', 'ffffffffffff'), ('VpnID', 16, 32, 'AAAA', 'ffff')]}, 'size': '44'}]}
###################################################################
'''
this class aims to define the relationship between webpath and local path
'''
class POFdesk():
  #httpd = core.WebServer
  def __init__ (self):
        global ovs_switches
        global links
        global portsinfo
        #global table_id
        ovs_switches=set()
        links=set()
        portsinfo={}
        core.listen_to_dependencies(self)
        httpd = core.WebServer
#######################################################################
#         www_path="/topo/static"
#         local_path=path_prase('template/static')
#         httpd.set_handler(www_path, StaticContentHandler,
#                      {'root':local_path}, True);
#########################################################################
        #httpd = core.WebServer
        #self.httpd.add_static_dir('test', 'test', relative=True)
#         self.add_static_dir('test', 'test', relative=True)
#        httpd.add_static_dir('test', 'test', relative=True)#webcore
        local_path=path_prase('template')
        www_path="/test/"
        httpd.set_handler(www_path, testhandler,
                          {'root':local_path}, True);#set handler      
        www_path="/Spectrum/"
        httpd.set_handler(www_path, slothandler,
                          {'root':local_path}, True);#set handler
        www_path="/topo/"
        httpd.set_handler(www_path,topohandler,
                     {'root':local_path}, True);
        www_path="/protocol/"
        httpd.set_handler(www_path,protocolhandler,
                     {'root':local_path}, True);
        www_path="/table/"
        httpd.set_handler(www_path,tablehandler,
                     {'root':local_path}, True);
        www_path="/port/"
        httpd.set_handler(www_path,porthandler,
                      {'root':local_path},True)
        print "the url has been built!--hdy"
  def _handle_openflow_ConnectionUp (self, event):
      #to find new switch up!
    global ovs_switches
    #global table_id
    global Tables
    global portsinfo
    #portsinfo[dpidToStr(event.dpid)]=event.connection.phyports
    print event.dpid
    ss=dpidToStr(event.dpid)
    portsinfo[ss]=event.connection.phyports
    #table_id[ss]=0
    Tables[ss]=[]
    ovs_switches.add(dpidToStr(event.dpid))
  def _handle_openflow_ConnectionDown (self, event):
      #find a switch connection down!
    global ovs_switches
    #global table_id
    global Tables
    global ports
    global portsinfo
    #ovs_switches.remove(dpidToStr(event.dpid))
    ss=dpidToStr(event.dpid)
    ovs_switches.remove(ss)
    #table_id.pop(ss)
    Tables.pop(ss)
    for port in ports:
        if port[0]==ss:
            ports.remove(port)

  def _handle_openflow_PortStatus (self, event):
    """
    Track changes to switch ports
    """
    global ports
    mac=dpidToStr(event.dpid)
    ports.append((mac,event.port))
         
  def _handle_openflow_discovery_LinkEvent (self, event):
      #find topolink!
      global links
      s1 = event.link.dpid1
      s2 = event.link.dpid2
      if s1 > s2: s1,s2 = s2,s1
      s1 = dpidToStr(s1)
      s2 = dpidToStr(s2)
      if event.added:
        links.add((s1,s2))
      elif event.removed and (s1,s2) in links:
        links.remove((s1,s2))

def path_prase(local_path):
#find the real path
    import inspect
    path = inspect.stack()[1][1]
    path = os.path.dirname(path)
    local_path = os.path.join(path, local_path)
    local_path = os.path.abspath(local_path)
    #print local_path
    return local_path
    
def OnlyStr(s,oth=''):
    s=str(s)
    fomart = 'abcdefghijklmnopqrstuvwxyz0123456789'
    for c in s:
        if not c in fomart:
            s = s.replace(c,'');
    return s;
class testhandler(StaticContentHandler):
  """
  A test page for POFdesk.
  """
#   def __init__ (self):
#       self.name=''
  def do_GET (self):
    print "get--hdy"
    slot="0000000000111111111110101010111111111111100000000000"
    if self.path.startswith('/static/'):
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #load static source
    else:
        path=path_prase('template')
        render = template.render(path)
        f=render.index(slot)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(f)
    
  def do_POST (self):
    print "it's a post"
    #print post_content
    slot="0000000000111111111110101010111111111111100000000000"
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type'],
          })
    path=path_prase('template')
    render = template.render(path)
    f=render.index(slot)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(f)
    
    
# class topohandler(StaticContentHandler):
#   """
#   topology page handler
#   """
#   def do_GET (self): 
#         global ovs_switches
#         global links
#         if self.path.startswith('/static/'):
#             SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #load static source
#         else:
#                     x=("111","42","126","184","412","291","681","418","540","669","675","876","896","766")
#                     y=("45","202","351","193","379","274","392","234","209","191","43","46","227","306")    
#                     i=0
#                     jsonStr=""
#                     for switch in ovs_switches:
#                         #m_dpid= str(dpid)
#                         m=x[i]
#                         n=y[i]
#                         if i==0:
#                             jsonStr+='{"devices":[{"id":"'+switch+'","name":"switch ","src":"static/img/Router_Icon_128x128.png","x":'+m+',"y":'+n+',"width":62,"height":30}'
#                             i+=1
#                         else:
#                             jsonStr+=',{"id":"'+switch+'","name":"switch ","src":"static/img/Router_Icon_128x128.png","x":'+m+',"y":'+n+',"width":62,"height":30}'
#                             i+=1
#                     jsonStr+=']'
#                     i=0
#                     if links:
#                         for link in links:
#                             if i == 0:
#                                jsonStr+=',"lines":[{"srcDeviceId":"'+link[0]+'","dstDeviceId":"'+link[1]+'","stroke":"black","strokeWidth":2}'
#                                i+=1
#                             else:
#                                 jsonStr+=',{"srcDeviceId":"'+link[0]+'","dstDeviceId":"'+link[1]+'","stroke":"black","strokeWidth":2}'
#                                 i+=1
#                         jsonStr+=']}'
#                     else:
#                         jsonStr+='}'
#                     path=path_prase('template')
#                     render = template.render(path)
#                     s=render.topo(jsonStr)
#                     s=str(s)
#                     s=s.replace('&quot;', '"')#translate &quot into "
#                     self.send_response(200)
#                     self.send_header('Content-type','text/html')
#                     self.end_headers()
#                     self.wfile.write(s)
#   def do_POST (self):
#     #print post_content
#     form = cgi.FieldStorage(
#       fp=self.rfile,
#       headers=self.headers,
#       environ={'REQUEST_METHOD':'POST',
#           'CONTENT_TYPE':self.headers['Content-Type'],
#           })

class topohandler(StaticContentHandler):
  """
  topology page handler
  """
  def do_GET (self): 
        global ovs_switches
        global links
        print "it is topo get"
        if self.path.startswith('/static/'):
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #load static source
        else:   
            i=0
            jsonStr=""
            for switch in ovs_switches:
#                 switchstr=dpidToStr(switch)
#                 switchint=string.atoi(switch)
#                 switchstr=dpidToStr(switchint)
                #m_dpid= str(dpid)
                if i==0:
                   # jsonStr+='{"devices":[{"id":"'+switch+'","name":"switch ","src":"static/img/Router_Icon_128x128.png","x":'+m+',"y":'+n+',"width":62,"height":30}'
                    jsonStr+='{"device":[{"id":"'+switch+'"}'
                    i+=1
                else:
                    #jsonStr+=',{id:'+switch+'}'
                    jsonStr+=',{"id":"'+switch+'"}'
                    i+=1
            jsonStr+=']'
            i=0
            if links:
                for link in links:
                    if i == 0:
                       #jsonStr+=',"lines":[{"srcDeviceId":"'+link[0]+'","dstDeviceId":"'+link[1]+'","stroke":"black","strokeWidth":2}'
                       jsonStr+=',"links":[{"source":"'+link[0]+'","target":"'+link[1]+'"}'
                       i+=1
                    else:
                        jsonStr+=',{"source":"'+link[0]+'","target":"'+link[1]+'"}'
                        i+=1
                jsonStr+=']}'
            else:
                jsonStr+='}'   
            #jsonStr='{"device":[{"id":"s1"},{"id":"s2"},{"id":"s3"},{"id":"s4"}],"links":[{"source":"s1","target":"s2"},{"source":"s2","target":"s3"},{"source":"s2","target":"s4"}]}'
            path=path_prase('template')
            render = template.render(path)
            s=render.topology(jsonStr)
            
            s=str(s)
            s=s.replace('&quot;', '"')#translate &quot into "
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(s)
                    
  def do_POST (self):
    #print post_content
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type'],
          })
    print form.getvalue('post_content')
class protocolhandler(StaticContentHandler):
    """
    topology page handler
    """
    global ovs_switches
    def do_GET(self):
        global ports
        pro_num=0
        for key in protocols.keys():
            pro_num+=1
        if self.path.startswith('/static/'):
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #load static source
        else:
            path=path_prase('template')
            render = template.render(path)
            s=render.protocol(protocols,protocol,protocol_name,ovs_switches,pro_num,table_matchs,table_match,Metadata,Tables,ports)           
            s=str(s)
            s=s.replace('&quot;', '"')#translate &quot into "
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(s) 
    def do_POST (self):
        global protocol
        global protocols
        global protocol_name
        global table_matchs
        global offset
        global Metadata
        #global entry_id
        global table_match
        #global table_id
        global Tables
        pro_num=0
        print "it's a post"
        #print post_content
        form = cgi.FieldStorage(
          fp=self.rfile,
          headers=self.headers,
          environ={'REQUEST_METHOD':'POST',
              'CONTENT_TYPE':self.headers['Content-Type'],
              })
##############to save the fields###############################
        if(form.getvalue('fieldname') and form.getvalue('fieldlength')):
            name=form.getvalue('fieldname')
            length=int(form.getvalue('fieldlength'))
            field=(name,length,offset)
            protocol.append(field)
            offset+=length
##############t#to process the operation of the field###############################
        if(form.getvalue('fielddelete')):
            protocol=[]
##############to save the protocol###############################
        if(form.getvalue('saveprotocol') and form.getvalue('protocolname') and protocol):
            if (form.getvalue('protocolname')=='Metadata'):
                Metadata=protocol
            else:
                protocols[form.getvalue('protocolname')]=protocol
                #to add protocol
                add_new_protocol(form.getvalue('protocolname'),protocol)
            protocol=[]
            offset=0
##############to process the operation of the protocol
        if(form.getvalue("saveoperation")):
            for key in protocols.keys():
                pro_num+=1
                if(form.getvalue(key)=="delete"):
                    protocols.pop(key)
                    if protocol_name==key:
                        protocol_name=""
                        table_match={}
                if(form.getvalue(key)=="add table"):
                    if(table_match):
                        if(table_match['protocol_name']!=key):
                            table_match={}
                    protocol_name=key
###************to process the table*********************************
        if(form.getvalue('table')):
            #entry_id=entry_id+1
            Entry_name=form.getvalue('Entry_Name')
            entry_id=form.getvalue('Entry_ID')
            table_type=form.getvalue('Table_Type')
            match=[]
            for field in protocols[protocol_name]:
                value=form.getvalue(field[0]+'_value')
                mask=form.getvalue(field[0]+'_mask')
                if mask:
                    match.append((field[0],field[1],field[2],value,mask))
            for field in Metadata:
                value=form.getvalue(field[0]+'_value')
                mask=form.getvalue(field[0]+'_mask')
                if mask:
                    match.append((field[0],field[1],field[2],value,mask))
            Table_entry={}
            Table_entry['entry_name']=Entry_name
            Table_entry['table_type']=table_type
            Table_entry['match']=match
            Table_entry['entry_id']=entry_id
            Table_entry['protocol_name']=protocol_name
            table_matchs.append(Table_entry)
###################to add table entry######################################
        if(form.getvalue('tablesubmit')):
            for table in table_matchs:
                if(form.getvalue(str(table['entry_name'])+str(table['entry_id']))=='delete'):
                    table_matchs.remove(table)
                    if(table_match==table):
                        table_match={}
                if(form.getvalue(str(table['entry_name'])+str(table['entry_id']))=='add_instruction'):
                    table_match=table
###################to add table entry########################################
        if(form.getvalue('addtableentrysubmit')):
            instruction=form.getvalue('submitinstruction')
            switch=form.getvalue('switch')
            table_ID=form.getvalue('Table_ID')
            table_ID=string.atoi(table_ID)
            priority=form.getvalue('Table_priority')
            size=form.getvalue('Table_Size')
            table_name=form.getvalue('table_name')
            #table_id[switch]=table_id[switch]+1
            instruction=eval(instruction)
            for key in  instruction['apply_action'].keys():
                if not instruction['apply_action'][key]:
                    del instruction['apply_action'][key]
            for key in instruction.keys():
                if not instruction[key]:
                    del instruction[key]
            table={}  
            table['priority']=priority
            table['size']=size
            #table['table_id']=table_id[switch]
            table['table_id']=table_ID
            table['Table_entry']=table_match
            table['instruction']=instruction
            table['table_name']=table_name
            Tables[switch].append(table)
            #to add table
            switch=OnlyStr(switch)
            switch=int(switch,16)
            print switch
            add_flowtable_flowmod(switch,table)
            print Tables
###################to send message to HTML#################################
        path=path_prase('template')
        render = template.render(path)
        f=render.protocol(protocols,protocol,protocol_name,ovs_switches,pro_num,table_matchs,table_match,Metadata,Tables,ports)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f)
class tablehandler(StaticContentHandler):
    """
    topology page handler
    """
    def do_GET(self):
        print "it's a get"
        global showtables
        if self.path.startswith('/static/'):
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #load static source
        else:
            if not showtables:
                showtables=Tables
            path=path_prase('template')
            render = template.render(path)
            s=render.table(showtables,ovs_switches,protocols)           
            s=str(s)
            s=s.replace('&quot;', '"')#translate &quot into "
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(s)
    def do_POST (self):
        global protocols
        global Tables
        global ovs_switches
        global showtables
        print "it's a post"
        #print post_content
        form = cgi.FieldStorage(
          fp=self.rfile,
          headers=self.headers,
          environ={'REQUEST_METHOD':'POST',
              'CONTENT_TYPE':self.headers['Content-Type'],
              })
        if form.getvalue('search'):
            device=form.getvalue('switch')
            protocolname=form.getvalue('protocol')
            showtables={}
            if device and protocolname:
                table=Tables[device]
                showtables[device]=[]
                for m in table:
                    if m['Table_entry']['protocol_name']==protocolname:
                        showtables[device].append(m)
            elif device and not protocolname:
                table=Tables[device]
                showtables[device]=[]
                showtables[device]=table
            elif not device and protocolname:
                for key in Tables:
                    showtables[key]=[]
                    for m in Tables[key]:
                        if m['Table_entry']['protocol_name']==protocolname:
                            showtables[key].append(m)
            else:
                showtables=Tables
                
        if form.getvalue('delete'):
            for key in Tables.keys():
                if form.getvalue(key):
                    for table in Tables[key]:
                        tableid=str(table['table_id'])
                        entryid=str(table['Table_entry']['entry_id'])
                        if form.getvalue('table_id')==tableid and form.getvalue('entry_id')==entryid:
                            Tables[key].remove(table)
                            print "table remove"
                            key=OnlyStr(key)
                            key=int(key,16)
                            table_id=string.atoi(tableid)
                            entry_id=string.atoi(entryid)
                            print key
                            print entry_id
                            print table_id
                            #print 'before delete'
                            #del_flow_table(key,table_id)
                            #del_flow_entry(key, table_id, entry_id)
                            del_flow_entry(key, table_id, entry_id)
                            break
                    break
        path=path_prase('template')
        render = template.render(path)
        f=render.table(showtables,ovs_switches,protocols)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f)
class porthandler(StaticContentHandler):
   
    #ports info page handler
    
    def do_GET(self):
        global ovs_switches
        global portsinfo
		#print portsinfo
        print "it is port get"
        jsonStr=""
        if self.path.startswith('/static'):
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        else:
            jsonStr='{'
            i=0
            for switch in ovs_switches:
                if(i==0):
                    jsonStr+='"'+switch+'":'
                    i+=1
                else:
                    jsonStr+=',"'+switch+'":' 
                j=0
                for p in portsinfo[switch]:
                    if j==0:
                        jsonStr+='[{"deviceId":"'+dpidToStr(p.desc.deviceId)+'","portId":"'+str(p.desc.portId)+'","hardwareAddress":"'+str(p.desc.hardwareAddress)+'","name":"'+str(p.desc.name)+'","config":"'+str(p.desc.config)+'","state":"'+str(p.desc.state)+'","currentFeatures":"'+str(p.desc.currentFeatures)+'","advertisedFeatures":"'+str(p.desc.advertisedFeatures)+'","supportedFeatures":"'+str(p.desc.supportedFeatures)+'","peerFeatures":"'+str(p.desc.peerFeatures)+'","currentSpeed":"'+str(p.desc.currentSpeed)+'","maxSpeed":"'+str(p.desc.maxSpeed)+'","openflowEnable":"'+str(p.desc.openflowEnable)+'"}'
                        j+=1
                    else:
                        jsonStr+=',{"deviceId":"'+dpidToStr(p.desc.deviceId)+'","portId":"'+str(p.desc.portId)+'","hardwareAddress":"'+str(p.desc.hardwareAddress)+'","name":"'+str(p.desc.name)+'","config":"'+str(p.desc.config)+'","state":"'+str(p.desc.state)+'","currentFeatures":"'+str(p.desc.currentFeatures)+'","advertisedFeatures":"'+str(p.desc.advertisedFeatures)+'","supportedFeatures":"'+str(p.desc.supportedFeatures)+'","peerFeatures":"'+str(p.desc.peerFeatures)+'","currentSpeed":"'+str(p.desc.currentSpeed)+'","maxSpeed":"'+str(p.desc.maxSpeed)+'","openflowEnable":"'+str(p.desc.openflowEnable)+'"}'
                jsonStr+=']'
            jsonStr+='}'
        #print jsonStr
        #jsonStr=jsonStr.replace('\'','')
        path=path_prase('template')
        render = template.render(path)
        try:
            s=render.port(jsonStr,ovs_switches)
            s=str(s)
            s=s.replace("&#39;","'")
            s=s.replace('&quot;','"')
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(s)
        except Exception,e:
            self.wfile._sock.close()
            self.wfile._sock=None
    def do_POST (self):
    #print post_content
        form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                'CONTENT_TYPE':self.headers['Content-Type'],
                })
        print form.getvalue('post_content')
class slothandler(StaticContentHandler):
  """
  A test page for POFdesk.
  """
#   def __init__ (self):
#       self.name=''
  def do_GET (self):
    print "get--hdy"
    slot="0000000000111111111110101010111111111111100000000000"
    if self.path.startswith('/static/'):
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self) #load static source
    else:
        path=path_prase('template')
        render = template.render(path)
        f=render.slot(slot)
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(f)
    
  def do_POST (self):
    print "it's a post"
    #print post_content
    slot="0000000000111111111110101010111111111111100000000000"
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type'],
          })
    path=path_prase('template')
    render = template.render(path)
    f=render.slot(slot)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(f)
def launch ():
    #core.call_when_ready(_start_pofdesk, ["WebServer","MessengerNexus_of_service"])
    core.registerNew(POFdesk)
    #app=web.application(urls, globals())
    #app.run()

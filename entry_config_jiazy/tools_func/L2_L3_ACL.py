import struct

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from time import sleep
import binascii

import assist_func as af

log = core.getLogger()

'''
switch (179) eth1 -> Ixia
switch (179) eth2 -> Ixia
L2 Parse (MM) -> L3 Parse (MM) -> Routable (MM) -> L3 Forward (LPM) -> ACL (MM) -> L2 Forward (MM)
 TableID: 0                1                2                  0            3                  4
GTableID: 0                1                2                  10           3                  4
'''

g_fields = {
    "dmac":     [      0,   0,  48, ],
    "smac":     [      1,  48,  48, ],
    "etype":    [      2,  96,  16, ],
    "iphead":   [      3, 112, 160, ],
    "ttl":      [      4, 176,   8, ],
    "proto":    [      5, 184,   8, ],
    "checksum": [      6, 192,  16, ],
    "sip":      [      7, 208,  32, ],
    "dip":      [      8, 240,  32, ],
    "sport":    [      9, 272,  16, ],
    "dport":    [     10, 288,  16, ],
    "inport":   [ 0xFFFF,  16,   8, ],
}

g_tables = {
      "L2 Parse": [ of.OF_MM_TABLE,  0,  0, [ "etype" ], 8 ],
      "L3 Parse": [ of.OF_MM_TABLE,  1,  1, [ "proto" ], 8 ],
      "Routable": [ of.OF_MM_TABLE,  2,  2, [ "inport", "dmac" ], 32 ],
    "L3 Forward": [ of.OF_LPM_TABLE, 0, 10, [ "dip" ], 10241 ],
           "ACL": [ of.OF_MM_TABLE,  3,  3, [ "proto", "sip", "dip", "sport", "dport" ], 2000 ],
    "L2 Forward": [ of.OF_MM_TABLE,  4,  4, [ "inport", "dmac" ], 32 ],
}

g_entries = {
    "L2 Parse": [
        [ 1, 0, 0,
         { "etype": [ "0800", "FFFF", ], },
         [ [ "GOTO_TABLE", "L3 Parse", ], ], ],
        [ 0, 1, 1,
         { "etype": [ "0000", "0000", ], },
         [ [ "GOTO_TABLE", "L2 Forward", ], ], ],
    ],
    "L3 Parse": [
        [ 1, 0, 2,
         { "proto": [ "06", "FF", ], },
         [ [ "GOTO_TABLE", "Routable", ], ], ],
        [ 1, 1, 2,
         { "proto": [ "11", "FF", ], },
         [ [ "GOTO_TABLE", "Routable", ], ], ],
        [ 0, 2, 3,
         { "proto": [ "00", "00", ], },
         [ [ "GOTO_TABLE", "L2 Forward", ], ], ],
    ],
    "Routable": [
        [ 0, 0, 4,
         { "inport": [ "00", "00", ], "dmac": [ "000000000000", "000000000000", ], },
         [ [ "GOTO_TABLE", "L3 Forward", ], ], ],
    ],
    "L3 Forward": [
        [ 0, 10240, 5,
         { "dip": [ "00000000", "00000000", ], },
         [ [ "APPLY_ACTIONS", [ [ "MODIFY_FIELD", "ttl", -1, ], [ "CALCULATE_CHECKSUM", "iphead", "checksum", ], [ "GROUP", 0, ], ], ], [ "GOTO_TABLE", "ACL", ], ], ],
    ],
    #  "ACL": [
        #  [ 1, 0, 6,
         #  { "proto": [ "06", "FF", ], "sip": [ "C0A80000", "FFFF0000", ], "dip": [ "C0A80000", "FFFF0000", ], "sport": [ "0000", "0000", ], "dport": [ "0000", "0000", ], },
         #  [ [ "GOTO_TABLE", "L2 Forward", ], ], ],
        #  [ 0, 1, 7,
         #  { "proto": [ "00", "00", ], "sip": [ "00000000", "00000000", ], "dip": [ "00000000", "00000000", ], "sport": [ "0000", "0000", ], "dport": [ "0000", "0000", ], },
         #  [ [ "APPLY_ACTIONS", [ [ "DROP", ], ], ], ], ],
    #  ],
    "L2 Forward": [
        [ 2, 0, 8,
         { "inport": [ "02", "FF", ], "dmac": [ "000000000000", "000000000000", ], },
         [ [ "APPLY_ACTIONS", [ [ "OUTPUT", 3, ], ], ], ], ],
        [ 1, 1, 8,
         { "inport": [ "03", "FF", ], "dmac": [ "000000000000", "000000000000", ], },
         [ [ "APPLY_ACTIONS", [ [ "OUTPUT", 2, ], ], ], ], ],
        [ 0, 2, 8,
         { "inport": [ "00", "00", ], "dmac": [ "000000000000", "000000000000", ], },
         [ [ "APPLY_ACTIONS", [ [ "OUTPUT", 2, ], ], ], ], ],
         #  [ [ "APPLY_ACTIONS", [ [ "DROP", ], ], ], ], ],
    ],
}

g_groups = {
    0: [
        [ "SET_FIELD", "smac", "7824AFC963C6", "FFFFFFFFFFFF", ],
        [ "SET_FIELD", "dmac", "7824AFC963C5", "FFFFFFFFFFFF", ],
    ],
}

def generate_l3_forward_instructions(nexthop):
    inss = []
    inss_info = [
        [ "APPLY_ACTIONS",
         [
            [ "MODIFY_FIELD", "ttl", -1, ],
            [ "CALCULATE_CHECKSUM", "iphead", "checksum", ],
            [ "GROUP", 0, ],
            #  [ "GROUP", int(nexthop), ],
         ],
        ],
        [ "GOTO_TABLE", "ACL", ],
    ]

    for ins_info in inss_info:
        ins = af.generate_instruction(ins_info, g_tables, g_fields)
        inss.append(ins)

    return inss

def generate_l3_forward_entry(priority, index, line, file_info, table_dict, field_dict):
    paras = line.split(file_info[1])
    table = table_dict[file_info[2]]
    msgs = []
    msg = of.ofp_flow_mod(tableType=table[0],
                          tableId=table[1],
                          priority=priority,
                          index=index,
                          counterId=file_info[3])
    matchx = af.generate_matchx_from_IP_subnet(field_dict["dip"], paras[0])
    msg.matchx.append(matchx)
    inss = generate_l3_forward_instructions(paras[1])
    for ins in inss:
        msg.instruction.append(ins)
    msgs.append(msg)
    return msgs

def generate_acl_instructions(nexthop):
    inss = []
    inss_info = [ [ "GOTO_TABLE", "L2 Forward", ], ]
    for ins_info in inss_info:
        ins = af.generate_instruction(ins_info, g_tables, g_fields)
        inss.append(ins)

    return inss

def generate_acl_entry(priority, index, line, file_info, table_dict, field_dict):
    paras = line.split(file_info[1])
    table = table_dict[file_info[2]]
    msgs = []

    matchx_sip = af.generate_matchx_from_IP_subnet(field_dict["sip"], paras[0])
    matchx_dip = af.generate_matchx_from_IP_subnet(field_dict["dip"], paras[1])
    matchxies_sport = af.generate_matchxies_from_port_range(field_dict["sport"], paras[2])
    matchxies_dport = af.generate_matchxies_from_port_range(field_dict["dport"], paras[3])
    matchx_proto = af.generate_matchx_from_proto(field_dict["proto"], paras[4])
    inss = generate_acl_instructions(paras[5])

    for matchx_sport in matchxies_sport:
        for matchx_dport in matchxies_dport:
            msg = of.ofp_flow_mod(tableType=table[0],
                                  tableId=table[1],
                                  priority=priority,
                                  index=index,
                                  counterId=file_info[3])
            msg.matchx.append(matchx_sip)
            msg.matchx.append(matchx_dip)
            msg.matchx.append(matchx_sport)
            msg.matchx.append(matchx_dport)
            msg.matchx.append(matchx_proto)
            for ins in inss:
                msg.instruction.append(ins)
            msgs.append(msg)
            index = index + 1
    return msgs

g_files = {
    "bgp20021201f.pref": [ generate_l3_forward_entry, "\t", "L3 Forward", 5, ],
    "acl2_seed_1.rules": [ generate_acl_entry, "\t", "ACL", 6, ],
}

def install_groups(event):
    for index in g_groups.keys():
        msg = of.ofp_group_mod()
        msg.groupId = index
        for act_info in g_groups[index]:
            act = af.generate_action(act_info, g_fields)
            msg.actions.append(act)
        event.connection.send(msg)

def install_tables(event):
    for table_name in g_tables.keys():
        msg = af.generate_table_mod_msg(table_name, g_tables, g_fields)
        event.connection.send(msg)

def install_flows(event):
    for table_name in g_entries.keys():
        for entry in g_entries[table_name]:
            table = g_tables[table_name]
            msg = af.generate_flow_mod_msg(table, entry, g_tables, g_fields)
            event.connection.send(msg)
    for file_name in g_files.keys():
        file_info = g_files[file_name]
        af.read_entries_from_file(event, file_name, file_info, g_tables, g_fields)

def _handle_ConnectionUp (event):
    core.PofManager.set_port_pof_enable(event.dpid, 0x2)
    core.PofManager.set_port_pof_enable(event.dpid, 0x3)
    install_groups(event)
    install_tables(event)
    install_flows(event)

def _handle_PacketIn(event):
    packet = event.parsed
    print "received PACKETIN packet, inport " + str(event.port)
    print "packet data: " + binascii.hexlify(packet.pack())
    print "parsed src mac: " + str(packet.src)
    print "parsed dst mac: " + str(packet.dst)
    print ""

def launch ():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("L2 + L3 + ACL running.")

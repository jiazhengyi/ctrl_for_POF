#include <endian.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "pof_common.h"
#include "hps_common_resource.h"

/* TODO: 将端口范围转换为掩码 */
/* 掩码匹配 */

/* Define some byte order transfer operators. */
#if __BYTE_ORDER == __BIG_ENDIAN

#define ntoh64(x)                  (x)
#define hton64(x)                  (x)
#define ntohl(x)                   (x)
#define htonl(x)                   (x)
#define ntohs(x)                   (x)
#define htons(x)                   (x)

// #elif __BYTE_ORDER == __LITTLE_ENDIAN
#else

#define ntoh64(x)                  ((((x) & 0x00000000000000ffLL) << 56) | \
                                    (((x) & 0x000000000000ff00LL) << 40) | \
                                    (((x) & 0x0000000000ff0000LL) << 24) | \
                                    (((x) & 0x00000000ff000000LL) <<  8) | \
                                    (((x) & 0x000000ff00000000LL) >>  8) | \
                                    (((x) & 0x0000ff0000000000LL) >> 24) | \
                                    (((x) & 0x00ff000000000000LL) >> 40) | \
                                    (((x) & 0xff00000000000000LL) >> 56))

#define hton64(x)                  ((((x) & 0x00000000000000ffLL) << 56) | \
                                    (((x) & 0x000000000000ff00LL) << 40) | \
                                    (((x) & 0x0000000000ff0000LL) << 24) | \
                                    (((x) & 0x00000000ff000000LL) <<  8) | \
                                    (((x) & 0x000000ff00000000LL) >>  8) | \
                                    (((x) & 0x0000ff0000000000LL) >> 24) | \
                                    (((x) & 0x00ff000000000000LL) >> 40) | \
                                    (((x) & 0xff00000000000000LL) >> 56))

#define ntohl(x)                   ((((x) & 0x000000ff) << 24) | \
                                    (((x) & 0x0000ff00) <<  8) | \
                                    (((x) & 0x00ff0000) >>  8) | \
                                    (((x) & 0xff000000) >> 24))

#define htonl(x)                   ((((x) & 0x000000ff) << 24) | \
                                    (((x) & 0x0000ff00) <<  8) | \
                                    (((x) & 0x00ff0000) >>  8) | \
                                    (((x) & 0xff000000) >> 24))

#define ntohs(x)                   ((((x) & 0x00ff) << 8) | \
                                    (((x) & 0xff00) >> 8))

#define htons(x)                   ((((x) & 0x00ff) << 8) | \
                                    (((x) & 0xff00) >> 8))
// #else
// #error "Not defined __BYTE_ORDER"
#endif /* POF_BYTE_ORDER */

#define MAX_STRING_LENGTH (24)

struct acl_rule {
	char s_ip[MAX_STRING_LENGTH];
	char d_ip[MAX_STRING_LENGTH];
	char s_port[MAX_STRING_LENGTH];
	char d_port[MAX_STRING_LENGTH];
	char protocol[MAX_STRING_LENGTH];
	char action[MAX_STRING_LENGTH];
};

int __range_have_multi_prefixes(const char *str)
{
	uint16_t down, up;
	uint16_t diff;

	sscanf(str, "%hu:%hu", &down, &up);
	diff = up - down;

	/* 要满足[down, up]能用一个prefix表示的话，要求diff低位全为1，
	 * down对应低位全为0 */
	while (diff) {
		if ((!(diff & 1)) || (down & 1)) {
			return 1;
		}
		diff >>= 1;
		down >>= 1;
	}

	return 0;
}

void __convert_ip_subnet_2_match_x(const char *str, struct hps_reso_flow_entry *entry, int match_no)
{
	uint16_t ip[4];
	uint16_t mlen;

	sscanf(str, "%hu.%hu.%hu.%hu/%hu", ip, ip + 1, ip + 2, ip + 3, &mlen);
	entry->match[match_no].value[0] = ip[0];
	entry->match[match_no].value[1] = ip[1];
	entry->match[match_no].value[2] = ip[2];
	entry->match[match_no].value[3] = ip[3];
	if (mlen / 8) {
		memset(entry->match[match_no].mask, 0xFF, mlen / 8);
	}
	if (mlen % 8) {
		entry->match[match_no].mask[mlen / 8] = 0xFF << (8 - (mlen % 8));
	}
}

void __convert_protocol_2_match_x(const char *str, struct hps_reso_flow_entry *entry, int match_no)
{
	unsigned v, m;
	sscanf(str, "%x/%x", &v, &m);

	entry->match[match_no].value[0] = v;
	entry->match[match_no].mask[0] = m;
}

/**
 * @brief 将端口范围转换为最长前缀表示，存入表项的match x里，可能存一个或多个
 *
 * @param str 端口范围的字符串
 * @param entry 表项
 * @param match_no 存储当前端口最长前缀的match x编号
 * @param stride 下一个最长前缀间隔几个表项存储
 * @param entry_space 剩余的表项空间
 *
 * @return 生成的最长前缀数量
 */
int __convert_port_range_2_match_x(const char *str, struct hps_reso_flow_entry *entry, int match_no, int stride, int entry_space)
{
	int multi;
	uint16_t down, up;
	uint16_t diff;
	uint8_t bits;

	if (0 == stride) {
		return 0;
	}

	sscanf(str, "%hu:%hu", &down, &up);
	diff = up - down;

	/* 要满足[down, up]能用一个prefix表示的话，要求diff低位全为1，
	 * down对应低位全为0 */
	multi = 0;
	bits = 0;
	while (diff) {
		if ((!(diff & 1)) || (down & 1)) {
			multi = 1;
			break;
		}
		diff >>= 1;
		down >>= 1;
		bits++;
	}

	if (!multi) {
		entry->match[match_no].value[0] = down >> 8;
		entry->match[match_no].value[1] = 0xFF & down;
		if (bits < 8) {
			entry->match[match_no].mask[0] = 0xFF;
			entry->match[match_no].mask[1] = 0xFF << bits;
		} else {
			entry->match[match_no].mask[0] = 0xFF << (bits - 8);
		}
	}

	return 1;
}

void __convert_action_2_instruction(const char *str, struct hps_reso_flow_entry *entry)
{
	int action;

	sscanf(str, "%x/", &action);

	if (action) {
		entry->instruction[0].type = OFPIT_GOTO_TABLE;
		entry->instruction[0].goto_table.next_table_id = 5;
	} else {
		entry->instruction[0].type = OFPIT_DROP;
	}
	entry->ins_num = 1;
}

void __init_acl_entry(struct hps_reso_logic_table *table, struct hps_reso_flow_entry *entry)
{
	entry->logic_tid = table->logic_tid;
	entry->priority = 0;
	entry->match_type = table->match_type;
	entry->match_field_num = table->match_field_num;
	entry->match[0].field_id = 0x1003;
	entry->match[0].offset = 32;
	entry->match[0].length = 32;
	entry->match[1].field_id = 0x1004;
	entry->match[1].offset = 64;
	entry->match[1].length = 32;
	entry->match[2].field_id = 0x1005;
	entry->match[2].offset = 96;
	entry->match[2].length = 8;
	entry->match[3].field_id = 0x1006;
	entry->match[3].offset = 104;
	entry->match[3].length = 16;
	entry->match[4].field_id = 0x1007;
	entry->match[4].offset = 120;
	entry->match[4].length = 16;
}

void __duplicate_acl_entry_without_port_x(struct hps_reso_flow_entry *base, struct hps_reso_flow_entry *entry)
{
	entry->logic_tid = base->logic_tid;
	entry->priority = base->priority;
	entry->match_type = base->match_type;
	entry->match_field_num = base->match_field_num;
	memcpy(entry->match + 0, base->match + 0, sizeof(struct ofp_pof_match_x));
	memcpy(entry->match + 1, base->match + 1, sizeof(struct ofp_pof_match_x));
	memcpy(entry->match + 2, base->match + 2, sizeof(struct ofp_pof_match_x));
	entry->match[3].field_id = base->match[3].field_id;
	entry->match[3].offset = base->match[3].offset;
	entry->match[3].length = base->match[3].length;
	entry->match[4].field_id = base->match[3].field_id;
	entry->match[4].offset = base->match[3].offset;
	entry->match[4].length = base->match[3].length;
	entry->ins_num = base->ins_num;
	memcpy(entry->instruction,
			base->instruction,
			entry->ins_num * sizeof(struct ofp_instruction));
}

int __read_acl_entry(struct acl_rule *rule, struct hps_reso_logic_table *table, int start)
{
	struct hps_reso_flow_entry *base, *entry;
	int sn, dn;
	int i, j;

	if (start >= HPS_MAX_ENTRY_NUM) {
		return 0;
	}

	base = table->flow_entry + start;
	__convert_ip_subnet_2_match_x(rule->s_ip, base, 0);
	__convert_ip_subnet_2_match_x(rule->d_ip, base, 1);
	__convert_protocol_2_match_x(rule->protocol, base, 2);
	__convert_action_2_instruction(rule->action, base);
	if (__range_have_multi_prefixes(rule->s_port) ||
			__range_have_multi_prefixes(rule->d_port)) {
		/* TODO: 处理需要多个最长前缀匹配的规则 */
		return 0;
	}

	sn = __convert_port_range_2_match_x(rule->s_port,
			base,
			3,
			1,
			HPS_MAX_ENTRY_NUM - start);
	dn = __convert_port_range_2_match_x(rule->d_port,
			base,
			4,
			sn,
			HPS_MAX_ENTRY_NUM - start);

	if (0 == (sn * dn)) {
		/* 剩余的表项空间无法存下展开的表项 */
		return 0;
	}

	/* 填充源端口和目的端口 */
	for (i = 0; i < sn; i++) {
		for (j = 0; j < dn; j++) {
			if (i) {
				base = table->flow_entry + start;
				entry = table->flow_entry + start + i;

				memcpy(entry->match + 4,
						base->match + 4,
						sizeof(struct ofp_pof_match_x));
			}

			if (j) {
				base = table->flow_entry + start + i;
				entry = table->flow_entry + start + j * sn + i;

				memcpy(entry->match + 3,
						base->match + 3,
						sizeof(struct ofp_pof_match_x));
			}
		}
	}

	/* 填充其他信息：一般信息、匹配信息、指令 */
	base = table->flow_entry + start;
	__init_acl_entry(table, base);
	base->index = start;
	for (i = 1; i < (sn * dn); i++) {
		entry = base + i;
		__duplicate_acl_entry_without_port_x(base, entry);
		entry->index = start + i;
	}

	return sn * dn;
}

void __init_acl_table(struct hps_reso_logic_table *table)
{
	table->logic_tid = 4;
	table->match_type = OFPTT_MM;
	strcpy(table->table_name, "ACL");
	table->match_field_num = 5;
	table->match[0].field_id = 0x1003;
	table->match[0].offset = 32;
	table->match[0].length = 32;
	table->match[1].field_id = 0x1004;
	table->match[1].offset = 64;
	table->match[1].length = 32;
	table->match[2].field_id = 0x1005;
	table->match[2].offset = 96;
	table->match[2].length = 8;
	table->match[3].field_id = 0x1006;
	table->match[3].offset = 104;
	table->match[3].length = 16;
	table->match[4].field_id = 0x1007;
	table->match[4].offset = 120;
	table->match[4].length = 16;
}

int read_acl_table(const char *path, struct hps_reso_logic_table *table)
{
	struct acl_rule r;
	FILE *fp;
	int i;
	int ret;

	fp = fopen(path, "r");
	if (NULL == fp) {
		return 1;
	}

	__init_acl_table(table);

	i = 0;
	do {
		ret = fscanf(fp,
				"@%s %s %s %s %s %s\n",
				r.s_ip,
				r.d_ip,
				r.s_port,
				r.d_port,
				r.protocol,
				r.action);
		if (ret < 0) {
			break;
		}

		ret = __read_acl_entry(&r, table, i);
		i += ret;

		if (i > 2) {
			break;
		}
	} while (ret > 0);
	table->entry_num = i;

	return 0;
}

#include "hps_debug.h"

const char *match_type_2_str[] = {
	"MASK MATCH",
	"LONGEST PREFIX MATCH",
	"EXACT MATCH",
	"DIRECT",
};

const char *ins_type_2_str[] = {
	"SET_FIELD",
	"ADD_FIELD",
	"DEL_FIELD",
	"CALCULATE_FIELD",
	"COMPARE",
	"ALG",
	"GOTO_TABLE",
	"GET_TABLE_ENTRY",
	"SET_TABLE_ENTRY",
	"SET_PACKET_OFFSET",
	"MOVE_PACKET_OFFSET",
	"OUTPUT",
	"DROP",
	"TOCP",
	"COUNTER",
	"METER",
	"ABSOLUTE_JMP",
	"RELATIVE_JMP",
	"CONDITIONAL_RELATIVE_JMP",
	"BRANCH",
};

static void __print_entry(struct hps_reso_flow_entry *entry)
{
	int i;

	printf("Entry ID %u, priority %u, %d match fields:\n",
			entry->index,
			entry->priority,
			entry->match_field_num);

	for (i = 0; i < entry->match_field_num; i++) {
		if (entry->match[i].field_id < 0x1000) {
			printf("\tField %u, ", entry->match[i].field_id);
		} else {
			printf("\tField 0x%x, ", entry->match[i].field_id);
		}
		if (entry->match[i].field_id < OFPXMT_OFB_MAX) {
			if (ofb_match_fields[entry->match[i].field_id].mask) {
				printf("has mask:\n");
				hps_debug_dump_memory(entry->match[i].mask,
					ofb_match_fields[entry->match[i].field_id].length_bytes);
			} else {
				printf("has no mask, ");
			}
			printf("value:\n");
			hps_debug_dump_memory(entry->match[i].value,
					ofb_match_fields[entry->match[i].field_id].length_bytes);
		} else {
			printf("has mask:\n");
			hps_debug_dump_memory(entry->match[i].mask,
					BYTE_SPAN(entry->match[i].length));
			printf("value:\n");
			hps_debug_dump_memory(entry->match[i].value,
					BYTE_SPAN(entry->match[i].length));
		}
	}

	printf("\thas %u instructions:\n", entry->ins_num);
	for (i = 0; i < entry->ins_num; i++) {
		printf("\t\t%s.\n",
				ins_type_2_str[entry->instruction[i].type - 0x8001]);
	}
}

static void __print_table(struct hps_reso_logic_table *table)
{
	int i;

	printf("table %u '%s', match type %s, %u match fields:\n",
			table->logic_tid,
			table->table_name,
			match_type_2_str[table->match_type],
			table->match_field_num);

	for (i = 0; i < table->match_field_num; i++) {
		if (table->match[i].field_id < OFPXMT_OFB_MAX) {
			printf("\tField %s (ID = %u), bits length %u, byte"
					" length %u, %s mask.\n",
					ofb_match_fields[table->match[i].field_id].name,
					table->match[i].field_id,
					ofb_match_fields[table->match[i].field_id].length_bits,
					ofb_match_fields[table->match[i].field_id].length_bytes,
					ofb_match_fields[table->match[i].field_id].mask ?
					"has" : "has no");
		} else if (table->match[i].field_id < 0x1000) {
			printf("\tField %u, offset %u, bits length %u.\n",
					table->match[i].field_id,
					table->match[i].offset,
					table->match[i].length);
		} else {
			printf("\tField 0x%x, offset %u, bits length %u.\n",
					table->match[i].field_id,
					table->match[i].offset,
					table->match[i].length);
		}
	}

	for (i = 0; i < table->entry_num; i++) {
		__print_entry(table->flow_entry + i);
	}
}

int main(int argc, char **argv)
{
	struct hps_reso_logic_table table;
	if (argc < 2) {
		printf("Usage: %s <acl-rule-file>\n", argv[0]);
		return 1;

	}

	read_acl_table(argv[1], &table);

	__print_table(&table);

	return 0;
}

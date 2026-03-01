/*
 * 🛡️ SHIELD LINUX - Security Module Header
 * Definiciones y estructuras principales
 */

#ifndef _SHIELD_SECURITY_MODULE_H
#define _SHIELD_SECURITY_MODULE_H

#include <linux/types.h>

/* ==================== CONSTANTES Y DEFINICIONES ==================== */

#define IP_TRACKER_BITS 10  // 2^10 = 1024 buckets
#define MAX_TRACKED_IPS 10000
#define CLEANUP_INTERVAL 60  // segundos

/* Niveles de amenaza */
#define THREAT_NONE      0
#define THREAT_LOW       1
#define THREAT_MEDIUM    2
#define THREAT_HIGH      3
#define THREAT_CRITICAL  4

/* Acciones de respuesta */
#define SHIELD_ACTION_ACCEPT    0
#define SHIELD_ACTION_DROP      1
#define SHIELD_ACTION_REDIRECT  2
#define SHIELD_ACTION_RATELIMIT 3

/* Tipos de bloqueo */
#define BLOCK_NONE          0
#define BLOCK_TEMPORARY     1   // 5 minutos
#define BLOCK_EXTENDED      2   // 1 hora
#define BLOCK_PERMANENT     3   // Hasta reinicio

/* Umbrales de detección */
#define PORTSCAN_THRESHOLD      5       // puertos en ventana
#define PORTSCAN_WINDOW         60      // segundos
#define SYNFLOOD_THRESHOLD      100     // SYN/segundo
#define SYNFLOOD_WINDOW         1       // segundo
#define DDOS_THRESHOLD          1000    // paquetes/segundo
#define BRUTEFORCE_THRESHOLD    10      // intentos
#define BRUTEFORCE_WINDOW       300     // segundos (5 min)

/* ==================== ESTRUCTURAS DE DATOS ==================== */

/* Información de amenaza de Threat Intel */
struct threat_intel_info {
    bool is_malicious;
    u8 severity;
    u16 score;          // 0-100
    u32 reports;
    char country[4];
    char last_reported[32];
};

/* Información de paquete analizado */
struct shield_pkt_info {
    u32 src_ip;
    u32 dst_ip;
    u16 src_port;
    u16 dst_port;
    u8 protocol;
    u8 tcp_flags;
    u8 threat_level;
    u8 action;
    u64 timestamp;
    struct threat_intel_info threat_info;
};

/* Entrada de tracking de IP */
struct ip_tracker_entry {
    struct hlist_node hash;
    u32 ip;
    u64 first_seen;
    u64 last_seen;
    u32 packet_count;
    u32 port_count;
    u16 ports[20];      // Últimos 20 puertos visitados
    u8 threat_level;
    u8 block_type;
    u64 block_until;
    u32 attack_patterns;
    char country[4];
};

/* Estadísticas globales */
struct shield_stats {
    u64 packets_inspected;
    u64 packets_dropped;
    u64 attacks_detected;
    u64 countermeasures_triggered;
    u64 start_time;
};

/* Regla de contramedida */
struct shield_rule {
    u32 src_ip;
    u32 dst_ip;
    u16 src_port;
    u16 dst_port;
    u8 protocol;
    u8 action;
    u32 duration;
};

/* ==================== PROTOTIPOS DE FUNCIONES ==================== */

// Funciones de detección (detection.c)
int detect_port_scan(u32 ip, u16 port, u64 timestamp);
int detect_syn_flood(u32 ip, u64 timestamp);
int detect_null_xmas_scan(struct tcphdr *tcph);
int detect_ddos_pattern(u32 src_ip, u16 dst_port, u8 protocol, u64 timestamp);
int check_threat_intel(u32 ip, struct threat_intel_info *info);
int detect_attack_pattern(struct sk_buff *skb, struct iphdr *iph, 
                          struct shield_pkt_info *info);
int detect_data_exfiltration(struct iphdr *iph);

// Funciones de inicialización/limpieza
int init_port_scan_detection(void);
void cleanup_port_scan_detection(void);
int init_syn_flood_detection(void);
void cleanup_syn_flood_detection(void);
int init_ddos_detection(void);
void cleanup_ddos_detection(void);
int init_threat_intel(void);
void cleanup_threat_intel(void);
void shield_cleanup_detection(void);

// Funciones de contramedidas (countermeasures.c)
void apply_tcp_reset_injection(u32 src_ip, u16 src_port, 
                                u32 dst_ip, u16 dst_port);
void apply_syn_cookie_advanced(u32 ip);
void apply_connection_kill(u32 ip);
void apply_rate_limit_escalation(u32 ip);
void apply_honeypot_redirect(u32 ip, u16 original_port);
void apply_packet_blackhole(u32 ip, u8 log_level);
void apply_icmp_unreachable(u32 ip);
void apply_dynamic_firewall_rule(u32 ip, u8 block_type);
void init_countermeasure_system(void);
void cleanup_countermeasure_system(void);
void log_forensics_event(struct shield_pkt_info *info);

/* ==================== MACROS DE UTILIDAD ==================== */

#define SHIELD_DEBUG(fmt, ...) \
    pr_debug("[🛡️ SHIELD] " fmt "\n", ##__VA_ARGS__)

#define SHIELD_INFO(fmt, ...) \
    pr_info("[🛡️ SHIELD] " fmt "\n", ##__VA_ARGS__)

#define SHIELD_WARN(fmt, ...) \
    pr_warn("[⚠️ SHIELD] " fmt "\n", ##__VA_ARGS__)

#define SHIELD_ERR(fmt, ...) \
    pr_err("[❌ SHIELD] " fmt "\n", ##__VA_ARGS__)

/* Conversión de IP a string */
#define IP_TO_STR(ip) \
    ((unsigned char*)&ip)[0], ((unsigned char*)&ip)[1], \
    ((unsigned char*)&ip)[2], ((unsigned char*)&ip)[3]

#define IP_FMT "%u.%u.%u.%u"

#endif /* _SHIELD_SECURITY_MODULE_H */

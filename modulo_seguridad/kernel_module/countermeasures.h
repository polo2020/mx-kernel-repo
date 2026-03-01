/*
 * 🛡️ SHIELD LINUX - Countermeasures Header
 * Definiciones de las 8 contramedidas activas
 */

#ifndef _SHIELD_COUNTERMEASURES_H
#define _SHIELD_COUNTERMEASURES_H

#include <linux/types.h>

/* ==================== ESTADÍSTICAS DE CONTRAMEDIDAS ==================== */

struct countermeasure_stats {
    u64 tcp_resets_sent;
    u64 syn_cookies_active;
    u64 connections_killed;
    u64 rate_limits_applied;
    u64 honeypot_redirects;
    u64 blackhole_drops;
    u64 icmp_unreachable_sent;
    u64 firewall_rules_created;
};

/* ==================== NIVELES DE LOG FORENSE ==================== */

#define LOG_NONE        0
#define LOG_ONLY        1
#define LOG_DETAILED    2
#define LOG_FORENSICS   3

/* ==================== PROTOTIPOS DE CONTRAMEDIDAS ==================== */

/*
 * 1. TCP Reset Injection
 * Envía paquetes RST para terminar conexiones maliciosas
 */
void apply_tcp_reset_injection(u32 src_ip, u16 src_port, 
                                u32 dst_ip, u16 dst_port);

/*
 * 2. SYN Cookie Advanced
 * Protección mejorada contra SYN floods
 */
void apply_syn_cookie_advanced(u32 ip);

/*
 * 3. Connection Kill Switch
 * Termina conexiones establecidas de atacantes
 */
void apply_connection_kill(u32 ip);

/*
 * 4. Rate Limit Escalation
 * Límite progresivo que se endurece con cada intento
 */
void apply_rate_limit_escalation(u32 ip);

/*
 * 5. Honeypot Redirect
 * Redirige atacantes a puertos honeypot
 */
void apply_honeypot_redirect(u32 ip, u16 original_port);

/*
 * 6. Packet Blackhole
 * Descarta paquetes silenciosamente con logging
 */
void apply_packet_blackhole(u32 ip, u8 log_level);

/*
 * 7. ICMP Unreachable
 * Envía ICMP tipo 3 para engañar al atacante
 */
void apply_icmp_unreachable(u32 ip);

/*
 * 8. Dynamic Firewall Rules
 * Genera reglas iptables/nftables automáticamente
 */
void apply_dynamic_firewall_rule(u32 ip, u8 block_type);

/* ==================== FUNCIONES DE SISTEMA ==================== */

/* Inicializar sistema de contramedidas */
void init_countermeasure_system(void);

/* Limpiar sistema de contramedidas */
void cleanup_countermeasure_system(void);

/* Logging forense */
void log_forensics_event(struct shield_pkt_info *info);

/* ==================== IOCTL DEFINITIONS ==================== */

#define SHIELD_IOC_MAGIC 'S'

#define SHIELD_IOC_TCP_RESET      _IOW(SHIELD_IOC_MAGIC, 1, struct shield_rule)
#define SHIELD_IOC_SYN_COOKIE     _IOW(SHIELD_IOC_MAGIC, 2, struct shield_rule)
#define SHIELD_IOC_CONN_KILL      _IOW(SHIELD_IOC_MAGIC, 3, struct shield_rule)
#define SHIELD_IOC_RATE_ESCALATE  _IOW(SHIELD_IOC_MAGIC, 4, struct shield_rule)
#define SHIELD_IOC_HONEYPOT       _IOW(SHIELD_IOC_MAGIC, 5, struct shield_rule)
#define SHIELD_IOC_BLACKHOLE      _IOW(SHIELD_IOC_MAGIC, 6, struct shield_rule)
#define SHIELD_IOC_ICMP_UNREACH   _IOW(SHIELD_IOC_MAGIC, 7, struct shield_rule)
#define SHIELD_IOC_FW_RULE        _IOW(SHIELD_IOC_MAGIC, 8, struct shield_rule)

#define SHIELD_IOC_GET_STATS      _IOR(SHIELD_IOC_MAGIC, 9, struct countermeasure_stats)
#define SHIELD_IOC_ENABLE_ALL     _IO(SHIELD_IOC_MAGIC, 10)
#define SHIELD_IOC_DISABLE_ALL    _IO(SHIELD_IOC_MAGIC, 11)

#endif /* _SHIELD_COUNTERMEASURES_H */

/*
 * 🛡️ SHIELD LINUX - Detection Header
 * Definiciones de las 7 funciones de detección reforzadas
 */

#ifndef _SHIELD_DETECTION_H
#define _SHIELD_DETECTION_H

#include <linux/types.h>

/* ==================== CONSTANTES DE DETECCIÓN ==================== */

#define PORTSCAN_BITS       10  // 1024 buckets
#define SYNFLOOD_BITS       10
#define DDOS_BITS           10

#define MAX_PORTS_TRACKED   20
#define PORTSCAN_THRESHOLD  5
#define PORTSCAN_WINDOW     60   // segundos
#define SYNFLOOD_THRESHOLD  100  // SYN/segundo
#define SYNFLOOD_WINDOW     1    // segundo
#define DDOS_THRESHOLD      1000 // paquetes/segundo

/* Tipos de scan */
#define SCAN_UNKNOWN    0
#define SCAN_VERTICAL   1
#define SCAN_HORIZONTAL 2
#define SCAN_BLOCK      3

/* Tipos de ataque DDoS */
#define ATTACK_UNKNOWN      0
#define ATTACK_UDP_FLOOD    1
#define ATTACK_ICMP_FLOOD   2
#define ATTACK_SYN_FLOOD    3
#define ATTACK_AMPLIFICATION 4

/* ==================== ESTRUCTURAS ==================== */

struct threat_intel_info;
struct shield_pkt_info;

/* ==================== PROTOTIPOS DE DETECCIÓN ==================== */

/*
 * 1. Advanced Port Scan Detection
 * Detección multi-algoritmo: horizontal, vertical, block scan
 */
int detect_port_scan(u32 ip, u16 port, u64 timestamp);
int init_port_scan_detection(void);
void cleanup_port_scan_detection(void);

/*
 * 2. SYN Flood Detection Reforzada
 * Con ratio analysis SYN/ACK
 */
int detect_syn_flood(u32 ip, u64 timestamp);
int detect_null_xmas_scan(struct tcphdr *tcph);
int init_syn_flood_detection(void);
void cleanup_syn_flood_detection(void);

/*
 * 3. DDoS Mitigation Engine
 * Protección capa 3/4/7
 */
int detect_ddos_pattern(u32 src_ip, u16 dst_port, u8 protocol, u64 timestamp);
int init_ddos_detection(void);
void cleanup_ddos_detection(void);

/*
 * 4. Threat Intelligence Integration
 * Múltiples feeds: AbuseIPDB, Spamhaus, AlienVault
 */
int check_threat_intel(u32 ip, struct threat_intel_info *info);
int init_threat_intel(void);
void cleanup_threat_intel(void);

/*
 * 5. Deep Pattern Detection
 * Regex + signature matching + heurística
 */
int detect_attack_pattern(struct sk_buff *skb, struct iphdr *iph,
                          struct shield_pkt_info *info);

/*
 * 6. Adaptive Rate Limiting
 * ML-based rate adjustment
 */
int apply_adaptive_rate_limit(u32 ip, u64 timestamp);

/*
 * 7. Self-Healing + Auto-Recovery
 * Monitoreo y recuperación de servicios
 */
int check_service_health(void);

/*
 * 8. Data Exfiltration Detection
 * Detección de transferencia sospechosa
 */
int detect_data_exfiltration(struct iphdr *iph);

/* Limpieza general */
void shield_cleanup_detection(void);

#endif /* _SHIELD_DETECTION_H */

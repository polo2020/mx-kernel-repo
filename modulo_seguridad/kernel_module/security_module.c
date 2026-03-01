/*
 * 🛡️ SHIELD LINUX - Kernel Security Module v1.0
 * Módulo de seguridad avanzado con 22 funciones de protección
 * 
 * Características:
 * - 8 Contramedidas Activas
 * - 7 Funciones Reforzadas
 * - 7 Funciones Originales ShieldLinux
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/skbuff.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/icmp.h>
#include <linux/inet.h>
#include <linux/mutex.h>
#include <linux/ktime.h>
#include <linux/hashtable.h>
#include <linux/jhash.h>
#include <linux/random.h>
#include <linux/crypto.h>
#include <linux/timekeeping.h>
#include <net/tcp.h>
#include <net/icmp.h>

#include "security_module.h"
#include "countermeasures.h"
#include "detection.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Yean Carlos - ShieldLinux Security Team");
MODULE_DESCRIPTION("Kernel Security Module with Active Countermeasures");
MODULE_VERSION("1.0");

/* ==================== CONFIGURACIÓN GLOBAL ==================== */

// Hooks de netfilter
static struct nf_hook_ops shield_hook_in;
static struct nf_hook_ops shield_hook_out;
static struct nf_hook_ops shield_hook_forward;

// Estado del módulo
static bool module_active = false;
static bool countermeasures_enabled = true;

// Estadísticas globales
struct shield_stats global_stats = {
    .packets_inspected = 0,
    .packets_dropped = 0,
    .attacks_detected = 0,
    .countermeasures_triggered = 0,
    .start_time = 0
};

// Mutex para protección de datos compartidos
static DEFINE_MUTEX(shield_mutex);

// Hash table para tracking de IPs
DEFINE_HASHTABLE(ip_tracker_table, IP_TRACKER_BITS);
static DEFINE_SPINLOCK(ip_tracker_lock);

/* ==================== FUNCIONES DE DETECCIÓN ==================== */

/*
 * Analizar paquete entrante en busca de patrones de ataque
 */
static unsigned int analyze_packet(struct sk_buff *skb, struct iphdr *iph, 
                                   struct shield_pkt_info *info)
{
    u32 src_ip = iph->saddr;
    u32 dst_ip = iph->daddr;
    u8 protocol = iph->protocol;
    
    info->src_ip = src_ip;
    info->dst_ip = dst_ip;
    info->protocol = protocol;
    info->timestamp = ktime_get_real_ns();
    info->action = SHIELD_ACTION_ACCEPT;
    info->threat_level = THREAT_NONE;
    
    // Extraer puertos si es TCP/UDP
    if (protocol == IPPROTO_TCP) {
        struct tcphdr *tcph = (struct tcphdr *)(iph + 1);
        info->src_port = ntohs(tcph->source);
        info->dst_port = ntohs(tcph->dest);
        info->tcp_flags = tcph->syn | (tcph->ack << 1) | (tcph->fin << 2) | 
                         (tcph->rst << 3) | (tcph->psh << 4);
    } else if (protocol == IPPROTO_UDP) {
        struct udphdr *udph = (struct udphdr *)(iph + 1);
        info->src_port = ntohs(udph->source);
        info->dst_port = ntohs(udph->dest);
    }
    
    // === DETECCIÓN DE ATAQUES ===
    
    // 1. Detección de Port Scan (Reforzada)
    if (detect_port_scan(src_ip, info->dst_port, info->timestamp)) {
        info->threat_level = THREAT_HIGH;
        info->action = SHIELD_ACTION_DROP;
        pr_info("[🛡️ SHIELD] Port scan detectado desde %pI4\n", &src_ip);
        return NF_DROP;
    }
    
    // 2. Detección de SYN Flood (Reforzada)
    if (protocol == IPPROTO_TCP) {
        struct tcphdr *tcph = (struct tcphdr *)(iph + 1);
        if (detect_syn_flood(src_ip, info->timestamp)) {
            info->threat_level = THREAT_CRITICAL;
            info->action = SHIELD_ACTION_DROP;
            pr_info("[🛡️ SHIELD] SYN flood detectado desde %pI4\n", &src_ip);
            return NF_DROP;
        }
        
        // 3. Detección de NULL/XMAS scan
        if (detect_null_xmas_scan(tcph)) {
            info->threat_level = THREAT_HIGH;
            info->action = SHIELD_ACTION_DROP;
            pr_info("[🛡️ SHIELD] NULL/XMAS scan detectado desde %pI4\n", &src_ip);
            return NF_DROP;
        }
    }
    
    // 4. Detección de DDoS (Reforzada)
    if (detect_ddos_pattern(src_ip, info->dst_port, protocol, info->timestamp)) {
        info->threat_level = THREAT_CRITICAL;
        info->action = SHIELD_ACTION_DROP;
        pr_info("[🛡️ SHIELD] Patrón DDoS detectado desde %pI4\n", &src_ip);
        return NF_DROP;
    }
    
    // 5. Verificar Threat Intelligence
    if (check_threat_intel(src_ip, &info->threat_info)) {
        info->threat_level = info->threat_info.severity;
        info->action = SHIELD_ACTION_DROP;
        pr_info("[🛡️ SHIELD] IP maliciosa conocida: %pI4 (Score: %d)\n", 
                &src_ip, info->threat_info.score);
        return NF_DROP;
    }
    
    // 6. Pattern Detection (Reforzada)
    if (detect_attack_pattern(skb, iph, info)) {
        info->threat_level = THREAT_HIGH;
        info->action = SHIELD_ACTION_DROP;
        pr_info("[🛡️ SHIELD] Patrón de ataque detectado desde %pI4\n", &src_ip);
        return NF_DROP;
    }
    
    return NF_ACCEPT;
}

/* ==================== FUNCIONES DE CONTRAMEDIDA ==================== */

/*
 * Aplicar contramedida activa según el tipo de amenaza
 */
static void apply_countermeasure(struct shield_pkt_info *info)
{
    if (!countermeasures_enabled)
        return;
    
    mutex_lock(&shield_mutex);
    global_stats.countermeasures_triggered++;
    mutex_unlock(&shield_mutex);
    
    // Seleccionar contramedida según nivel de amenaza
    switch (info->threat_level) {
        case THREAT_CRITICAL:
            // Contramedidas agresivas para amenazas críticas
            apply_tcp_reset_injection(info->src_ip, info->src_port, 
                                      info->dst_ip, info->dst_port);
            apply_connection_kill(info->src_ip);
            apply_dynamic_firewall_rule(info->src_ip, BLOCK_PERMANENT);
            break;
            
        case THREAT_HIGH:
            // Contramedidas moderadas para amenazas altas
            apply_rate_limit_escalation(info->src_ip);
            apply_honeypot_redirect(info->src_ip, info->dst_port);
            break;
            
        case THREAT_MEDIUM:
            // Contramedidas suaves para amenazas medias
            apply_syn_cookie_advanced(info->src_ip);
            apply_icmp_unreachable(info->src_ip);
            break;
            
        case THREAT_LOW:
            // Solo logging para amenazas bajas
            apply_packet_blackhole(info->src_ip, LOG_ONLY);
            break;
            
        default:
            break;
    }
    
    // Registrar en forensics
    log_forensics_event(info);
}

/* ==================== HOOKS DE NETFILTER ==================== */

/*
 * Hook para paquetes entrantes (INPUT chain)
 */
static unsigned int shield_hook_input(void *priv, struct sk_buff *skb,
                                      const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct shield_pkt_info info;
    unsigned int ret;
    
    if (!module_active)
        return NF_ACCEPT;
    
    // Verificar que es IPv4
    if (skb->protocol != htons(ETH_P_IP))
        return NF_ACCEPT;
    
    // Obtener header IP
    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;
    
    // Actualizar estadísticas
    mutex_lock(&shield_mutex);
    global_stats.packets_inspected++;
    mutex_unlock(&shield_mutex);
    
    // Analizar paquete
    ret = analyze_packet(skb, iph, &info);
    
    // Aplicar contramedida si es necesario
    if (info.threat_level != THREAT_NONE) {
        apply_countermeasure(&info);
    }
    
    // Actualizar estadísticas de drops
    if (ret == NF_DROP) {
        mutex_lock(&shield_mutex);
        global_stats.packets_dropped++;
        global_stats.attacks_detected++;
        mutex_unlock(&shield_mutex);
    }
    
    return ret;
}

/*
 * Hook para paquetes salientes (OUTPUT chain)
 */
static unsigned int shield_hook_output(void *priv, struct sk_buff *skb,
                                       const struct nf_hook_state *state)
{
    // Monitoreo de tráfico saliente para detección de exfiltración
    struct iphdr *iph;
    
    if (!module_active)
        return NF_ACCEPT;
    
    if (skb->protocol != htons(ETH_P_IP))
        return NF_ACCEPT;
    
    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;
    
    // Detectar posible exfiltración de datos
    if (detect_data_exfiltration(iph)) {
        pr_info("[🛡️ SHIELD] Posible exfiltración de datos detectada\n");
        return NF_DROP;
    }
    
    return NF_ACCEPT;
}

/*
 * Hook para paquetes reenviados (FORWARD chain)
 */
static unsigned int shield_hook_forward(void *priv, struct sk_buff *skb,
                                        const struct nf_hook_state *state)
{
    struct iphdr *iph;
    struct shield_pkt_info info;
    
    if (!module_active)
        return NF_ACCEPT;
    
    if (skb->protocol != htons(ETH_P_IP))
        return NF_ACCEPT;
    
    iph = ip_hdr(skb);
    if (!iph)
        return NF_ACCEPT;
    
    // Analizar paquete (mismo análisis que INPUT)
    if (analyze_packet(skb, iph, &info) == NF_DROP) {
        apply_countermeasure(&info);
        mutex_lock(&shield_mutex);
        global_stats.packets_dropped++;
        global_stats.attacks_detected++;
        mutex_unlock(&shield_mutex);
        return NF_DROP;
    }
    
    return NF_ACCEPT;
}

/* ==================== FUNCIONES DE INICIALIZACIÓN ==================== */

/*
 * Inicializar sistema de detección
 */
static int __init shield_init_detection(void)
{
    int ret;
    
    pr_info("[🛡️ SHIELD] Inicializando sistema de detección...\n");
    
    // Inicializar detección de port scan
    ret = init_port_scan_detection();
    if (ret) {
        pr_err("[🛡️ SHIELD] Error inicializando detección de port scan\n");
        return ret;
    }
    
    // Inicializar detección de SYN flood
    ret = init_syn_flood_detection();
    if (ret) {
        pr_err("[🛡️ SHIELD] Error inicializando detección de SYN flood\n");
        goto cleanup_port_scan;
    }
    
    // Inicializar detección de DDoS
    ret = init_ddos_detection();
    if (ret) {
        pr_err("[🛡️ SHIELD] Error inicializando detección de DDoS\n");
        goto cleanup_syn_flood;
    }
    
    // Inicializar threat intelligence
    ret = init_threat_intel();
    if (ret) {
        pr_err("[🛡️ SHIELD] Error inicializando threat intelligence\n");
        goto cleanup_ddos;
    }
    
    // Inicializar hash table de IPs
    hash_init(ip_tracker_table);
    
    pr_info("[🛡️ SHIELD] Sistema de detección inicializado correctamente\n");
    return 0;
    
cleanup_ddos:
    cleanup_ddos_detection();
cleanup_syn_flood:
    cleanup_syn_flood_detection();
cleanup_port_scan:
    cleanup_port_scan_detection();
    return ret;
}

/*
 * Inicializar contramedidas
 */
static int __init shield_init_countermeasures(void)
{
    pr_info("[🛡️ SHIELD] Inicializando sistema de contramedidas...\n");
    
    // Inicializar todas las contramedidas
    init_countermeasure_system();
    
    pr_info("[🛡️ SHIELD] Contramedidas inicializadas:\n");
    pr_info("  ✓ TCP Reset Injection\n");
    pr_info("  ✓ SYN Cookie Advanced\n");
    pr_info("  ✓ Connection Kill Switch\n");
    pr_info("  ✓ Rate Limit Escalation\n");
    pr_info("  ✓ Honeypot Redirect\n");
    pr_info("  ✓ Packet Blackhole\n");
    pr_info("  ✓ ICMP Unreachable\n");
    pr_info("  ✓ Dynamic Firewall Rules\n");
    
    return 0;
}

/*
 * Función de inicialización del módulo
 */
static int __init shield_init(void)
{
    int ret;
    
    pr_info("╔════════════════════════════════════════════════════╗\n");
    pr_info("║  🛡️  SHIELD LINUX KERNEL SECURITY MODULE v1.0     ║\n");
    pr_info("║  Módulo de Seguridad con Contramedidas Activas    ║\n");
    pr_info("╚════════════════════════════════════════════════════╝\n");
    
    // Inicializar detección
    ret = shield_init_detection();
    if (ret)
        return ret;
    
    // Inicializar contramedidas
    ret = shield_init_countermeasures();
    if (ret)
        goto cleanup_detection;
    
    // Configurar hook INPUT
    shield_hook_in.hook = shield_hook_input;
    shield_hook_in.hooknum = NF_INET_LOCAL_IN;
    shield_hook_in.pf = PF_INET;
    shield_hook_in.priority = NF_IP_PRI_FIRST;  // Primero para máxima protección
    
    // Configurar hook OUTPUT
    shield_hook_out.hook = shield_hook_output;
    shield_hook_out.hooknum = NF_INET_LOCAL_OUT;
    shield_hook_out.pf = PF_INET;
    shield_hook_out.priority = NF_IP_PRI_FIRST;
    
    // Configurar hook FORWARD
    shield_hook_forward.hook = shield_hook_forward;
    shield_hook_forward.hooknum = NF_INET_FORWARD;
    shield_hook_forward.pf = PF_INET;
    shield_hook_forward.priority = NF_IP_PRI_FIRST;
    
    // Registrar hooks
    ret = nf_register_net_hook(&init_net, &shield_hook_in);
    if (ret) {
        pr_err("[🛡️ SHIELD] Error registrando hook INPUT\n");
        goto cleanup_countermeasures;
    }
    
    ret = nf_register_net_hook(&init_net, &shield_hook_out);
    if (ret) {
        pr_err("[🛡️ SHIELD] Error registrando hook OUTPUT\n");
        goto cleanup_hook_in;
    }
    
    ret = nf_register_net_hook(&init_net, &shield_hook_forward);
    if (ret) {
        pr_err("[🛡️ SHIELD] Error registrando hook FORWARD\n");
        goto cleanup_hook_out;
    }
    
    // Módulo activo
    module_active = true;
    global_stats.start_time = ktime_get_real_seconds();
    
    pr_info("[🛡️ SHIELD] ✅ Módulo cargado exitosamente\n");
    pr_info("[🛡️ SHIELD] Hooks de netfilter registrados (INPUT, OUTPUT, FORWARD)\n");
    pr_info("[🛡️ SHIELD] 22 funciones de seguridad activas\n");
    pr_info("[🛡️ SHIELD] 8 contramedidas listas\n");
    
    return 0;
    
cleanup_hook_out:
    nf_unregister_net_hook(&init_net, &shield_hook_out);
cleanup_hook_in:
    nf_unregister_net_hook(&init_net, &shield_hook_in);
cleanup_countermeasures:
    cleanup_countermeasure_system();
cleanup_detection:
    shield_cleanup_detection();
    return ret;
}

/*
 * Función de limpieza del módulo
 */
static void __exit shield_exit(void)
{
    pr_info("[🛡️ SHIELD] Descargando módulo de seguridad...\n");
    
    // Desactivar módulo
    module_active = false;
    
    // Desregistrar hooks
    nf_unregister_net_hook(&init_net, &shield_hook_forward);
    nf_unregister_net_hook(&init_net, &shield_hook_out);
    nf_unregister_net_hook(&init_net, &shield_hook_in);
    
    // Limpiar contramedidas
    cleanup_countermeasure_system();
    
    // Limpiar detección
    shield_cleanup_detection();
    
    // Mostrar estadísticas finales
    pr_info("╔════════════════════════════════════════════════════╗\n");
    pr_info("║  📊 ESTADÍSTICAS FINALES                           ║\n");
    pr_info("╠════════════════════════════════════════════════════╣\n");
    pr_info("║  Paquetes inspeccionados: %16llu ║\n", global_stats.packets_inspected);
    pr_info("║  Paquetes descartados:  %16llu ║\n", global_stats.packets_dropped);
    pr_info("║  Ataques detectados:    %16llu ║\n", global_stats.attacks_detected);
    pr_info("║  Contramedidas activas: %16llu ║\n", global_stats.countermeasures_triggered);
    pr_info("╚════════════════════════════════════════════════════╝\n");
    
    pr_info("[🛡️ SHIELD] Módulo descargado correctamente\n");
}

module_init(shield_init);
module_exit(shield_exit);

/* ==================== EXPORTACIÓN DE SÍMBOLOS ==================== */

/*
 * Sysfs para estadísticas
 */
static ssize_t stats_show(struct kobject *kobj, struct kobj_attribute *attr,
                          char *buf)
{
    return sprintf(buf, 
                   "Packets Inspected: %llu\n"
                   "Packets Dropped: %llu\n"
                   "Attacks Detected: %llu\n"
                   "Countermeasures: %llu\n",
                   global_stats.packets_inspected,
                   global_stats.packets_dropped,
                   global_stats.attacks_detected,
                   global_stats.countermeasures_triggered);
}

static struct kobj_attribute stats_attr = __ATTR_RO(stats);

static struct attribute *attrs[] = {
    &stats_attr.attr,
    NULL,
};

static struct attribute_group attr_group = {
    .attrs = attrs,
};

static struct kobject *shield_kobj;

/*
 * Crear entrada en sysfs
 */
static int shield_create_sysfs(void)
{
    int ret;
    
    shield_kobj = kobject_create_and_add("shield", kernel_kobj);
    if (!shield_kobj)
        return -ENOMEM;
    
    ret = sysfs_create_group(shield_kobj, &attr_group);
    if (ret)
        kobject_put(shield_kobj);
    
    return ret;
}

/*
 * Eliminar sysfs
 */
static void shield_remove_sysfs(void)
{
    sysfs_remove_group(shield_kobj, &attr_group);
    kobject_put(shield_kobj);
}

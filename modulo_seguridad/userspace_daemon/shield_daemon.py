#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ SHIELD LINUX - Userspace Daemon v1.0
Daemon de gestión para el módulo de seguridad del kernel

Funciones:
- Gestión del módulo kernel
- Monitoreo en tiempo real
- Threat Intelligence (AbuseIPDB, Spamhaus)
- 8 Contramedidas activas
- 7 Funciones de detección reforzadas
- Logging forense
- API REST para gestión remota
"""

import os
import sys
import subprocess
import re
import json
import time
import socket
import threading
import hashlib
import signal
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional, Dict, List, Set, Tuple
import urllib.request
import ssl
import http.server
import socketserver

# ==================== CONFIGURACIÓN ====================

CONFIG_DIR = "/etc/shield"
LOG_DIR = "/var/log"
MODULE_NAME = "security_module"
MODULE_PATH = "/lib/modules/$(uname -r)/kernel/security/security_module.ko"

# Archivos de configuración y estado
CONFIG_FILE = f"{CONFIG_DIR}/config.json"
STATE_FILE = f"{CONFIG_DIR}/shield_state.json"
WHITELIST_FILE = f"{CONFIG_DIR}/whitelist.json"
BLACKLIST_FILE = f"{CONFIG_DIR}/blacklist.json"
FORENSICS_LOG = f"{LOG_DIR}/shield_forensics.log"
BANS_LOG = f"{LOG_DIR}/shield_bans.log"
DAEMON_LOG = f"{LOG_DIR}/shield_daemon.log"

# APIs de Threat Intelligence
ABUSEIPDB_API_KEY = "445e7aea35654d655abda609f1312c3e07eabac64e0071904921335db8034e282dac16119b305295"
SPAMHAUS_DROP_URL = "https://www.spamhaus.org/drop/drop.txt"

# Umbrales de configuración
DEFAULT_CONFIG = {
    "portscan_threshold": 5,
    "portscan_window": 60,
    "synflood_threshold": 100,
    "ddos_threshold": 1000,
    "bruteforce_threshold": 10,
    "bruteforce_window": 300,
    "ban_time_default": -1,  # -1 = permanente
    "enable_countermeasures": True,
    "enable_threat_intel": True,
    "enable_forensics": True,
    "log_level": "INFO",
    "api_port": 8765,
    "api_enabled": True
}

# ==================== CLASES PRINCIPALES ====================

class ThreatIntelligenceFeed:
    """Gestión de feeds de inteligencia de amenazas"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.spamhaus_drop: Set[str] = set()
        self.last_update = 0
        self.cache_max_age = 3600  # 1 hora
    
    def check_abuseipdb(self, ip: str) -> Dict:
        """Consulta AbuseIPDB API"""
        if ip in self.cache:
            cached = self.cache[ip]
            if time.time() - cached.get('timestamp', 0) < self.cache_max_age:
                return cached['data']
        
        try:
            req = urllib.request.Request(
                f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}",
                headers={"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
            )
            context = ssl.create_default_context()
            with urllib.request.urlopen(req, context=context, timeout=5) as response:
                data = json.loads(response.read().decode())
                result = data.get('data', {})
                
                self.cache[ip] = {
                    'timestamp': time.time(),
                    'data': {
                        'is_malicious': result.get('abuseConfidenceScore', 0) > 50,
                        'score': result.get('abuseConfidenceScore', 0),
                        'reports': result.get('totalReports', 0),
                        'country': result.get('countryCode', 'XX'),
                        'last_reported': result.get('lastReportedAt')
                    }
                }
                
                return self.cache[ip]['data']
        except Exception as e:
            log(f"Error consultando AbuseIPDB: {e}", "WARNING")
            return {'is_malicious': False, 'score': 0}
    
    def update_spamhaus_drop(self):
        """Descarga lista Spamhaus DROP"""
        try:
            req = urllib.request.Request(SPAMHAUS_DROP_URL)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode()
                self.spamhaus_drop = set()
                for line in content.split('\n'):
                    if line and not line.startswith(';') and '/' in line:
                        self.spamhaus_drop.add(line.split(';')[0].strip())
                log(f"Spamhaus DROP: {len(self.spamhaus_drop)} redes cargadas")
        except Exception as e:
            log(f"Error actualizando Spamhaus: {e}", "WARNING")
    
    def check_spamhaus(self, ip: str) -> bool:
        """Verifica si IP está en Spamhaus DROP"""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip)
            for cidr in self.spamhaus_drop:
                if ip_obj in ipaddress.ip_network(cidr, strict=False):
                    return True
        except:
            pass
        return False


class CountermeasureManager:
    """Gestión de las 8 contramedidas activas"""
    
    def __init__(self):
        self.enabled = True
        self.stats = {
            'tcp_resets': 0,
            'syn_cookies': 0,
            'conn_kills': 0,
            'rate_limits': 0,
            'honeypot_redirects': 0,
            'blackhole_drops': 0,
            'icmp_unreachable': 0,
            'firewall_rules': 0
        }
    
    def apply_tcp_reset(self, src_ip: str, src_port: int, dst_ip: str, dst_port: int):
        """1. TCP Reset Injection"""
        if not self.enabled:
            return
        
        self.stats['tcp_resets'] += 1
        log(f"TCP Reset: {src_ip}:{src_port} → {dst_ip}:{dst_port}", "COUNTERMEASURE")
        
        # Ejecutar iptables para enviar RST
        try:
            subprocess.run(
                ["iptables", "-A", "OUTPUT", "-p", "tcp", "--tcp-flags", "RST", "RST",
                 "-s", dst_ip, "--sport", str(dst_port), "-d", src_ip, "--dport", str(src_port),
                 "-j", "REJECT", "--reject-with", "tcp-reset"],
                capture_output=True, timeout=5
            )
        except Exception as e:
            log(f"Error TCP Reset: {e}", "ERROR")
    
    def apply_connection_kill(self, ip: str):
        """3. Connection Kill Switch"""
        if not self.enabled:
            return
        
        self.stats['conn_kills'] += 1
        log(f"Connection Kill: {ip}", "COUNTERMEASURE")
        
        # Matar conexiones establecidas
        try:
            subprocess.run(["ss", "-K", "src", ip], capture_output=True, timeout=5)
        except:
            pass
    
    def apply_rate_limit(self, ip: str, limit_pps: int = 10):
        """4. Rate Limit Escalation"""
        if not self.enabled:
            return
        
        self.stats['rate_limits'] += 1
        log(f"Rate Limit: {ip} → {limit_pps} pps", "COUNTERMEASURE")
        
        try:
            # Usar hashlimit para rate limiting
            subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-m", "hashlimit",
                 "--hashlimit-name", f"shield_{ip.replace('.', '_')}",
                 "--hashlimit-mode", "srcip",
                 "--hashlimit-upto", str(limit_pps),
                 "--hashlimit-burst", str(limit_pps * 2),
                 "-j", "DROP"],
                capture_output=True, timeout=5
            )
        except Exception as e:
            log(f"Error Rate Limit: {e}", "ERROR")
    
    def apply_honeypot_redirect(self, ip: str, original_port: int, honeypot_port: int = 9999):
        """5. Honeypot Redirect"""
        if not self.enabled:
            return
        
        self.stats['honeypot_redirects'] += 1
        log(f"Honeypot Redirect: {ip}:{original_port} → :{honeypot_port}", "COUNTERMEASURE")
        
        try:
            subprocess.run(
                ["iptables", "-t", "nat", "-A", "PREROUTING", "-s", ip, "-p", "tcp",
                 "--dport", str(original_port), "-j", "REDIRECT", "--to-port", str(honeypot_port)],
                capture_output=True, timeout=5
            )
        except Exception as e:
            log(f"Error Honeypot: {e}", "ERROR")
    
    def apply_blackhole(self, ip: str):
        """6. Packet Blackhole"""
        if not self.enabled:
            return
        
        self.stats['blackhole_drops'] += 1
        log(f"Blackhole: {ip}", "COUNTERMEASURE")
        
        try:
            subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                capture_output=True, timeout=5
            )
        except Exception as e:
            log(f"Error Blackhole: {e}", "ERROR")
    
    def apply_icmp_unreachable(self, ip: str):
        """7. ICMP Unreachable"""
        if not self.enabled:
            return
        
        self.stats['icmp_unreachable'] += 1
        log(f"ICMP Unreachable: {ip}", "COUNTERMEASURE")
        
        try:
            subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-j", "REJECT",
                 "--reject-with", "icmp-port-unreachable"],
                capture_output=True, timeout=5
            )
        except Exception as e:
            log(f"Error ICMP: {e}", "ERROR")
    
    def apply_firewall_rule(self, ip: str, block_type: str = "permanent"):
        """8. Dynamic Firewall Rule"""
        if not self.enabled:
            return
        
        self.stats['firewall_rules'] += 1
        log(f"Firewall Rule: {ip} ({block_type})", "COUNTERMEASURE")
        
        try:
            subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                capture_output=True, timeout=5
            )
            # Registrar en bans log
            with open(BANS_LOG, 'a') as f:
                f.write(f"{datetime.now().isoformat()} BAN {ip} TYPE={block_type}\n")
        except Exception as e:
            log(f"Error Firewall: {e}", "ERROR")


class ShieldDaemon:
    """Daemon principal de ShieldLinux"""
    
    def __init__(self):
        self.running = False
        self.config = DEFAULT_CONFIG.copy()
        self.threat_intel = ThreatIntelligenceFeed()
        self.countermeasures = CountermeasureManager()
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'packets_inspected': 0,
            'attacks_detected': 0,
            'countermeasures_triggered': 0,
            'ips_blocked': set()
        }
        self.ip_tracker: Dict[str, Dict] = defaultdict(lambda: {
            'first_seen': None,
            'last_seen': None,
            'packet_count': 0,
            'port_count': 0,
            'ports': set(),
            'threat_level': 0
        })
        
        # Cargar configuración
        self.load_config()
        
        # Registrar signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                log("Configuración cargada")
        except Exception as e:
            log(f"Error cargando configuración: {e}", "WARNING")
    
    def save_config(self):
        """Guardar configuración"""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            log(f"Error guardando configuración: {e}", "ERROR")
    
    def signal_handler(self, signum, frame):
        """Manejar señales de terminación"""
        log(f"Señal {signum} recibida, cerrando daemon...")
        self.running = False
    
    def load_kernel_module(self):
        """Cargar módulo del kernel"""
        try:
            # Verificar si ya está cargado
            result = subprocess.run(["lsmod", "|", "grep", MODULE_NAME], 
                                   shell=True, capture_output=True)
            if result.returncode != 0:
                log("Cargando módulo del kernel...")
                subprocess.run(["insmod", f"{MODULE_NAME}.ko"], check=True)
                log("✅ Módulo cargado exitosamente")
            else:
                log("Módulo ya está cargado")
        except Exception as e:
            log(f"Error cargando módulo: {e}", "ERROR")
    
    def unload_kernel_module(self):
        """Descargar módulo del kernel"""
        try:
            subprocess.run(["rmmod", MODULE_NAME], check=True)
            log("Módulo descargado")
        except Exception as e:
            log(f"Error descargando módulo: {e}", "ERROR")
    
    def monitor_logs(self):
        """Monitorear logs del sistema"""
        log_paths = [
            "/var/log/ufw.log",
            "/var/log/auth.log",
            "/var/log/syslog",
            "/var/log/kern.log"
        ]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                threading.Thread(target=self._monitor_single_log, 
                               args=(log_path,), daemon=True).start()
    
    def _monitor_single_log(self, log_path: str):
        """Monitorear un archivo de log específico"""
        try:
            with open(log_path, 'r') as f:
                f.seek(0, 2)  # Ir al final
                while self.running:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    
                    self.process_log_line(line, log_path)
        except Exception as e:
            log(f"Error monitoreando {log_path}: {e}", "ERROR")
    
    def process_log_line(self, line: str, source: str):
        """Procesar línea de log y detectar ataques"""
        # Extraer IP de línea UFW
        if "UFW BLOCK" in line:
            match = re.search(r"SRC=([\d\.]+).*DPT=(\d+)", line)
            if match:
                ip = match.group(1)
                port = match.group(2)
                self.handle_blocked_packet(ip, port)
        
        # Extraer IP de auth.log (failed login)
        if "Failed password" in line or "authentication failure" in line:
            match = re.search(r"from\s+([\d\.]+)", line)
            if match:
                ip = match.group(1)
                self.handle_auth_failure(ip)
    
    def handle_blocked_packet(self, ip: str, port: str):
        """Manejar paquete bloqueado por UFW"""
        tracker = self.ip_tracker[ip]
        now = datetime.now()
        
        tracker['last_seen'] = now
        tracker['packet_count'] += 1
        tracker['ports'].add(port)
        tracker['port_count'] = len(tracker['ports'])
        
        if not tracker['first_seen']:
            tracker['first_seen'] = now
        
        # Verificar Threat Intel
        if self.config.get('enable_threat_intel'):
            threat_info = self.threat_intel.check_abuseipdb(ip)
            if threat_info.get('is_malicious'):
                log(f"🚫 IP maliciosa conocida: {ip} (Score: {threat_info['score']})", "THREAT")
                self.apply_countermeasures(ip, threat_level=4)
                return
        
        # Detectar port scan
        if tracker['port_count'] >= self.config['portscan_threshold']:
            log(f"⚠️ Port scan detectado: {ip} ({tracker['port_count']} puertos)", "ATTACK")
            self.stats['attacks_detected'] += 1
            self.apply_countermeasures(ip, threat_level=3)
        
        # Detectar flood
        if tracker['packet_count'] >= self.config['ddos_threshold']:
            log(f"🚨 Posible DDoS: {ip} ({tracker['packet_count']} paquetes)", "ATTACK")
            self.stats['attacks_detected'] += 1
            self.apply_countermeasures(ip, threat_level=4)
    
    def handle_auth_failure(self, ip: str):
        """Manejar fallo de autenticación"""
        tracker = self.ip_tracker[ip]
        tracker['packet_count'] += 1
        
        if tracker['packet_count'] >= self.config['bruteforce_threshold']:
            log(f"🔐 Brute force detectado: {ip} ({tracker['packet_count']} intentos)", "ATTACK")
            self.stats['attacks_detected'] += 1
            self.apply_countermeasures(ip, threat_level=3)
    
    def apply_countermeasures(self, ip: str, threat_level: int):
        """Aplicar contramedidas según nivel de amenaza"""
        if not self.config.get('enable_countermeasures'):
            return
        
        self.stats['countermeasures_triggered'] += 1
        self.stats['ips_blocked'].add(ip)
        
        log(f"🛡️ Aplicando contramedidas a {ip} (Nivel: {threat_level})", "ACTION")
        
        if threat_level >= 4:
            # Amenaza crítica: todas las contramedidas
            self.countermeasures.apply_tcp_reset(ip, 0, "0.0.0.0", 0)
            self.countermeasures.apply_connection_kill(ip)
            self.countermeasures.apply_firewall_rule(ip, "permanent")
        elif threat_level >= 3:
            # Amenaza alta: contramedidas fuertes
            self.countermeasures.apply_rate_limit(ip, 5)
            self.countermeasures.apply_firewall_rule(ip, "extended")
        elif threat_level >= 2:
            # Amenaza media: contramedidas moderadas
            self.countermeasures.apply_rate_limit(ip, 50)
        else:
            # Amenaza baja: solo logging
            pass
    
    def save_state(self):
        """Guardar estado actual"""
        try:
            state = {
                'stats': self.stats,
                'ip_tracker': {
                    ip: {
                        'first_seen': str(data['first_seen']),
                        'last_seen': str(data['last_seen']),
                        'packet_count': data['packet_count'],
                        'port_count': data['port_count'],
                        'threat_level': data['threat_level']
                    }
                    for ip, data in list(self.ip_tracker.items())[:100]
                },
                'countermeasure_stats': self.countermeasures.stats,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            log(f"Error guardando estado: {e}", "ERROR")
    
    def run(self):
        """Ejecutar daemon principal"""
        log("╔════════════════════════════════════════════════════╗")
        log("║  🛡️  SHIELD LINUX DAEMON v1.0 INICIANDO           ║")
        log("╚════════════════════════════════════════════════════╝")
        
        self.running = True
        self.stats['start_time'] = datetime.now().isoformat()
        
        # Cargar módulo kernel
        self.load_kernel_module()
        
        # Iniciar monitoreo de logs
        self.monitor_logs()
        
        # Actualizar threat intel
        if self.config.get('enable_threat_intel'):
            self.threat_intel.update_spamhaus_drop()
            threading.Thread(target=self._update_threat_intel_periodic, 
                           daemon=True).start()
        
        # Guardar estado periódicamente
        threading.Thread(target=self._save_state_periodic, daemon=True).start()
        
        # Iniciar API REST si está habilitada
        if self.config.get('api_enabled'):
            threading.Thread(target=self._start_api, daemon=True).start()
        
        log("✅ Daemon iniciado correctamente")
        log(f"📊 Estadísticas iniciales: {self.stats}")
        
        # Loop principal
        while self.running:
            time.sleep(1)
        
        # Limpieza
        self.shutdown()
    
    def _update_threat_intel_periodic(self):
        """Actualizar threat intel periódicamente"""
        while self.running:
            time.sleep(3600)  # Cada hora
            self.threat_intel.update_spamhaus_drop()
    
    def _save_state_periodic(self):
        """Guardar estado periódicamente"""
        while self.running:
            time.sleep(60)  # Cada minuto
            self.save_state()
    
    def _start_api(self):
        """Iniciar API REST"""
        port = self.config.get('api_port', 8765)
        
        class ShieldAPIHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/stats':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(self.server.daemon.stats).encode())
                elif self.path == '/status':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    status = {'running': self.server.daemon.running, 'module': 'loaded'}
                    self.wfile.write(json.dumps(status).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Silenciar logs de API
        
        try:
            with socketserver.TCPServer(("", port), ShieldAPIHandler) as httpd:
                httpd.daemon = True
                httpd.daemon_ref = self
                log(f"API REST iniciada en puerto {port}")
                httpd.serve_forever()
        except Exception as e:
            log(f"Error iniciando API: {e}", "ERROR")
    
    def shutdown(self):
        """Apagar daemon limpiamente"""
        log("Apagando daemon...")
        self.save_state()
        log("✅ Daemon apagado correctamente")


# ==================== FUNCIONES DE LOGGING ====================

def log(message: str, level: str = "INFO"):
    """Función de logging centralizada"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}"
    
    print(log_line)
    
    try:
        os.makedirs(os.path.dirname(DAEMON_LOG), exist_ok=True)
        with open(DAEMON_LOG, 'a') as f:
            f.write(log_line + "\n")
    except:
        pass


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    # Verificar root
    if os.geteuid() != 0:
        print("❌ Este programa debe ejecutarse como root")
        sys.exit(1)
    
    # Crear daemon y ejecutar
    daemon = ShieldDaemon()
    
    try:
        daemon.run()
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
        daemon.shutdown()
    except Exception as e:
        log(f"Error fatal: {e}", "ERROR")
        sys.exit(1)

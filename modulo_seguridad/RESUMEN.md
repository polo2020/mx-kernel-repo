# 🛡️ SHIELD LINUX - Módulo de Seguridad para Kernel
## Resumen Completo del Proyecto

---

## 📁 Estructura del Proyecto

```
/home/jean/Música/modulo_seguridad/
├── README.md                           # Documentación principal
├── kernel_module/                      # Módulo del kernel (C)
│   ├── Makefile                        # Compilación
│   ├── security_module.c               # Módulo principal
│   ├── security_module.h               # Cabeceras
│   ├── countermeasures.c               # 8 Contramedidas
│   ├── countermeasures.h
│   ├── detection.c                     # 7 Funciones reforzadas
│   └── detection.h
├── userspace_daemon/                   # Daemon Python
│   ├── shield_daemon.py                # Daemon principal
│   ├── shield_cli.py                   # CLI
│   └── requirements.txt                # Dependencias
├── scripts/                            # Scripts de instalación
│   ├── install.sh
│   ├── uninstall.sh
│   ├── load_module.sh
│   └── unload_module.sh
└── rules/                              # Reglas de detección
    ├── yara_rules/
    │   └── malware_detection.yar
    └── sigma_rules/
        └── attack_detection.yml
```

---

## 🔥 8 CONTRAMEDIDAS ACTIVAS

| # | Contramedida | Función | Impacto |
|---|--------------|---------|---------|
| 1 | **TCP Reset Injection** | Envía paquetes RST para terminar conexiones | ⚡ Inmediato |
| 2 | **SYN Cookie Advanced** | Protección criptográfica contra SYN floods | 🛡️ Preventivo |
| 3 | **Connection Kill Switch** | Termina conexiones establecidas de atacantes | ⚡ Inmediato |
| 4 | **Rate Limit Escalation** | Límite progresivo (100→50→10→1 pps) | 📉 Gradual |
| 5 | **Honeypot Redirect** | Redirige a puertos trampa para análisis | 🍯 Engaño |
| 6 | **Packet Blackhole** | Descarte silencioso con logging forense | 🕳️ Sigiloso |
| 7 | **ICMP Unreachable** | Envía ICMP tipo 3 para engañar atacante | 🎭 Engaño |
| 8 | **Dynamic Firewall Rules** | Genera reglas iptables automáticamente | 🔥 Permanente |

---

## ✅ 7 FUNCIONES REFORZADAS

| # | Función | Mejora | Detección |
|---|---------|--------|-----------|
| 9 | **Advanced Port Scan** | Multi-algoritmo (horizontal, vertical, block) | 🎯 5 puertos/60s |
| 10 | **DDoS Mitigation** | Protección capa 3/4/7 | 🌊 1000 pps |
| 11 | **Adaptive Rate Limit** | ML-based adjustment | 🤖 Dinámico |
| 12 | **CIDR + ASN Blocking** | Bloqueo por ISP/ASN | 🌐 Completo |
| 13 | **Deep Pattern Detection** | Regex + signatures + heurística | 🦠 Malware |
| 14 | **Threat Intel** | AbuseIPDB, Spamhaus, AlienVault | 🧠 IA |
| 15 | **Self-Healing** | Auto-recuperación de servicios | ♻️ Automático |

---

## 🛡️ FUNCIONES ORIGINALES ShieldLinux

- ✅ Detección de Port Scanning
- ✅ Detección de DDoS/DoS
- ✅ GeoIP Check
- ✅ IP Reputation
- ✅ Dynamic Rate Limiting
- ✅ CIDR Range Blocking (/24)
- ✅ Pattern Attack Detection
- ✅ Temporal Analysis
- ✅ Smart Whitelist
- ✅ Statistics & Reporting
- ✅ Adaptive Threshold
- ✅ Multi-Log Monitoring
- ✅ Automated Countermeasures
- ✅ Threat Intelligence
- ✅ Self-Healing

---

## 🚀 Instalación y Uso

### 1. Compilar módulo del kernel:

```bash
cd /home/jean/Música/modulo_seguridad/kernel_module
make
sudo make install
```

### 2. Instalar daemon:

```bash
sudo /home/jean/Música/modulo_seguridad/scripts/install.sh
```

### 3. Cargar módulo:

```bash
sudo /home/jean/Música/modulo_seguridad/scripts/load_module.sh
```

### 4. Iniciar daemon:

```bash
sudo systemctl start shield-daemon
sudo systemctl enable shield-daemon
```

---

## 🔧 Comandos CLI

```bash
# Ver estado
shield-cli status

# Ver estadísticas
shield-cli stats

# Generar reporte
shield-cli report

# Ver baneos
shield-cli bans

# Listar contramedidas
shield-cli countermeasures

# Configuración
shield-cli config get
shield-cli config set portscan_threshold 10

# Ver logs
shield-cli logs -n 100
shield-cli logs --forensics
```

---

## 📊 Estadísticas y Monitoreo

### API REST (puerto 8765):

```bash
# Ver estadísticas
curl http://localhost:8765/stats

# Ver estado
curl http://localhost:8765/status
```

### Logs:

```bash
# Log principal
tail -f /var/log/shield_daemon.log

# Log de baneos
tail -f /var/log/shield_bans.log

# Log forense
tail -f /var/log/shield_forensics.log

# Logs del kernel
dmesg | grep -i shield
journalctl -k | grep -i security_module
```

---

## 🔐 Configuración

Archivo: `/etc/shield/config.json`

```json
{
    "portscan_threshold": 5,
    "portscan_window": 60,
    "synflood_threshold": 100,
    "ddos_threshold": 1000,
    "bruteforce_threshold": 10,
    "bruteforce_window": 300,
    "ban_time_default": -1,
    "enable_countermeasures": true,
    "enable_threat_intel": true,
    "enable_forensics": true,
    "log_level": "INFO",
    "api_port": 8765,
    "api_enabled": true
}
```

---

## 📈 Flujo de Detección y Respuesta

```
1. Paquete entra → Netfilter Hook
2. Análisis → Detección de patrones
3. Verificación → Threat Intelligence
4. Clasificación → Nivel de amenaza (1-4)
5. Respuesta → Contramedida apropiada
6. Logging → Forensics detallado
7. Reporte → Estadísticas actualizadas
```

---

## 🎯 Niveles de Amenaza y Respuesta

| Nivel | Color | Contramedidas |
|-------|-------|---------------|
| **1 - Bajo** | 🟢 | Solo logging |
| **2 - Medio** | 🟡 | SYN Cookie + ICMP Unreachable |
| **3 - Alto** | 🟠 | Rate Limit + Honeypot + Firewall |
| **4 - Crítico** | 🔴 | TCP Reset + Connection Kill + Blackhole |

---

## 📚 Archivos del Sistema

| Archivo | Descripción |
|---------|-------------|
| `/lib/modules/$(uname -r)/kernel/security/security_module.ko` | Módulo kernel |
| `/usr/local/bin/shield_daemon.py` | Daemon userspace |
| `/usr/local/bin/shield-cli` | CLI |
| `/etc/shield/config.json` | Configuración |
| `/etc/shield/whitelist.json` | IPs permitidas |
| `/etc/shield/blacklist.json` | IPs bloqueadas |
| `/var/log/shield_daemon.log` | Log principal |
| `/var/log/shield_bans.log` | Log de baneos |
| `/var/log/shield_forensics.log` | Log forense |

---

## 🐛 Solución de Problemas

### El módulo no carga:
```bash
dmesg | tail -50
make clean && make
sudo make install
```

### El daemon no inicia:
```bash
systemctl status shield-daemon
journalctl -u shield-daemon -f
```

### Errores de compilación:
```bash
sudo apt-get install linux-headers-$(uname -r) build-essential
```

---

## 📄 Licencia

ShieldLinux Kernel Security Module v1.0
Basado en el proyecto original ShieldLinux v2.0

---

**🛡️ ¡Protección de nivel militar para tu kernel Linux!**

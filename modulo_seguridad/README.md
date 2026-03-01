# 🛡️ Kernel Security Module v1.0
## Módulo de Seguridad Avanzado para Kernel Linux

Módulo de seguridad del kernel con **22 funciones de protección activa** + **8 contramedidas automáticas** + **7 funciones reforzadas**.

---

## 📋 Características Principales

### 🔥 8 CONTRAMEDIDAS ACTIVAS (Countermeasures):

| # | Contramedida | Descripción |
|---|--------------|-------------|
| 1 | **TCP Reset Injection** | Envía paquetes RST para terminar conexiones maliciosas instantáneamente |
| 2 | **SYN Cookie Advanced** | Protección mejorada contra SYN floods con cookies criptográficas |
| 3 | **Connection Kill Switch** | Termina conexiones establecidas de atacantes |
| 4 | **Rate Limit Escalation** | Límite progresivo que se endurece con cada intento |
| 5 | **Honeypot Redirect** | Redirige atacantes a puertos honeypot para análisis |
| 6 | **Packet Blackhole** | Descarta paquetes silenciosamente con logging forense |
| 7 | **ICMP Unreachable** | Envía ICMP tipo 3 para engañar al atacante |
| 8 | **Dynamic Firewall Rules** | Genera reglas iptables/nftables automáticamente |

### ✅ 7 FUNCIONES REFORZADAS:

| # | Función | Mejora |
|---|---------|--------|
| 9 | **Advanced Port Scan Detection** | Multi-algoritmo: horizontal, vertical, block scan |
| 10 | **DDoS Mitigation Engine** | Protección capa 3/4/7 con mitigación automática |
| 11 | **Adaptive Rate Limiting** | ML-based rate adjustment según comportamiento |
| 12 | **CIDR + ASN Blocking** | Bloqueo por rango IP y número de sistema autónomo |
| 13 | **Deep Pattern Detection** | Regex + signature matching + heurística |
| 14 | **Threat Intel Integration** | Múltiples feeds (AbuseIPDB, Spamhaus, AlienVault) |
| 15 | **Self-Healing + Auto-Recovery** | Monitoreo y recuperación automática de servicios |

### 🛡️ FUNCIONES ORIGINALES ShieldLinux:

| Función | Descripción |
|---------|-------------|
| Detección de Port Scanning | Detecta escaneo de múltiples puertos |
| Detección de DDoS/DoS | Detecta ráfagas de conexiones por segundo |
| GeoIP Check | Clasificación geográfica de IPs |
| IP Reputation | Verifica contra blacklist/whitelist |
| Dynamic Rate Limiting | Límite dinámico según comportamiento |
| CIDR Range Blocking | Banea rangos completos de IPs (/24) |
| Pattern Attack Detection | Detecta SSH brute-force, HTTP, MySQL, etc. |
| Temporal Analysis | Detecta ataques automatizados por regularidad |
| Smart Whitelist | Gestión inteligente con IPs locales auto-whitelisted |
| Statistics & Reporting | Reportes completos con top atacantes |
| Adaptive Threshold | Threshold se ajusta según historial |
| Multi-Log Monitoring | Soporte para auth.log, syslog, nginx, fail2ban |
| Automated Countermeasures | Acciones por severidad |
| Threat Intelligence | Integración con bases de amenazas |
| Self-Healing | Health check y auto-remediación |

---

## 📦 Estructura del Módulo

```
modulo_seguridad/
├── kernel_module/
│   ├── Makefile              # Compilación del módulo kernel
│   ├── security_module.c     # Módulo principal del kernel
│   ├── security_module.h     # Cabeceras y definiciones
│   ├── countermeasures.c     # 8 contramedidas activas
│   ├── countermeasures.h
│   ├── detection.c           # 7 funciones reforzadas
│   └── detection.h
├── userspace_daemon/
│   ├── shield_daemon.py      # Daemon principal Python
│   ├── shield_cli.py         # CLI de línea de comandos
│   ├── shield_gui.py         # Interfaz gráfica
│   ├── config.json           # Configuración
│   └── requirements.txt      # Dependencias Python
├── scripts/
│   ├── install.sh            # Instalación automática
│   ├── uninstall.sh          # Desinstalación
│   ├── load_module.sh        # Cargar módulo kernel
│   └── unload_module.sh      # Descargar módulo
├── rules/
│   ├── yara_rules/           # Reglas YARA para malware
│   ├── sigma_rules/          # Reglas MITRE ATT&CK
│   └── signatures/           # Firmas de ataques
└── docs/
    ├── INSTALL.md            # Guía de instalación
    ├── CONFIGURATION.md      # Configuración detallada
    └── API.md                # Documentación de API
```

---

## 🚀 Instalación Rápida

### 1. Compilar módulo del kernel:

```bash
cd /home/jean/Música/modulo_seguridad/kernel_module
make
```

### 2. Instalar daemon y herramientas:

```bash
sudo ./scripts/install.sh
```

### 3. Cargar módulo:

```bash
sudo insmod security_module.ko
# O para cargar automáticamente al inicio:
sudo ./scripts/load_module.sh
```

### 4. Iniciar daemon:

```bash
sudo systemctl start shield-daemon
sudo systemctl enable shield-daemon
```

---

## 🔧 Comandos

### Usando shield-cli:

```bash
shield-cli status          # Ver estado
shield-cli start           # Iniciar
shield-cli stop            # Detener
shield-cli countermeasures # Listar contramedidas activas
shield-cli report          # Reporte de seguridad
shield-cli bans            # Ver baneos
shield-cli stats           # Estadísticas
```

### Ver logs del kernel:

```bash
dmesg | grep -i shield
journalctl -k | grep -i security_module
```

---

## 📊 Ejemplo de Uso

### Activar contramedida TCP Reset:

```bash
sudo shield-cli countermeasure enable tcp_reset
```

### Configurar detección de port scan:

```bash
sudo shield-cli config set portscan_threshold 5
sudo shield-cli config set portscan_window 60
```

### Ver estadísticas en tiempo real:

```bash
watch -n 1 'shield-cli stats'
```

---

## 🔐 API de Contramedidas

El módulo expone las siguientes contramedidas vía ioctl:

```c
#define SHIELD_IOC_TCP_RESET      _IOW('S', 1, struct shield_rule)
#define SHIELD_IOC_SYN_COOKIE     _IOW('S', 2, struct shield_rule)
#define SHIELD_IOC_CONN_KILL      _IOW('S', 3, struct shield_rule)
#define SHIELD_IOC_RATE_ESCALATE  _IOW('S', 4, struct shield_rule)
#define SHIELD_IOC_HONEYPOT       _IOW('S', 5, struct shield_rule)
#define SHIELD_IOC_BLACKHOLE      _IOW('S', 6, struct shield_rule)
#define SHIELD_IOC_ICMP_UNREACH   _IOW('S', 7, struct shield_rule)
#define SHIELD_IOC_FW_RULE        _IOW('S', 8, struct shield_rule)
```

---

## 📁 Archivos del Sistema

| Archivo | Descripción |
|---------|-------------|
| `/lib/modules/$(uname -r)/kernel/security/security_module.ko` | Módulo kernel |
| `/usr/local/bin/shield-daemon` | Daemon userspace |
| `/usr/local/bin/shield-cli` | CLI |
| `/usr/local/bin/shield-gui` | GUI |
| `/etc/shield/config.json` | Configuración |
| `/var/log/shield.log` | Log principal |
| `/var/log/shield_bans.log` | Log de baneos |
| `/var/log/shield_forensics.log` | Log forense |

---

## 🐛 Solución de Problemas

### El módulo no carga:

```bash
# Verificar logs del kernel
dmesg | tail -50

# Verificar versión del kernel
uname -r

# Recompile el módulo
make clean && make
```

### El daemon no inicia:

```bash
# Verificar estado
systemctl status shield-daemon

# Ver logs
journalctl -u shield-daemon -f
```

---

## 📄 Licencia

Kernel Security Module v1.0 - Basado en ShieldLinux v2.0

---

**🛡️ ¡Protección activa de nivel militar para tu kernel!**

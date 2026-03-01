# 🛡️ ShieldLinux v2.0
## Sistema de Seguridad Avanzado para MX Linux Live ISO

Daemon de monitoreo y protección automática para UFW con **15 funciones de seguridad potenciadas con IA** + **GUI Manager**.

---

## 📋 Características Principales

| Función | Descripción |
|---------|-------------|
| 🎯 **Detección de Port Scanning** | Detecta escaneo de múltiples puertos |
| 🚨 **Detección de DDoS/DoS** | Detecta ráfagas de conexiones por segundo |
| 🌍 **GeoIP Check** | Clasificación geográfica de IPs |
| 📊 **IP Reputation** | Verifica contra blacklist/whitelist/known attackers |
| ⚡ **Dynamic Rate Limiting** | Límite dinámico según comportamiento |
| 🎭 **CIDR Range Blocking** | Banea rangos completos de IPs (/24) |
| 🔍 **Pattern Attack Detection** | Detecta SSH brute-force, HTTP, MySQL, etc. |
| 🕐 **Temporal Analysis** | Detecta ataques automatizados por regularidad |
| ✅ **Smart Whitelist** | Gestión inteligente con IPs locales auto-whitelisted |
| 📈 **Statistics & Reporting** | Reportes completos con top atacantes |
| 🎚️ **Adaptive Threshold** | Threshold se ajusta según historial (1-3 intentos) |
| 📁 **Multi-Log Monitoring** | Soporte para auth.log, syslog, nginx, fail2ban |
| 🛡️ **Automated Countermeasures** | Acciones por severidad (log/temp ban/permanent/CIDR) |
| 🧠 **Threat Intelligence** | Integración con bases de amenazas |
| 🔧 **Self-Healing** | Health check y auto-remediación de UFW |
| 🖥️ **GUI Manager** | Interfaz gráfica con tema cybersecurity |

---

## 📦 Instalación Rápida

### En sistema instalado:

```bash
cd /home/jean/Música/seguridad
sudo ./install.sh
```

### El instalador:
1. ✅ Instala dependencias (Python3, UFW, systemd, PySide6, Pillow)
2. ✅ Copia el daemon a `/usr/local/bin/shield-linux`
3. ✅ Copia la GUI a `/usr/local/bin/shield-manager`
4. ✅ Crea el servicio systemd
5. ✅ Configura UFW con logging
6. ✅ Crea archivos de configuración
7. ✅ Genera/copía el tema visual
8. ✅ Configura logrotate
9. ✅ Habilita el servicio

---

## 🚀 Uso en MX Linux Live ISO

### Opción 1: Instalación en la ISO antes de construir

```bash
# En el entorno de construcción de la ISO
sudo ./install.sh
sudo ./post-install-config.sh
```

### Opción 2: Instalación manual en la ISO

1. Copie la carpeta `seguridad` a la estructura de la ISO
2. Ejecute `install.sh` durante el proceso de construcción
3. Ejecute `post-install-config.sh` para integración live

### Autoinicio en Live ISO

El daemon se inicia automáticamente gracias a:
- `/etc/rc.local` - Script de autoinicio
- `/etc/init.d/shield-linux-live` - Init script SysV
- `/etc/systemd/system/shield-linux-persist.service` - Persistencia

---

## 🔧 Comandos de Gestión

### Usando shield-cli (línea de comandos):

```bash
shield-cli status      # Ver estado del daemon
shield-cli start       # Iniciar
shield-cli stop        # Detener
shield-cli restart     # Reiniciar
shield-cli report      # Reporte de seguridad
shield-cli bans        # Ver logs de baneos
shield-cli stats       # Estadísticas
shield-cli whitelist   # Ver whitelist
shield-cli blacklist   # Ver blacklist
```

### Usando GUI Manager (interfaz gráfica):

```bash
sudo shield-manager    # Abrir interfaz gráfica
```

La GUI incluye:
- 📊 Dashboard en tiempo real
- 📋 Monitoreo de logs
- ⚙️ Gestión de whitelist/blacklist
- 🎮 Control del servicio
- 📈 Estadísticas visuales

### Usando systemctl:

```bash
sudo systemctl start shield-linux
sudo systemctl stop shield-linux
sudo systemctl restart shield-linux
sudo systemctl status shield-linux
sudo journalctl -u shield-linux -f  # Ver logs en tiempo real
```

---

## 📁 Archivos del Sistema

| Archivo | Descripción |
|---------|-------------|
| `/usr/local/bin/shield-linux` | Daemon principal |
| `/usr/local/bin/shield-manager` | GUI Manager |
| `/etc/systemd/system/shield-linux.service` | Servicio systemd |
| `/etc/shield_linux/shield_state.json` | Estado persistente |
| `/etc/shield_linux/whitelist.json` | IPs permitidas |
| `/etc/shield_linux/blacklist.json` | IPs bloqueadas |
| `/etc/shield_linux/tema.jpg` | Tema visual |
| `/var/log/ufw.log` | Log de UFW (entrada) |
| `/var/log/shield_bans.log` | Log de baneos (salida) |

---

## ⚙️ Configuración

### Editar threshold y opciones:

Edite `/usr/local/bin/shield-linux` (sección de configuración):

```python
THRESHOLD = 3              # Intentos antes de banear
BAN_TIME_DEFAULT = -1      # -1 = permanente, >0 = minutos
SCAN_THRESHOLD = 5         # Puertos para detectar port scanning
DDOS_THRESHOLD = 50        # Conexiones/seg para detectar DDoS
RATE_LIMIT_WINDOW = 60     # Ventana de tiempo en segundos
```

### Agregar IP a whitelist:

```bash
# Editar manualmente
sudo nano /etc/shield_linux/whitelist.json

# O usar shield-cli
shield-cli whitelist  # Ver
# Editar JSON agregando IP al array "ips"
```

### Agregar IP a blacklist:

```bash
# Editar manualmente
sudo nano /etc/shield_linux/blacklist.json
```

---

## 🔍 Ver Logs

```bash
# Logs del daemon
sudo journalctl -u shield-linux -f

# Baneos registrados
cat /var/log/shield_bans.log

# Actividad de UFW
tail -f /var/log/ufw.log | grep "UFW BLOCK"
```

---

## 🛡️ Estructura de la ISO Live

Para integrar ShieldLinux en una ISO Live de MX Linux:

```
iso_root/
├── live/
│   └── persistence/
│       └── shield_linux/      # Configuración persistente
├── etc/
│   ├── rc.local               # Autoinicio
│   ├── init.d/
│   │   └── shield-linux-live  # Init script
│   └── systemd/
│       └── system/
│           └── shield-linux*.service
└── usr/
    └── local/
        └── bin/
            ├── shield-linux   # Daemon
            ├── shield-cli     # CLI
            └── shield-live-init  # Init live
```

---

## 📊 Ejemplo de Reporte

```
╔════════════════════════════════════════╗
║  🛡️  SHIELD LINUX - REPORTE           ║
╠════════════════════════════════════════╣
║  Ataques totales:    1247              ║
║  Bans totales:        342              ║
║  IPs baneadas:         89              ║
║  Inicio:     2026-02-25T10:30:00       ║
╚════════════════════════════════════════╝
```

---

## 🔐 Consideraciones de Seguridad

1. **Requiere root**: El daemon debe ejecutarse como root
2. **UFW activo**: Asegúrese de que UFW esté habilitado
3. **Logging**: Configure `sudo ufw logging on`
4. **Persistencia**: En sistemas live, use `/live/persistence/`

---

## 🐛 Solución de Problemas

### El daemon no inicia:
```bash
# Verificar UFW
sudo ufw status

# Verificar logs
sudo journalctl -u shield-linux -n 50

# Verificar permisos
ls -la /usr/local/bin/shield-linux
```

### UFW no está activo:
```bash
sudo ufw enable
sudo ufw logging on
```

### Error de permisos:
```bash
sudo chmod +x /usr/local/bin/shield-linux
sudo chown root:root /usr/local/bin/shield-linux
```

---

## 📄 Licencia

ShieldLinux v2.0 - Sistema de seguridad avanzado para MX Linux

---

## 🤝 Contribuciones

Para reportar bugs o sugerencias, contacte al equipo de desarrollo.

---

**🛡️ ¡Protege tu sistema con inteligencia artificial!**

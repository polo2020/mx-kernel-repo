#!/bin/bash
# 🛡️ SHIELD LINUX - Script de Instalación
# Instala módulo de seguridad del kernel y daemon

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║  🛡️  SHIELD LINUX - INSTALADOR                    ║"
echo "╚════════════════════════════════════════════════════╝"

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script debe ejecutarse como root"
    exit 1
fi

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$SCRIPT_DIR/kernel_module"
DAEMON_DIR="$SCRIPT_DIR/userspace_daemon"
RULES_DIR="$SCRIPT_DIR/rules"

INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="/etc/shield"
LOG_DIR="/var/log"
MODULE_INSTALL_DIR="/lib/modules/$(uname -r)/kernel/security"

echo -e "${BLUE}[*] Iniciando instalación...${NC}"

# 1. Crear directorios
echo -e "${BLUE}[*] Creando directorios...${NC}"
mkdir -p "$CONFIG_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$MODULE_INSTALL_DIR"
mkdir -p "$CONFIG_DIR/yara_rules"
mkdir -p "$CONFIG_DIR/sigma_rules"

# 2. Instalar dependencias
echo -e "${BLUE}[*] Instalando dependencias...${NC}"
apt-get update
apt-get install -y python3 python3-pip iptables net-tools procps \
    build-essential linux-headers-$(uname -r) kmod jq ss || {
    echo -e "${YELLOW}[!] Algunas dependencias no pudieron instalarse${NC}"
}

# 3. Compilar módulo del kernel
echo -e "${BLUE}[*] Compilando módulo del kernel...${NC}"
cd "$MODULE_DIR"
make clean
make

if [ -f "security_module.ko" ]; then
    echo -e "${GREEN}[✓] Módulo compilado exitosamente${NC}"
    
    # Copiar módulo
    cp security_module.ko "$MODULE_INSTALL_DIR/"
    echo -e "${GREEN}[✓] Módulo copiado a $MODULE_INSTALL_DIR${NC}"
    
    # Actualizar dependencias
    depmod -a
    echo -e "${GREEN}[✓] Dependencias actualizadas${NC}"
else
    echo -e "${RED}[✗] Error compilando módulo${NC}"
    echo -e "${YELLOW}[!] El daemon userspace funcionará sin el módulo kernel${NC}"
fi

# 4. Instalar daemon y herramientas
echo -e "${BLUE}[*] Instalando daemon y herramientas...${NC}"
cp "$DAEMON_DIR/shield_daemon.py" "$INSTALL_DIR/"
cp "$DAEMON_DIR/shield_cli.py" "$INSTALL_DIR/shield-cli"
chmod +x "$INSTALL_DIR/shield_daemon.py"
chmod +x "$INSTALL_DIR/shield-cli"

echo -e "${GREEN}[✓] Daemon instalado en $INSTALL_DIR${NC}"

# 5. Crear configuración por defecto
echo -e "${BLUE}[*] Creando configuración...${NC}"
cat > "$CONFIG_DIR/config.json" << 'EOF'
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
EOF

# Crear archivos de listas vacíos
echo '{"ips": []}' > "$CONFIG_DIR/whitelist.json"
echo '{"ips": []}' > "$CONFIG_DIR/blacklist.json"

echo -e "${GREEN}[✓] Configuración creada${NC}"

# 6. Crear servicio systemd
echo -e "${BLUE}[*] Creando servicio systemd...${NC}"
cat > /etc/systemd/system/shield-daemon.service << EOF
[Unit]
Description=ShieldLinux Security Daemon
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/shield_daemon.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=shield-daemon

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable shield-daemon

echo -e "${GREEN}[✓] Servicio systemd creado${NC}"

# 7. Configurar logs
echo -e "${BLUE}[*] Configurando logs...${NC}"
touch "$LOG_DIR/shield_daemon.log"
touch "$LOG_DIR/shield_bans.log"
touch "$LOG_DIR/shield_forensics.log"
chmod 640 "$LOG_DIR/shield_*.log"

echo -e "${GREEN}[✓] Logs configurados${NC}"

# 8. Configurar UFW
echo -e "${BLUE}[*] Configurando UFW...${NC}"
ufw logging on 2>/dev/null || true
echo -e "${GREEN}[✓] UFW configurado${NC}"

# 9. Copiar reglas YARA/Sigma
echo -e "${BLUE}[*] Instalando reglas de detección...${NC}"
if [ -d "$RULES_DIR" ]; then
    cp -r "$RULES_DIR"/* "$CONFIG_DIR/" 2>/dev/null || true
    echo -e "${GREEN}[✓] Reglas instaladas${NC}"
fi

# 10. Resumen
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  🛡️  INSTALACIÓN COMPLETADA                       ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║  Módulo Kernel:     $MODULE_INSTALL_DIR          ║"
echo "║  Daemon:            $INSTALL_DIR/shield_daemon.py ║"
echo "║  CLI:               $INSTALL_DIR/shield-cli       ║"
echo "║  Configuración:     $CONFIG_DIR                   ║"
echo "║  Logs:              $LOG_DIR                      ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║  COMANDOS ÚTILES:                                  ║"
echo "║  sudo systemctl start shield-daemon   # Iniciar   ║"
echo "║  sudo systemctl stop shield-daemon    # Detener   ║"
echo "║  sudo systemctl status shield-daemon  # Estado    ║"
echo "║  shield-cli status                    # Ver estado ║"
echo "║  shield-cli stats                     # Estadísticas║"
echo "║  shield-cli report                    # Reporte    ║"
echo "╚════════════════════════════════════════════════════╝"

# Preguntar si iniciar ahora
read -p "¿Desea iniciar el daemon ahora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    systemctl start shield-daemon
    echo -e "${GREEN}[✓] Daemon iniciado${NC}"
    systemctl status shield-daemon --no-pager
fi

echo ""
echo -e "${GREEN}✅ Instalación completada exitosamente${NC}"

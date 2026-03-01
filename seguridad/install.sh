#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 🛡️ SHIELD LINUX - Script de Instalación para MX Linux Live ISO
# ═══════════════════════════════════════════════════════════════

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Rutas
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="/etc/shield_linux"
SYSTEMD_DIR="/etc/systemd/system"
USR_BIN_DIR="/usr/local/bin"
LOG_DIR="/var/log"
VAR_LIB_DIR="/var/lib/shield_linux"

# Archivos
DAEMON_FILE="$SCRIPT_DIR/shield_daemon_updated.py"
SERVICE_FILE="$SCRIPT_DIR/shield-linux.service"
POSTINST_FILE="$SCRIPT_DIR/post-install-config.sh"

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🛡️  SHIELD LINUX - Instalador para MX Linux Live     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si es root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[!] Este script debe ejecutarse como root${NC}"
   echo "    Use: sudo ./install.sh"
   exit 1
fi

# Detectar si es sistema Live
detect_live_system() {
    if grep -q "live-media" /proc/cmdline 2>/dev/null || \
       grep -q "boot=live" /proc/cmdline 2>/dev/null || \
       [ -f /live/iso/VERSION ] || \
       [ -d /live ]; then
        return 0
    fi
    return 1
}

# Detectar MX Linux
detect_mxlinux() {
    if [ -f /etc/mx-version ] || grep -q "MX" /etc/os-release 2>/dev/null; then
        return 0
    fi
    return 1
}

echo -e "${BLUE}[ℹ] Detectando sistema...${NC}"

IS_LIVE=false
IS_MX=false

if detect_live_system; then
    IS_LIVE=true
    echo -e "${YELLOW}[!] Sistema LIVE detectado${NC}"
fi

if detect_mxlinux; then
    IS_MX=true
    echo -e "${GREEN}[✓] MX Linux detectado${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# PASO 1: Instalar dependencias
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[1/8] Instalando dependencias...${NC}"

apt-get update -qq

# Paquetes esenciales
PACKAGES=(
    "python3"
    "python3-pip"
    "ufw"
    "systemd"
    "logrotate"
    "sudo"
    "pyside6"
    "python3-pil"
)

for pkg in "${PACKAGES[@]}"; do
    # Verificar instalación con nombres alternativos
    if dpkg -l | grep -qE "^ii  ($pkg|python3-$pkg) "; then
        echo -e "  ${GREEN}[✓]${NC} $pkg ya instalado"
    else
        echo -e "  ${YELLOW}[⏳]${NC} Instalando $pkg..."
        apt-get install -y -qq "$pkg" 2>/dev/null || \
        apt-get install -y -qq "python3-$pkg" 2>/dev/null || \
        echo -e "  ${YELLOW}[⚠]${NC} $pkg no disponible (puede estar instalado con otro nombre)"
    fi
done

# ═══════════════════════════════════════════════════════════════
# PASO 2: Crear directorios
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[2/8] Creando directorios...${NC}"

DIRECTORIES=(
    "$CONFIG_DIR"
    "$VAR_LIB_DIR"
    "$LOG_DIR"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "  ${GREEN}[✓]${NC} Creado: $dir"
    else
        echo -e "  ${GREEN}[✓]${NC} Existe: $dir"
    fi
done

# ═══════════════════════════════════════════════════════════════
# PASO 3: Copiar archivos del daemon
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[3/8] Copiando archivos del daemon...${NC}"

# Copiar daemon a /usr/local/bin
if [ -f "$DAEMON_FILE" ]; then
    cp "$DAEMON_FILE" "$USR_BIN_DIR/shield-linux"
    chmod +x "$USR_BIN_DIR/shield-linux"
    echo -e "  ${GREEN}[✓]${NC} Daemon instalado en $USR_BIN_DIR/shield-linux"
else
    echo -e "  ${RED}[!]${NC} No se encontró: $DAEMON_FILE"
    exit 1
fi

# Copiar manager GUI
MANAGER_FILE="$SCRIPT_DIR/shield_manager.py"
if [ -f "$MANAGER_FILE" ]; then
    cp "$MANAGER_FILE" "$USR_BIN_DIR/shield-manager"
    chmod +x "$USR_BIN_DIR/shield-manager"
    echo -e "  ${GREEN}[✓]${NC} GUI Manager instalado en $USR_BIN_DIR/shield-manager"
fi

# Copiar/generar tema
THEME_FILE="$SCRIPT_DIR/tema.jpg"
if [ -f "$THEME_FILE" ]; then
    cp "$THEME_FILE" "$CONFIG_DIR/tema.jpg"
    echo -e "  ${GREEN}[✓]${NC} Tema copiado a $CONFIG_DIR/tema.jpg"
else
    # Generar tema si no existe
    echo -e "  ${YELLOW}[⏳]${NC} Generando tema..."
    python3 "$SCRIPT_DIR/generate_theme.py" 2>/dev/null || true
    if [ -f "$CONFIG_DIR/tema.jpg" ]; then
        echo -e "  ${GREEN}[✓]${NC} Tema generado"
    fi
fi

# ═══════════════════════════════════════════════════════════════
# PASO 4: Crear archivo de configuración inicial
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[4/8] Creando archivos de configuración...${NC}"

# Whitelist inicial (vacía)
cat > "$CONFIG_DIR/whitelist.json" << 'EOF'
{
  "ips": [],
  "updated": "initial_install"
}
EOF
echo -e "  ${GREEN}[✓]${NC} whitelist.json creado"

# Blacklist inicial (vacía)
cat > "$CONFIG_DIR/blacklist.json" << 'EOF'
{
  "ips": [],
  "updated": "initial_install"
}
EOF
echo -e "  ${GREEN}[✓]${NC} blacklist.json creado"

# Estado inicial
cat > "$CONFIG_DIR/shield_state.json" << 'EOF'
{
  "attack_counter": {},
  "attack_timestamps": {},
  "banned_ips": [],
  "temp_bans": {},
  "statistics": {
    "total_attacks": 0,
    "total_bans": 0,
    "total_blocks": 0,
    "start_time": null,
    "last_attack": null,
    "top_attackers": [],
    "attacks_by_day": {}
  }
}
EOF
echo -e "  ${GREEN}[✓]${NC} shield_state.json creado"

# ═══════════════════════════════════════════════════════════════
# PASO 5: Crear servicio systemd
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[5/8] Creando servicio systemd...${NC}"

cat > "$SYSTEMD_DIR/shield-linux.service" << 'EOF'
[Unit]
Description=ShieldLinux Security Daemon
Documentation=https://github.com/shield-linux
After=network.target ufw.service
Wants=ufw.service

[Service]
Type=simple
ExecStart=/usr/local/bin/shield-linux
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=shield-linux

# Seguridad del servicio
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/etc/shield_linux /var/log /var/lib/shield_linux

# Logging
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo -e "  ${GREEN}[✓]${NC} shield-linux.service creado"

# Recargar systemd
systemctl daemon-reload
echo -e "  ${GREEN}[✓]${NC} systemd recargado"

# ═══════════════════════════════════════════════════════════════
# PASO 6: Configurar UFW
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[6/8] Configurando UFW...${NC}"

# Habilitar logging de UFW
if ! grep -q "^LOGLEVEL=" /etc/ufw/ufw.conf 2>/dev/null; then
    echo "LOGLEVEL=medium" >> /etc/ufw/ufw.conf
    echo -e "  ${GREEN}[✓]${NC} Logging UFW configurado"
fi

# Asegurar que el log exista
touch /var/log/ufw.log
chmod 640 /var/log/ufw.log
echo -e "  ${GREEN}[✓]${NC} /var/log/ufw.log creado"

# Reglas UFW por defecto (seguras)
echo -e "  ${YELLOW}[ℹ]${NC} Configurando reglas UFW por defecto..."

# Solo si UFW no está configurado
if ! ufw status verbose 2>/dev/null | grep -q "Status: active"; then
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw logging on
    echo -e "  ${GREEN}[✓]${NC} Reglas UFW configuradas"
else
    echo -e "  ${GREEN}[✓]${NC} UFW ya está configurado"
fi

# ═══════════════════════════════════════════════════════════════
# PASO 7: Configurar logrotate
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[7/8] Configurando logrotate...${NC}"

cat > /etc/logrotate.d/shield-linux << 'EOF'
/var/log/shield_bans.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root adm
    postrotate
        systemctl reload shield-linux 2>/dev/null || true
    endscript
}
EOF

echo -e "  ${GREEN}[✓]${NC} logrotate configurado"

# ═══════════════════════════════════════════════════════════════
# PASO 8: Habilitar y iniciar servicio
# ═══════════════════════════════════════════════════════════════
echo -e "\n${BLUE}[8/8] Habilitando servicio...${NC}"

if [ "$IS_LIVE" = true ]; then
    echo -e "  ${YELLOW}[⚠]${NC} Sistema LIVE: El servicio NO se habilitará permanentemente"
    echo -e "  ${YELLOW}[ℹ]${NC} Para ISO Live, use el script post-install.sh"
else
    systemctl enable shield-linux
    echo -e "  ${GREEN}[✓]${NC} Servicio habilitado para inicio automático"
fi

# ═══════════════════════════════════════════════════════════════
# Configuración específica para MX Linux Live ISO
# ═══════════════════════════════════════════════════════════════
if [ "$IS_LIVE" = true ] || [ "$IS_MX" = true ]; then
    echo -e "\n${CYAN}[📦] Configuración especial para MX Linux Live...${NC}"
    
    # Crear script de post-instalación para la ISO
    cat > "$POSTINST_FILE" << 'POSTINST_EOF'
#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 🛡️ SHIELD LINUX - Post-Instalación para MX Linux Live ISO
# Este script se ejecuta cuando la ISO live inicia
# ═══════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🛡️  SHIELD LINUX - Configuración Live ISO            ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Habilitar UFW si no está activo
if ! ufw status 2>/dev/null | grep -q "Status: active"; then
    echo "[✓] Activando UFW..."
    echo "y" | ufw enable
fi

# Iniciar el daemon de ShieldLinux
echo "[✓] Iniciando ShieldLinux Daemon..."
systemctl start shield-linux

# Verificar estado
sleep 2
if systemctl is-active --quiet shield-linux; then
    echo "[✓] ShieldLinux está activo y monitoreando"
else
    echo "[!] ShieldLinux no pudo iniciarse"
fi

# Mostrar estado de UFW
echo ""
echo "=== Estado de UFW ==="
ufw status verbose
POSTINST_EOF

    chmod +x "$POSTINST_FILE"
    echo -e "  ${GREEN}[✓]${NC} post-install-config.sh creado"
    
    # Para integración en ISO: copiar a /etc/rc.local o similar
    # En MX Linux live, se puede agregar al boot process
    
    # Crear script de autoinicio para live
    cat > /etc/rc.local << 'RCLOCAL_EOF'
#!/bin/bash
# Autoinicio para ShieldLinux en Live ISO
if [ -x /usr/local/bin/shield-linux ]; then
    # Esperar a que la red esté disponible
    sleep 5
    
    # Activar UFW si es necesario
    if ! ufw status 2>/dev/null | grep -q "Status: active"; then
        echo "y" | ufw enable 2>/dev/null || true
    fi
    
    # Iniciar daemon
    /usr/local/bin/shield-linux &
fi
exit 0
RCLOCAL_EOF

    chmod +x /etc/rc.local
    echo -e "  ${GREEN}[✓]${NC} rc.local configurado para autoinicio"
fi

# ═══════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════
echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🛡️  INSTALACIÓN COMPLETADA EXITOSAMENTE           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}📋 Archivos instalados:${NC}"
echo "  • Daemon:     $USR_BIN_DIR/shield-linux"
echo "  • GUI:        $USR_BIN_DIR/shield-manager"
echo "  • Servicio:   $SYSTEMD_DIR/shield-linux.service"
echo "  • Config:     $CONFIG_DIR/"
echo "  • Tema:       $CONFIG_DIR/tema.jpg"
echo "  • Logs:       $LOG_DIR/ufw.log, $LOG_DIR/shield_bans.log"

echo -e "\n${CYAN}🔧 Comandos útiles:${NC}"
echo "  • Iniciar daemon:   sudo systemctl start shield-linux"
echo "  • Abrir GUI:        sudo shield-manager"
echo "  • Ver estado:       sudo systemctl status shield-linux"
echo "  • Ver logs:         sudo journalctl -u shield-linux -f"
echo "  • Ver bans:         cat /var/log/shield_bans.log"

if [ "$IS_LIVE" = true ]; then
    echo -e "\n${YELLOW}⚠️  SISTEMA LIVE DETECTADO:${NC}"
    echo "   Los cambios no persistirán después del reinicio."
    echo "   Para integración permanente en la ISO:"
    echo "   1. Copie este instalador a la estructura de la ISO"
    echo "   2. Ejecute post-install-config.sh en el boot de la ISO"
    echo "   3. O integre en /etc/rc.local o scripts de live-boot"
fi

echo -e "\n${GREEN}[✓] ¡ShieldLinux está listo para proteger tu sistema!${NC}"

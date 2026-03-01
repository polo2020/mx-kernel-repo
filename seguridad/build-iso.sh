#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 🛡️ SHIELD LINUX - Script para Construir ISO con ShieldLinux
# Para MX Linux Live ISO
# ═══════════════════════════════════════════════════════════════

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🛡️  SHIELD LINUX - Constructor de ISO Live              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[!] Este script debe ejecutarse como root${NC}"
   exit 1
fi

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIELD_DIR="$SCRIPT_DIR"

# Puntos de montaje
ISO_MOUNT="/mnt/iso_source"
ISO_OUTPUT="/mnt/iso_output"
WORK_DIR="/tmp/shield_iso_work"

echo -e "\n${BLUE}[ℹ] Configuración:${NC}"
echo "  Directorio ShieldLinux: $SHIELD_DIR"
echo "  Montaje ISO: $ISO_MOUNT"
echo "  Output ISO: $ISO_OUTPUT"
echo "  Work dir: $WORK_DIR"

# ═══════════════════════════════════════════════════════════════
# PASO 1: Preparar entorno
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}[1/6] Preparando entorno de trabajo...${NC}"

# Instalar herramientas necesarias
apt-get update -qq
apt-get install -y -qq genisoimage xorriso squashfs-tools rsync

# Crear directorios
mkdir -p "$ISO_MOUNT" "$ISO_OUTPUT" "$WORK_DIR"

echo -e "  ${GREEN}[✓]${NC} Herramientas instaladas"

# ═══════════════════════════════════════════════════════════════
# PASO 2: Montar ISO original (si existe)
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}[2/6] Preparando ISO...${NC}"

read -p "¿Tiene una ISO base de MX Linux? (ruta completa o 'n' para nueva): " ISO_PATH

if [ "$ISO_PATH" != "n" ] && [ -f "$ISO_PATH" ]; then
    echo "  Montando ISO: $ISO_PATH"
    mount -o loop "$ISO_PATH" "$ISO_MOUNT"
    
    # Copiar contenido
    rsync -a "$ISO_MOUNT/" "$WORK_DIR/"
    
    echo -e "  ${GREEN}[✓]${NC} ISO montada y copiada"
else
    echo "  ${YELLOW}[ℹ]${NC} Creando estructura desde cero..."
    mkdir -p "$WORK_DIR"/{live,etc,usr/local/bin,var/log}
fi

# ═══════════════════════════════════════════════════════════════
# PASO 3: Integrar ShieldLinux
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}[3/6] Integrando ShieldLinux en la ISO...${NC}"

# Copiar daemon
cp "$SHIELD_DIR/shield_daemon_updated.py" "$WORK_DIR/usr/local/bin/shield-linux"
chmod +x "$WORK_DIR/usr/local/bin/shield-linux"
echo -e "  ${GREEN}[✓]${NC} Daemon copiado"

# Copiar CLI
cp "$SHIELD_DIR/shield_cli.sh" "$WORK_DIR/usr/local/bin/shield-cli" 2>/dev/null || \
    cat > "$WORK_DIR/usr/local/bin/shield-cli" << 'CLIEOF'
#!/bin/bash
# ShieldLinux CLI - Versión mínima
case "${1:-status}" in
    status) systemctl status shield-linux --no-pager 2>/dev/null || pgrep -f shield-linux >/dev/null && echo "Activo" || echo "Inactivo" ;;
    start) systemctl start shield-linux 2>/dev/null || /usr/local/bin/shield-linux & ;;
    stop) systemctl stop shield-linux 2>/dev/null || pkill -f shield-linux ;;
    report) cat /var/log/shield_bans.log 2>/dev/null | tail -10 ;;
    *) echo "Uso: shield-cli {status|start|stop|report}" ;;
esac
CLIEOF
chmod +x "$WORK_DIR/usr/local/bin/shield-cli"
echo -e "  ${GREEN}[✓]${NC} CLI copiado"

# Copiar servicio systemd
mkdir -p "$WORK_DIR/etc/systemd/system"
cp "$SHIELD_DIR/shield-linux.service" "$WORK_DIR/etc/systemd/system/"
echo -e "  ${GREEN}[✓]${NC} Servicio systemd copiado"

# ═══════════════════════════════════════════════════════════════
# PASO 4: Configurar autoinicio
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}[4/6] Configurando autoinicio...${NC}"

# Crear script de init live
cat > "$WORK_DIR/usr/local/bin/shield-live-init" << 'INITEOF'
#!/bin/bash
# Autoinicio ShieldLinux Live
sleep 5
echo "y" | ufw enable 2>/dev/null || true
/usr/local/bin/shield-linux &
echo $! > /var/run/shield-linux.pid
INITEOF
chmod +x "$WORK_DIR/usr/local/bin/shield-live-init"
echo -e "  ${GREEN}[✓]${NC} Script live-init creado"

# rc.local
mkdir -p "$WORK_DIR/etc"
cat > "$WORK_DIR/etc/rc.local" << 'RCEOF'
#!/bin/bash
/usr/local/bin/shield-live-init &
exit 0
RCEOF
chmod +x "$WORK_DIR/etc/rc.local"
echo -e "  ${GREEN}[✓]${NC} rc.local configurado"

# Init script SysV
mkdir -p "$WORK_DIR/etc/init.d"
cat > "$WORK_DIR/etc/init.d/shield-linux-live" << 'INITDEOF'
#!/bin/sh
### BEGIN INIT INFO
# Provides: shield-linux-live
# Required-Start: $network ufw
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Description: ShieldLinux Live
### END INIT INFO
case "$1" in
    start) /usr/local/bin/shield-live-init & ;;
    stop) kill $(cat /var/run/shield-linux.pid 2>/dev/null) 2>/dev/null ;;
    *) echo "Uso: $0 {start|stop}" ;;
esac
exit 0
INITDEOF
chmod +x "$WORK_DIR/etc/init.d/shield-linux-live"
echo -e "  ${GREEN}[✓]${NC} Init script SysV creado"

# Crear directorio de persistencia
mkdir -p "$WORK_DIR/live/persistence/shield_linux"

# Configuración inicial vacía
cat > "$WORK_DIR/live/persistence/shield_linux/whitelist.json" << 'WLEOF'
{"ips": [], "updated": "iso_build"}
WLEOF

cat > "$WORK_DIR/live/persistence/shield_linux/blacklist.json" << 'BLEOF'
{"ips": [], "updated": "iso_build"}
BLEOF

cat > "$WORK_DIR/live/persistence/shield_linux/shield_state.json" << 'SEOF'
{"attack_counter": {}, "attack_timestamps": {}, "banned_ips": [], "temp_bans": {}, "statistics": {"total_attacks": 0, "total_bans": 0, "total_blocks": 0, "start_time": null, "last_attack": null, "top_attackers": [], "attacks_by_day": {}}}
SEOF

echo -e "  ${GREEN}[✓]${NC} Persistencia configurada"

# ═══════════════════════════════════════════════════════════════
# PASO 5: Reconstruir filesystem
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}[5/6] Reconstruyendo filesystem...${NC}"

# Comprimir con mksquashfs
if [ -d "$WORK_DIR/live" ]; then
    mksquashfs "$WORK_DIR" "$WORK_DIR/live/filesystem.squashfs" -comp xz -b 1024k -Xdict-size 1024k
    echo -e "  ${GREEN}[✓]${NC} filesystem.squashfs creado"
fi

# ═══════════════════════════════════════════════════════════════
# PASO 6: Crear ISO
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}[6/6] Creando ISO...${NC}"

ISO_NAME="MX_Linux_Shield_Live_$(date +%Y%m%d).iso"
ISO_PATH_FINAL="$ISO_OUTPUT/$ISO_NAME"

# Crear ISO booteable
genisoimage -o "$ISO_PATH_FINAL" \
    -b live/grub.img \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "SHIELD_MX_LINUX" \
    "$WORK_DIR" 2>/dev/null || \
xorriso -as mkisofs -o "$ISO_PATH_FINAL" \
    -b live/grub.img \
    -no-emul-boot \
    -boot-load-size 4 \
    -boot-info-table \
    -J -R -V "SHIELD_MX_LINUX" \
    "$WORK_DIR" 2>/dev/null || {
    echo -e "  ${YELLOW}[⚠]${NC} No se pudo crear ISO booteable (falta grub.img)"
    echo "  Creando ISO sin boot..."
    genisoimage -o "$ISO_PATH_FINAL" -J -R -V "SHIELD_MX_LINUX" "$WORK_DIR"
}

echo -e "  ${GREEN}[✓]${NC} ISO creada: $ISO_PATH_FINAL"

# ═══════════════════════════════════════════════════════════════
# LIMPIEZA
# ═══════════════════════════════════════════════════════════════

echo -e "\n${BLUE}Limpiando...${NC}"
umount "$ISO_MOUNT" 2>/dev/null || true
rm -rf "$WORK_DIR" "$ISO_MOUNT"

# ═══════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════

echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🛡️  ISO CON ShieldLinux CREADA EXITOSAMENTE           ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${CYAN}📦 ISO creada:${NC}"
echo "  $ISO_PATH_FINAL"

echo -e "\n${CYAN}📋 Tamaño:${NC}"
ls -lh "$ISO_PATH_FINAL" | awk '{print "  " $5}'

echo -e "\n${CYAN}ℹ️  Para probar la ISO:${NC}"
echo "  qemu-system-x86_64 -cdrom \"$ISO_PATH_FINAL\" -m 2048"

echo -e "\n${GREEN}[✓] ¡Proceso completado!${NC}"

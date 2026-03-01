#!/bin/bash
# 🛡️ SHIELD LINUX - Script de Desinstalación

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║  🛡️  SHIELD LINUX - DESINSTALADOR                 ║"
echo "╚════════════════════════════════════════════════════╝"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script debe ejecutarse como root"
    exit 1
fi

# Detener servicio
echo "[*] Deteniendo servicio..."
systemctl stop shield-daemon 2>/dev/null || true
systemctl disable shield-daemon 2>/dev/null || true

# Eliminar servicio systemd
echo "[*] Eliminando servicio systemd..."
rm -f /etc/systemd/system/shield-daemon.service
systemctl daemon-reload

# Eliminar módulo del kernel
echo "[*] Eliminando módulo del kernel..."
rmmod security_module 2>/dev/null || true
rm -f /lib/modules/$(uname -r)/kernel/security/security_module.ko
depmod -a

# Eliminar daemon y herramientas
echo "[*] Eliminando archivos del daemon..."
rm -f /usr/local/bin/shield_daemon.py
rm -f /usr/local/bin/shield-cli

# Eliminar configuración (opcional)
read -p "¿Eliminar configuración? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    rm -rf /etc/shield
fi

# Eliminar logs (opcional)
read -p "¿Eliminar logs? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    rm -f /var/log/shield_*.log
fi

echo "✅ Desinstalación completada"

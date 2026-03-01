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

#!/bin/bash
# 🛡️ SHIELD LINUX - Descargar módulo del kernel

MODULE_NAME="security_module"

echo "╔════════════════════════════════════════════════════╗"
echo "║  🛡️  SHIELD LINUX - DESCARGAR MÓDULO              ║"
echo "╚════════════════════════════════════════════════════╝"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script debe ejecutarse como root"
    exit 1
fi

# Verificar si está cargado
if ! lsmod | grep -q "$MODULE_NAME"; then
    echo "ℹ️  El módulo no está cargado"
    exit 0
fi

# Descargar módulo
echo "[*] Descargando módulo..."
rmmod "$MODULE_NAME"

if [ $? -eq 0 ]; then
    echo "✅ Módulo descargado exitosamente"
else
    echo "❌ Error descargando módulo"
    exit 1
fi

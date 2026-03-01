#!/bin/bash
# 🛡️ SHIELD LINUX - Cargar módulo del kernel

MODULE_NAME="security_module"
MODULE_PATH="/lib/modules/$(uname -r)/kernel/security/security_module.ko"

echo "╔════════════════════════════════════════════════════╗"
echo "║  🛡️  SHIELD LINUX - CARGAR MÓDULO                 ║"
echo "╚════════════════════════════════════════════════════╝"

if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script debe ejecutarse como root"
    exit 1
fi

# Verificar si el módulo existe
if [ ! -f "$MODULE_PATH" ]; then
    echo "❌ Módulo no encontrado en $MODULE_PATH"
    echo "[*] Primero compile el módulo con: make"
    exit 1
fi

# Verificar si ya está cargado
if lsmod | grep -q "$MODULE_NAME"; then
    echo "⚠️  El módulo ya está cargado"
    lsmod | grep "$MODULE_NAME"
    exit 0
fi

# Cargar módulo
echo "[*] Cargando módulo..."
insmod "$MODULE_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Módulo cargado exitosamente"
    echo ""
    echo "Verificando carga:"
    lsmod | grep "$MODULE_NAME"
    echo ""
    echo "Logs del kernel:"
    dmesg | tail -20 | grep -i shield
else
    echo "❌ Error cargando módulo"
    exit 1
fi

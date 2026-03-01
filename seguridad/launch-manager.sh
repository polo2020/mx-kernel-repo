#!/bin/bash
# 🛡️ ShieldLinux Manager Launcher
# Script de lanzamiento para la GUI

# Verificar si es root
if [[ $EUID -ne 0 ]]; then
    echo "⚠️ ShieldLinux Manager requiere privilegios de root"
    echo "   Ejecutando con sudo..."
    exec sudo "$0" "$@"
fi

# Verificar dependencias
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "⚠️ PySide6 no está instalado"
    echo "   Instalando..."
    pip3 install PySide6 -q
fi

# Verificar si el daemon está corriendo
if ! systemctl is-active --quiet shield-linux.service 2>/dev/null; then
    echo "ℹ️  El servicio shield-linux no está activo"
    read -p "¿Desea iniciarlo? (s/n): " response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        systemctl start shield-linux.service
    fi
fi

# Lanzar la GUI
echo "🛡️  Iniciando ShieldLinux Manager..."
exec python3 /usr/local/bin/shield-manager "$@"

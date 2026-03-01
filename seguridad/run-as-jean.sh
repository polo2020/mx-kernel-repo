#!/bin/bash
# 🛡️ ShieldLinux Manager - Launcher para usuario jean
# Ejecuta la GUI en la sesión del usuario jean

# Detectar usuario actual
CURRENT_USER=$(who | grep ':0' | head -n1 | cut -d' ' -f1)
if [ -z "$CURRENT_USER" ]; then
    CURRENT_USER="jean"
fi

echo "🛡️ Iniciando ShieldLinux Manager para usuario: $CURRENT_USER"

# Obtener UID del usuario
USER_UID=$(id -u $CURRENT_USER)

# Configurar variables de entorno para X11
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/${USER_UID}/bus

# Permitir conexiones X11
xhost +local: 2>/dev/null || true

# Ejecutar la GUI
echo "🚀 Lanzando GUI..."
sudo python3 /usr/local/bin/shield-manager

# Restaurar permisos X11
xhost -local: 2>/dev/null || true

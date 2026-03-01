#!/bin/bash
# Inyectar optimizaciones Zen en paquetes .deb del kernel
# Ejecutar DESPUÉS de compilar el kernel con repokernel.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  Inyectando optimizaciones Zen en .deb"
echo "=============================================="
echo ""

# Buscar el .deb de linux-image
IMAGE_DEB=$(ls -1 linux-image-*.deb 2>/dev/null | head -1)

if [ -z "$IMAGE_DEB" ]; then
    echo "✗ ERROR: No se encontró linux-image-*.deb en $SCRIPT_DIR"
    echo "   Primero debes compilar el kernel con repokernel.py"
    exit 1
fi

echo ">>> Paquete encontrado: $IMAGE_DEB"
echo ""

# Crear directorio temporal
TEMP_DIR=$(mktemp -d)
EXTRACT_DIR="$TEMP_DIR/extract"
CONTROL_DIR="$TEMP_DIR/control"

echo ">>> Extrayendo $IMAGE_DEB..."

# Extraer el paquete
cd "$TEMP_DIR"
ar x "$SCRIPT_DIR/$IMAGE_DEB"

# Extraer data.tar
if [ -f data.tar.xz ]; then
    tar -xf data.tar.xz -C "$EXTRACT_DIR" 2>/dev/null || mkdir -p "$EXTRACT_DIR" && tar -xf data.tar.xz -C "$EXTRACT_DIR"
elif [ -f data.tar.gz ]; then
    tar -xzf data.tar.gz -C "$EXTRACT_DIR"
elif [ -f data.tar.zst ]; then
    tar --zstd -xf data.tar.zst -C "$EXTRACT_DIR"
fi

# Extraer control.tar
mkdir -p "$CONTROL_DIR"
if [ -f control.tar.xz ]; then
    tar -xf control.tar.xz -C "$CONTROL_DIR"
elif [ -f control.tar.gz ]; then
    tar -xzf control.tar.gz -C "$CONTROL_DIR"
fi

echo ">>> Creando script postinst con optimizaciones Zen..."

# Crear script postinst
cat > "$CONTROL_DIR/postinst" << 'POSTINST'
#!/bin/bash
set -e

echo "=============================================="
echo "  Aplicando optimizaciones Zen Kernel"
echo "=============================================="

# Crear configuración sysctl
SYSCTL_FILE="/etc/sysctl.d/99-zen-kernel.conf"
cat > "$SYSCTL_FILE" << 'EOF'
# Zen Kernel Optimizations
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.dirty_ratio=10
vm.dirty_background_ratio=5
vm.dirty_expire_centisecs=1500
vm.dirty_writeback_centisecs=500
vm.watermark_boost_factor=0
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
net.ipv4.tcp_fastopen=3
net.ipv4.tcp_slow_start_after_idle=0
kernel.sched_energy_aware=0
EOF

echo "✓ Sysctl configurado: $SYSCTL_FILE"

# Aplicar sysctl
sysctl --system >/dev/null 2>&1 || true

# Configurar I/O Scheduler por defecto
SCHEDULER_FILE="/etc/udev/rules.d/60-scheduler-zen.rules"
cat > "$SCHEDULER_FILE" << 'EOF'
# Zen I/O Scheduler
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/scheduler}="kyber"
ACTION=="add|change", KERNEL=="nvme[0-9]*", ATTR{queue/scheduler}="kyber"
EOF

echo "✓ I/O Scheduler configurado: $SCHEDULER_FILE"

# Activar irqbalance
if command -v systemctl &> /dev/null; then
    systemctl enable irqbalance 2>/dev/null || true
    systemctl start irqbalance 2>/dev/null || true
    echo "✓ irqbalance activado"
fi

# Configurar CPU Governor por defecto
GOVERNOR_FILE="/etc/systemd/system/zen-cpu-governor.service"
cat > "$GOVERNOR_FILE" << 'EOF'
[Unit]
Description=Set CPU Governor to Performance
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > $gov; done'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable zen-cpu-governor 2>/dev/null || true
systemctl start zen-cpu-governor 2>/dev/null || true
echo "✓ CPU Governor configurado"

echo ""
echo "=============================================="
echo "  Optimizaciones Zen aplicadas!"
echo "=============================================="
echo ""
echo "Reinicia el sistema para aplicar todos los cambios."
echo ""

exit 0
POSTINST

chmod 755 "$CONTROL_DIR/postinst"

echo ">>> Actualizando control.tar..."
cd "$CONTROL_DIR"
tar -cf "$TEMP_DIR/control.tar" --owner=0 --group=0 .

echo ">>> Reconstruyendo $IMAGE_DEB..."
cd "$TEMP_DIR"

# Eliminar archivos viejos
rm -f control.tar.* data.tar.* debian-binary

# Crear debian-binary
echo "2.0" > debian-binary

# Reconstruir el .deb
ar rcs "$SCRIPT_DIR/$IMAGE_DEB" debian-binary control.tar data.tar.*

echo ""
echo "=============================================="
echo "  ¡PAQUETE ACTUALIZADO!"
echo "=============================================="
echo ""
echo "El paquete $IMAGE_DEB ahora incluye:"
echo "  ✓ Sysctl optimizado (swappiness=1, BBR)"
echo "  ✓ I/O Scheduler Kyber por defecto"
echo "  ✓ irqbalance activado"
echo "  ✓ CPU Governor performance"
echo ""
echo "Estas optimizaciones se aplicarán automáticamente"
echo "al instalar el paquete con: sudo apt install ./linux-image-*.deb"
echo ""

# Limpiar
rm -rf "$TEMP_DIR"

echo ">>> Regenerando Packages.gz..."
cd "$SCRIPT_DIR"
dpkg-scanpackages . /dev/null > Packages
gzip -9fk Packages

echo "✓ Packages.gz actualizado"
echo ""
echo ">>> Listo para subir a GitHub!"
echo "    git add ."
echo "    git commit -m 'Zen kernel con optimizaciones incluidas'"
echo "    git push -u origin master --force"

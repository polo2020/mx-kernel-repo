#!/bin/bash
# Zen Kernel Optimizations - Post-installation Script
# Aplicar optimizaciones de rendimiento estilo Liquorix/Zen

echo "=============================================="
echo "  Zen Kernel Optimizations - Post Install"
echo "=============================================="
echo ""

# Crear archivo de sysctl con optimizaciones
SYSCTL_FILE="/etc/sysctl.d/99-zen-optimizations.conf"

echo ">>> Creando $SYSCTL_FILE con optimizaciones..."

cat > "$SYSCTL_FILE" << 'EOF'
# ============================================
# ZEN / LIQUORIX KERNEL OPTIMIZATIONS
# ============================================

# --- Virtual Memory ---
# Priorizar responsividad sobre throughput
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.dirty_ratio=40
vm.dirty_background_ratio=10
vm.dirty_expire_centisecs=1500
vm.dirty_writeback_centisecs=500

# Transparent Huge Pages
vm.transparent_hugepage=always
vm.compact_unevictable_allowed=0

# Watermark boost (0 = sin boost, mejor latencia)
vm.watermark_boost_factor=0
vm.watermark_scale_factor=10

# --- CPU Scheduler ---
# Energy Performance Bias para rendimiento
kernel.sched_energy_aware=0

# --- Network TCP BBR ---
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr

# Buffer de red optimizados
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_adv_win_scale=-2
net.ipv4.tcp_collapse_max_bytes=6291456
net.ipv4.tcp_notsent_lowat=131072

# TCP optimizaciones
net.ipv4.tcp_fastopen=3
net.ipv4.tcp_fastopen_blackhole_timeout_sec=3600
net.ipv4.tcp_slow_start_after_idle=0
net.ipv4.tcp_mtu_probing=1
net.ipv4.tcp_max_syn_backlog=8192
net.ipv4.tcp_max_tw_buckets=2000000
net.ipv4.tcp_fin_timeout=15
net.ipv4.tcp_keepalive_time=600
net.ipv4.tcp_keepalive_probes=3
net.ipv4.tcp_keepalive_intvl=30

# IPv6 (si se usa)
net.ipv6.conf.all.disable_ipv6=0
net.ipv6.conf.default.disable_ipv6=0

# --- Filesystem ---
# Mejorar I/O de disco
vm.dirty_background_bytes=67108864
vm.dirty_bytes=536870912

# --- Kernel ---
# Maximizar rendimiento
kernel.pid_max=4194304
kernel.core_uses_pid=1
kernel.kptr_restrict=0
kernel.perf_event_paranoid=-1

# watchdog
kernel.watchdog=0
kernel.watchdog_thresh=4

# --- IRQ Balance ---
# Distribuir IRQs entre CPUs
irq.smp_affinity=1

EOF

echo ">>> Archivo creado exitosamente"
echo ""

# Aplicar sysctl
echo ">>> Aplicando configuraciones..."
sysctl --system -p "$SYSCTL_FILE" 2>/dev/null || sysctl -p "$SYSCTL_FILE"

echo ""
echo ">>> Configuraciones aplicadas"
echo ""

# Verificar TCP congestion control
echo ">>> Verificando TCP congestion control:"
sysctl net.ipv4.tcp_congestion_control
echo ""

# Verificar scheduler de I/O
echo ">>> Verificando I/O scheduler disponible:"
if [ -f /sys/block/sda/queue/scheduler ]; then
    cat /sys/block/sda/queue/scheduler 2>/dev/null || echo "No disponible para sda"
fi
if [ -f /sys/block/nvme0n1/queue/scheduler ]; then
    cat /sys/block/nvme0n1/queue/scheduler 2>/dev/null || echo "No disponible para NVMe"
fi
echo ""

# Crear script de activación BBR
BBR_SCRIPT="/etc/network/if-up.d/enable-bbr"
cat > "$BBR_SCRIPT" << 'EOF'
#!/bin/sh
# Activar BBR al levantar interfaz de red
sysctl -w net.ipv4.tcp_congestion_control=bbr 2>/dev/null || true
EOF
chmod +x "$BBR_SCRIPT"

echo "=============================================="
echo "  Optimizaciones Zen aplicadas!"
echo "=============================================="
echo ""
echo "Reinicia el sistema para aplicar todos los cambios."
echo ""
echo "Verificar después del reinicio:"
echo "  sysctl net.ipv4.tcp_congestion_control  # Debe mostrar: bbr"
echo "  cat /sys/block/sd*/queue/scheduler      # Debe mostrar: kyber"
echo ""

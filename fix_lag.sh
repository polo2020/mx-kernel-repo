#!/bin/bash
# Solución Rápida de Lag - Video + Multitarea
# Aplicar inmediatamente sin reiniciar

echo "=============================================="
echo "  APLICANDO SOLUCIONES DE LAG"
echo "=============================================="
echo ""

# 1. Cambiar I/O Scheduler a Kyber
echo ">>> 1. Cambiando I/O Scheduler a Kyber..."
for disk in /sys/block/sd* /sys/block/nvme*; do
    if [ -d "$disk/queue" ]; then
        DISK_NAME=$(basename "$disk")
        echo "kyber" > "$disk/queue/scheduler" 2>/dev/null && echo "   ✓ $DISK_NAME -> kyber"
    fi
done
echo ""

# 2. Cambiar TCP a BBR
echo ">>> 2. Cambiando TCP Congestion Control a BBR..."
sysctl -w net.ipv4.tcp_congestion_control=bbr 2>/dev/null && echo "   ✓ TCP: bbr" || echo "   ⚠ BBR no disponible"
sysctl -w net.core.default_qdisc=fq 2>/dev/null && echo "   ✓ qdisc: fq"
echo ""

# 3. Reducir Swappiness
echo ">>> 3. Reduciendo Swappiness..."
sysctl -w vm.swappiness=1 && echo "   ✓ swappiness = 1"
echo ""

# 4. Optimizar VM Dirty Pages
echo ">>> 4. Optimizando VM Dirty Pages..."
sysctl -w vm.dirty_ratio=10 && echo "   ✓ dirty_ratio = 10"
sysctl -w vm.dirty_background_ratio=5 && echo "   ✓ dirty_background_ratio = 5"
sysctl -w vm.dirty_expire_centisecs=1500 && echo "   ✓ dirty_expire = 1500"
sysctl -w vm.dirty_writeback_centisecs=500 && echo "   ✓ dirty_writeback = 500"
echo ""

# 5. Cambiar CPU Governor a Performance
echo ">>> 5. Cambiando CPU Governor a Performance..."
for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$gov" ]; then
        echo "performance" > "$gov" 2>/dev/null
    fi
done
CURRENT_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
echo "   ✓ CPU Governor: $CURRENT_GOV"
echo ""

# 6. Activar irqbalance
echo ">>> 6. Activando irqbalance..."
if command -v irqbalance &> /dev/null; then
    systemctl start irqbalance 2>/dev/null && echo "   ✓ irqbalance iniciado" || echo "   ⚠ No se pudo iniciar irqbalance"
else
    echo "   ⚠ irqbalance no instalado. Instalar con: sudo apt install irqbalance"
fi
echo ""

# 7. Desactivar Turbo Boost (reduce calor y throttling)
echo ">>> 7. Gestión de Turbo Boost..."
if [ -f /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
    echo "1" > /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null && echo "   ✓ Turbo DESACTIVADO (menos calor)" || echo "   ⚠ No se pudo desactivar Turbo"
fi
echo ""

# 8. Optimizaciones de Red adicionales
echo ">>> 8. Optimizaciones de Red..."
sysctl -w net.ipv4.tcp_fastopen=3 2>/dev/null
sysctl -w net.ipv4.tcp_slow_start_after_idle=0 2>/dev/null
sysctl -w net.ipv4.tcp_mtu_probing=1 2>/dev/null
echo "   ✓ Optimizaciones TCP aplicadas"
echo ""

# 9. Prioridad de procesos de video/usuario
echo ">>> 9. Configurando prioridades de procesos..."
# Renice procesos del usuario actual
renice -n -5 -u $(whoami) 2>/dev/null && echo "   ✓ Prioridad de usuario aumentada"
echo ""

echo "=============================================="
echo "  SOLUCIONES APLICADAS"
echo "=============================================="
echo ""
echo "Verificaciones:"
echo "  I/O Scheduler: $(cat /sys/block/sda/queue/scheduler 2>/dev/null)"
echo "  TCP Congestion: $(sysctl -n net.ipv4.tcp_congestion_control 2>/dev/null)"
echo "  Swappiness: $(sysctl -n vm.swappiness 2>/dev/null)"
echo "  CPU Governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)"
echo ""
echo "=============================================="
echo "  HACER PERMANENTES LOS CAMBIOS"
echo "=============================================="
echo ""
echo "Estos cambios se perderán al reiniciar."
echo "Para hacerlos permanentes, ejecuta:"
echo ""
echo "  sudo ./zen_optimizations.sh"
echo ""
echo "O agrega al archivo /etc/sysctl.d/99-zen-optimizations.conf"
echo ""

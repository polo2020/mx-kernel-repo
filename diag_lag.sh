#!/bin/bash
# Diagnóstico de Lag en Video + Multitarea
# Ejecutar como root o con sudo

echo "=============================================="
echo "  DIAGNÓSTICO DE LAG - VIDEO + MULTITAREA"
echo "=============================================="
echo ""

# 1. Verificar Scheduler de I/O actual
echo "1. I/O SCHEDULER ACTUAL:"
for disk in /sys/block/sd* /sys/block/nvme*; do
    if [ -d "$disk" ]; then
        DISK_NAME=$(basename "$disk")
        SCHED=$(cat "$disk/queue/scheduler" 2>/dev/null)
        echo "   $DISK_NAME: $SCHED"
    fi
done 2>/dev/null
echo ""

# 2. Verificar TCP Congestion Control
echo "2. TCP CONGESTION CONTROL:"
sysctl net.ipv4.tcp_congestion_control 2>/dev/null | sed 's/^/   /'
echo ""

# 3. Verificar Swappiness
echo "3. MEMORIA (SWAPPINESS):"
sysctl vm.swappiness 2>/dev/null | sed 's/^/   /'
echo ""

# 4. Verificar Frecuencia de CPU
echo "4. CPU FREQUENCY GOVERNOR:"
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$cpu" ]; then
        GOV=$(cat "$cpu" 2>/dev/null)
        CPU_ID=$(echo "$cpu" | cut -d'/' -f6)
        echo "   $CPU_ID: $GOV"
    fi
done 2>/dev/null
echo ""

# 5. Verificar IRQ Balance
echo "5. IRQ BALANCE:"
if pgrep -x irqbalance >/dev/null 2>&1; then
    echo "   ✓ irqbalance está corriendo"
else
    echo "   ✗ irqbalance NO está corriendo"
fi
echo ""

# 6. Verificar procesos consumiendo I/O
echo "6. TOP 5 PROCESOS POR I/O (si iotop está disponible):"
if command -v iotop &> /dev/null; then
    iotop -b -n 1 -o 2>/dev/null | head -10 | sed 's/^/   /'
else
    echo "   iotop no instalado. Instalar con: sudo apt install iotop"
fi
echo ""

# 7. Verificar uso de GPU
echo "7. GPU / DRIVERS DE VIDEO:"
if command -v lspci &> /dev/null; then
    echo "   Controladores de video detectados:"
    lspci -k | grep -A 2 -E "(VGA|3D)" | sed 's/^/   /'
fi
echo ""

# 8. Verificar si hay throttling
echo "8. CPU THERMAL / THROTTLING:"
if [ -f /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
    TURBO=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null)
    echo "   Intel P-State Turbo: $([ "$TURBO" = "1" ] && echo "DESACTIVADO" || echo "ACTIVADO")"
fi
if [ -d /sys/class/thermal ]; then
    echo "   Temperaturas:"
    for zone in /sys/class/thermal/thermal_zone*; do
        if [ -f "$zone/temp" ]; then
            TYPE=$(cat "$zone/type" 2>/dev/null)
            TEMP=$(cat "$zone/temp" 2>/dev/null)
            TEMP_C=$((TEMP / 1000))
            echo "      $TYPE: ${TEMP_C}°C"
        fi
    done | sed 's/^/   /'
fi
echo ""

# 9. Verificar VM Dirty Pages (causa común de lag)
echo "9. VM DIRTY PAGES (causa común de stuttering):"
sysctl vm.dirty_ratio 2>/dev/null | sed 's/^/   /'
sysctl vm.dirty_background_ratio 2>/dev/null | sed 's/^/   /'
sysctl vm.dirty_expire_centisecs 2>/dev/null | sed 's/^/   /'
echo ""

# 10. Verificar si hay procesos en D state (I/O wait)
echo "10. PROCESOS EN I/O WAIT (estado D):"
ps aux | awk '$8 ~ /D/ {print "   " $0}' | head -5
if [ $(ps aux | awk '$8 ~ /D/' | wc -l) -eq 0 ]; then
    echo "   No hay procesos en I/O wait actualmente"
fi
echo ""

# RECOMENDACIONES
echo "=============================================="
echo "  RECOMENDACIONES PARA ELIMINAR LAG"
echo "=============================================="
echo ""

PROBLEMAS=0

# Verificar scheduler
CURRENT_SCHED=$(cat /sys/block/sda/queue/scheduler 2>/dev/null | grep -o '\[.*\]' | tr -d '[]')
if [ "$CURRENT_SCHED" != "kyber" ] && [ "$CURRENT_SCHED" != "bfq" ]; then
    echo "⚠️  CAMBIAR I/O SCHEDULER A KYBER/BFQ:"
    echo "    echo kyber | sudo tee /sys/block/sda/queue/scheduler"
    echo "    echo kyber | sudo tee /sys/block/nvme0n1/queue/scheduler"
    PROBLEMAS=$((PROBLEMAS+1))
fi

# Verificar swappiness
SWAP=$(sysctl -n vm.swappiness 2>/dev/null)
if [ "$SWAP" -gt 10 ]; then
    echo "⚠️  REDUCIR SWAPPINESS (causa lag al tener poca RAM):"
    echo "    sudo sysctl vm.swappiness=1"
    PROBLEMAS=$((PROBLEMAS+1))
fi

# Verificar dirty ratio
DIRTY=$(sysctl -n vm.dirty_ratio 2>/dev/null)
if [ "$DIRTY" -gt 20 ]; then
    echo "⚠️  REDUCIR DIRTY RATIO (evita stuttering de disco):"
    echo "    sudo sysctl vm.dirty_ratio=10"
    echo "    sudo sysctl vm.dirty_background_ratio=5"
    PROBLEMAS=$((PROBLEMAS+1))
fi

# Verificar governor de CPU
GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)
if [ "$GOV" = "powersave" ]; then
    echo "⚠️  CAMBIAR CPU GOVERNOR A PERFORMANCE:"
    echo "    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
    PROBLEMAS=$((PROBLEMAS+1))
fi

if [ $PROBLEMAS -eq 0 ]; then
    echo "✓ No se detectaron problemas obvios de configuración"
    echo ""
    echo "Posibles causas del lag:"
    echo "  1. Drivers de video propietarios faltantes"
    echo "  2. Hardware insuficiente para la resolución del video"
    echo "  3. Navegador usando aceleración por software"
    echo ""
    echo "Soluciones adicionales:"
    echo "  - Instalar drivers propietarios de GPU"
    echo "  - Usar VA-API para aceleración de video por hardware"
    echo "  - Limitar procesos en segundo plano del navegador"
fi

echo ""
echo "=============================================="
echo "  APLICAR SOLUCIONES ZEN AUTOMÁTICAS"
echo "=============================================="
echo ""
echo "Para aplicar todas las optimizaciones Zen automáticamente:"
echo "  sudo ./zen_optimizations.sh"
echo ""
echo "Luego reinicia: sudo reboot"
echo ""

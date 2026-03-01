#!/bin/bash
# 🛡️ SHIELD LINUX - Comparador de Versiones
# Muestra diferencias entre módulo kernel y userspace

echo "╔════════════════════════════════════════════════════╗"
echo "║  🛡️  SHIELD LINUX - COMPARADOR DE VERSIONES       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  CARACTERÍSTICA           │  KERNEL  │  USERSPACE │  eBPF  │"
echo "├──────────────────────────────────────────────────────────────┤"
echo "│  Velocidad de respuesta   │  1-10μs  │   100-500ms │  1-5μs │"
echo "│  Kernel panic riesgo      │   ❌ Sí   │    ✅ No    │  ✅ No │"
echo "│  Memory leak riesgo       │   ❌ Sí   │    ✅ No    │  ✅ No │"
echo "│  Debugging                │  Difícil │   Fácil     │ Medio  │"
echo "│  Recompilar necesario     │   ❌ Sí   │    ✅ No    │  ✅ No │"
echo "│  Configuración dinámica   │   ❌ No   │    ✅ Sí    │  ✅ Sí │"
echo "│  Estabilidad              │   Media  │   Excelente │  Alta  │"
echo "│  Rendimiento              │ Excelente│    Bueno    │Excelente│"
echo "│  Consumo RAM              │  5-10 MB │   50-100 MB │ 10-20MB│"
echo "│  Consumo CPU              │  0.1-1%  │    3-5%     │ 0.5-2% │"
echo "└──────────────────────────────────────────────────────────────┘"
echo ""

echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  VERSIÓN KERNEL MODULE (.ko)                                │"
echo "├─────────────────────────────────────────────────────────────┤"
echo "│  ✅ Ventajas:                                               │"
echo "│     • Máximo rendimiento (1-10μs)                          │"
echo "│     • Integrado en el kernel                               │"
echo "│     • Contramedidas más rápidas                            │"
echo "│                                                             │"
echo "│  ❌ Desventajas:                                            │"
echo "│     • Riesgo de kernel panic                               │"
echo "│     • Memory leaks afectan todo el sistema                 │"
echo "│     • Difícil debugging (dmesg, crash dumps)               │"
echo "│     • Requiere recompilar para cambios                     │"
echo "│     • Inestable si hay bugs                                │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  VERSIÓN USERSPACE (Python)                                 │"
echo "├─────────────────────────────────────────────────────────────┤"
echo "│  ✅ Ventajas:                                               │"
echo "│     • SIN riesgo de kernel panic                           │"
echo "│     • Memory leaks solo afectan al daemon                  │"
echo "│     • Fácil debugging (logs, pdb, gdb)                     │"
echo "│     • SIN recompilar (config dinámica)                     │"
echo "│     • Muy estable                                          │"
echo "│     • Fácil de actualizar                                  │"
echo "│                                                             │"
echo "│  ❌ Desventajas:                                            │"
echo "│     • Más lento (100-500ms vs 1-10μs)                      │"
echo "│     • Más consumo de RAM (50-100MB)                        │"
echo "│     • Más consumo de CPU (3-5%)                            │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  VERSIÓN eBPF/XDP (Híbrida) - RECOMENDADA                   │"
echo "├─────────────────────────────────────────────────────────────┤"
echo "│  ✅ Ventajas:                                               │"
echo "│     • Rendimiento casi-igual al kernel (1-5μs)             │"
echo "│     • SIN riesgo de kernel panic (verificado)              │"
echo "│     • Carga dinámica (sin recompilar)                      │"
echo "│     • Memory leaks contenidos                              │"
echo "│     • Debugging medio (bpftool, trace_pipe)                │"
echo "│                                                             │"
echo "│  ❌ Desventajas:                                            │"
echo "│     • Requiere kernel 4.8+                                 │"
echo "│     • Más complejo de implementar                          │"
echo "│     • Limitado por verifier de eBPF                        │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

echo "╔════════════════════════════════════════════════════╗"
echo "║  RECOMENDACIÓN                                     ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║  Producción crítica:  eBPF/XDP (mejor balance)    ║"
echo "║  Desarrollo/pruebas:  Userspace (más fácil)       ║"
echo "║  Máximo rendimiento:  Kernel module (con riesgo)  ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Preguntar cuál instalar
echo "Selecciona la versión a instalar:"
echo "  1) Userspace (SIN riesgos, recomendado para la mayoría)"
echo "  2) Kernel module (máximo rendimiento, con riesgos)"
echo "  3) eBPF/XDP (híbrido, recomendado para producción)"
echo "  4) Salir"
echo ""
read -p "Opción [1-4]: " opcion

case $opcion in
    1)
        echo ""
        echo "Instalando versión USERSPACE..."
        echo "✅ SIN módulo kernel"
        echo "✅ SIN riesgo de kernel panic"
        echo "✅ Fácil debugging"
        echo ""
        cp /home/jean/Música/modulo_seguridad/userspace_daemon/shield_daemon_userspace.py /usr/local/bin/shield-daemon
        chmod +x /usr/local/bin/shield-daemon
        echo "✅ Daemon userspace instalado en /usr/local/bin/shield-daemon"
        ;;
    2)
        echo ""
        echo "Instalando versión KERNEL MODULE..."
        echo "⚠️  CON riesgo de kernel panic"
        echo "⚠️  Requiere compilación"
        echo ""
        cd /home/jean/Música/modulo_seguridad/kernel_module
        make
        make install
        echo "✅ Módulo kernel instalado"
        ;;
    3)
        echo ""
        echo "Instalando versión eBPF/XDP..."
        echo "✅ Mejor balance rendimiento/seguridad"
        echo "⚠️  Requiere kernel 4.8+"
        echo ""
        
        # Verificar kernel
        KERNEL_VERSION=$(uname -r)
        KERNEL_MAJOR=$(echo $KERNEL_VERSION | cut -d. -f1)
        KERNEL_MINOR=$(echo $KERNEL_VERSION | cut -d. -f2)
        
        if [ $KERNEL_MAJOR -gt 4 ] || ([ $KERNEL_MAJOR -eq 4 ] && [ $KERNEL_MINOR -ge 8 ]); then
            echo "✅ Kernel compatible: $KERNEL_VERSION"
            # Instalar herramientas eBPF
            apt-get install -y bpfcc-tools libbpfcc
            echo "✅ Herramientas eBPF instaladas"
            echo "⚠️  Programa eBPF requiere compilación adicional"
        else
            echo "❌ Kernel no compatible: $KERNEL_VERSION (requiere 4.8+)"
            echo "Usando fallback a userspace..."
            cp /home/jean/Música/modulo_seguridad/userspace_daemon/shield_daemon_userspace.py /usr/local/bin/shield-daemon
        fi
        ;;
    4)
        echo "Saliendo..."
        exit 0
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  Instalación completada                           ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║  Para iniciar:                                     ║"
echo "║  sudo systemctl start shield-daemon               ║"
echo "║  sudo systemctl enable shield-daemon              ║"
echo "║                                                    ║"
echo "║  Para verificar:                                   ║"
echo "║  shield-cli status                                ║"
echo "╚════════════════════════════════════════════════════╝"

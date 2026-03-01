#!/bin/bash
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     🛡️ SHIELD LINUX v6.0 ULTRA - MONITOR EN VIVO       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
while true; do
    clear
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║     🛡️ SHIELD LINUX v6.0 ULTRA - MONITOR EN VIVO       ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 DETECCIONES DE HOY (desde $(date +%H:%M)):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "   🔴 SPAMHAUS:  $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'SPAMHAUS') redes bloqueadas"
    echo "   📋 MITRE:     $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'MITRE') técnicas detectadas"
    echo "   🦠 YARA:      $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'YARA') malware detectado"
    echo "   🍯 HONEYPOT:  $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'HONEYPOT') IPs cayeron en trampa"
    echo "   ⚠️  CASCADE:   $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'CASCADE') subnets baneadas"
    echo "   🔗 CORRELATION: $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'CORRELATION') ataques coordinados"
    echo "   🌐 ABUSEIPDB: $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'ABUSEIPDB') consultas
   🔄 API ROTATION: $(sudo journalctl -u shield-linux --since '00:00' | grep -c 'Rotación de API') rotaciones"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔴 ÚLTIMOS 5 BANS EN TIEMPO REAL:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    sudo journalctl -u shield-linux -n 20 --no-pager | grep "BAN:" | tail -5
    echo ""
    echo "Presiona Ctrl+C para salir"
    sleep 5
done

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ SHIELD LINUX - CLI Tool
Herramienta de línea de comandos para gestión del módulo
"""

import sys
import os
import subprocess
import json
import argparse
from datetime import datetime

CONFIG_DIR = "/etc/shield"
STATE_FILE = f"{CONFIG_DIR}/shield_state.json"
BANS_LOG = "/var/log/shield_bans.log"
DAEMON_LOG = "/var/log/shield_daemon.log"
MODULE_NAME = "security_module"

def check_root():
    """Verificar permisos de root"""
    if os.geteuid() != 0:
        print("❌ Este comando requiere permisos de root")
        sys.exit(1)

def cmd_status(args):
    """Ver estado del módulo y daemon"""
    print("╔════════════════════════════════════════════════════╗")
    print("║  🛡️  SHIELD LINUX - ESTADO                         ║")
    print("╚════════════════════════════════════════════════════╝")
    
    # Estado del módulo kernel
    result = subprocess.run(["lsmod", "|", "grep", MODULE_NAME], shell=True, capture_output=True)
    if result.returncode == 0:
        print("✅ Módulo Kernel: CARGADO")
    else:
        print("❌ Módulo Kernel: NO CARGADO")
    
    # Estado del daemon
    result = subprocess.run(["pgrep", "-f", "shield_daemon.py"], capture_output=True)
    if result.returncode == 0:
        print("✅ Daemon: EJECUTÁNDOSE")
    else:
        print("❌ Daemon: DETENIDO")
    
    # Estado de UFW
    result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
    if "active" in result.stdout.lower():
        print("✅ UFW: ACTIVO")
    else:
        print("⚠️  UFW: INACTIVO")

def cmd_start(args):
    """Iniciar daemon"""
    check_root()
    print("Iniciando ShieldLinux daemon...")
    
    daemon_path = "/usr/local/bin/shield_daemon.py"
    if not os.path.exists(daemon_path):
        daemon_path = os.path.join(os.path.dirname(__file__), "shield_daemon.py")
    
    subprocess.Popen([sys.executable, daemon_path], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    start_new_session=True)
    print("✅ Daemon iniciado")

def cmd_stop(args):
    """Detener daemon"""
    check_root()
    print("Deteniendo ShieldLinux daemon...")
    subprocess.run(["pkill", "-f", "shield_daemon.py"])
    print("✅ Daemon detenido")

def cmd_restart(args):
    """Reiniciar daemon"""
    cmd_stop(args)
    import time
    time.sleep(2)
    cmd_start(args)

def cmd_report(args):
    """Generar reporte de seguridad"""
    print("╔════════════════════════════════════════════════════╗")
    print("║  🛡️  SHIELD LINUX - REPORTE DE SEGURIDAD          ║")
    print("╚════════════════════════════════════════════════════╝")
    
    # Leer estado
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        stats = state.get('stats', {})
        print(f"📊 Inicio:            {stats.get('start_time', 'N/A')}")
        print(f"📦 Paquetes:          {stats.get('packets_inspected', 0):,}")
        print(f"⚔️  Ataques:          {stats.get('attacks_detected', 0):,}")
        print(f"🛡️  Contramedidas:    {stats.get('countermeasures_triggered', 0):,}")
        print(f"🚫 IPs Bloqueadas:    {len(stats.get('ips_blocked', set()))}")
    except FileNotFoundError:
        print("No hay estado disponible")
    
    # Leer bans log
    try:
        with open(BANS_LOG, 'r') as f:
            lines = f.readlines()[-10:]
            if lines:
                print("\n📋 Últimos baneos:")
                for line in lines:
                    print(f"   {line.strip()}")
    except FileNotFoundError:
        pass

def cmd_bans(args):
    """Ver lista de baneos"""
    print("╔════════════════════════════════════════════════════╗")
    print("║  🚫 BANEOS REGISTRADOS                             ║")
    print("╚════════════════════════════════════════════════════╝")
    
    try:
        with open(BANS_LOG, 'r') as f:
            for line in f.readlines()[-50:]:
                print(line.strip())
    except FileNotFoundError:
        print("No hay baneos registrados")

def cmd_stats(args):
    """Ver estadísticas en tiempo real"""
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        stats = state.get('stats', {})
        cm_stats = state.get('countermeasure_stats', {})
        
        print("╔════════════════════════════════════════════════════╗")
        print("║  📊 ESTADÍSTICAS EN TIEMPO REAL                   ║")
        print("╠════════════════════════════════════════════════════╣")
        print(f"║  Paquetes inspeccionados:  {stats.get('packets_inspected', 0):>15,} ║")
        print(f"║  Ataques detectados:       {stats.get('attacks_detected', 0):>15,} ║")
        print(f"║  Contramedidas activas:    {stats.get('countermeasures_triggered', 0):>15,} ║")
        print(f"║  IPs bloqueadas:           {len(stats.get('ips_blocked', set())):>15} ║")
        print("╠════════════════════════════════════════════════════╣")
        print(f"║  TCP Resets:               {cm_stats.get('tcp_resets', 0):>15,} ║")
        print(f"║  Rate Limits:              {cm_stats.get('rate_limits', 0):>15,} ║")
        print(f"║  Firewall Rules:           {cm_stats.get('firewall_rules', 0):>15,} ║")
        print(f"║  Blackhole Drops:          {cm_stats.get('blackhole_drops', 0):>15,} ║")
        print("╚════════════════════════════════════════════════════╝")
    except FileNotFoundError:
        print("No hay estadísticas disponibles")

def cmd_countermeasures(args):
    """Listar contramedidas disponibles"""
    print("╔════════════════════════════════════════════════════╗")
    print("║  🛡️  CONTRAMEDIDAS DISPONIBLES                     ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║  1. TCP Reset Injection                            ║")
    print("║  2. SYN Cookie Advanced                            ║")
    print("║  3. Connection Kill Switch                         ║")
    print("║  4. Rate Limit Escalation                          ║")
    print("║  5. Honeypot Redirect                              ║")
    print("║  6. Packet Blackhole                               ║")
    print("║  7. ICMP Unreachable                               ║")
    print("║  8. Dynamic Firewall Rules                         ║")
    print("╚════════════════════════════════════════════════════╝")

def cmd_config(args):
    """Gestionar configuración"""
    config_file = f"{CONFIG_DIR}/config.json"
    
    if args.action == "get":
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if args.key and args.key in config:
                    print(f"{args.key}: {config[args.key]}")
                else:
                    for k, v in config.items():
                        print(f"{k}: {v}")
        except FileNotFoundError:
            print("Configuración no encontrada")
    
    elif args.action == "set":
        check_root()
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Convertir valor
            try:
                value = int(args.value)
            except ValueError:
                try:
                    value = float(args.value)
                except ValueError:
                    if args.value.lower() == 'true':
                        value = True
                    elif args.value.lower() == 'false':
                        value = False
                    else:
                        value = args.value
            
            config[args.key] = value
            
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ {args.key} = {value}")
        except Exception as e:
            print(f"❌ Error: {e}")

def cmd_logs(args):
    """Ver logs"""
    log_file = DAEMON_LOG
    
    if args.forensics:
        log_file = "/var/log/shield_forensics.log"
    elif args.bans:
        log_file = BANS_LOG
    
    try:
        lines = args.lines if args.lines else 50
        subprocess.run(["tail", "-n", str(lines), log_file])
    except FileNotFoundError:
        print(f"Log {log_file} no encontrado")

def main():
    parser = argparse.ArgumentParser(
        description="🛡️ ShieldLinux CLI - Gestión del módulo de seguridad"
    )
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # status
    subparsers.add_parser('status', help='Ver estado del módulo')
    
    # start
    subparsers.add_parser('start', help='Iniciar daemon')
    
    # stop
    subparsers.add_parser('stop', help='Detener daemon')
    
    # restart
    subparsers.add_parser('restart', help='Reiniciar daemon')
    
    # report
    subparsers.add_parser('report', help='Generar reporte')
    
    # bans
    subparsers.add_parser('bans', help='Ver baneos')
    
    # stats
    subparsers.add_parser('stats', help='Ver estadísticas')
    
    # countermeasures
    subparsers.add_parser('countermeasures', help='Listar contramedidas')
    
    # config
    config_parser = subparsers.add_parser('config', help='Gestionar configuración')
    config_parser.add_argument('action', choices=['get', 'set'])
    config_parser.add_argument('key', nargs='?')
    config_parser.add_argument('value', nargs='?')
    
    # logs
    logs_parser = subparsers.add_parser('logs', help='Ver logs')
    logs_parser.add_argument('-n', '--lines', type=int, default=50)
    logs_parser.add_argument('--forensics', action='store_true')
    logs_parser.add_argument('--bans', action='store_true')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        cmd_status(args)
    elif args.command == 'start':
        cmd_start(args)
    elif args.command == 'stop':
        cmd_stop(args)
    elif args.command == 'restart':
        cmd_restart(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'bans':
        cmd_bans(args)
    elif args.command == 'stats':
        cmd_stats(args)
    elif args.command == 'countermeasures':
        cmd_countermeasures(args)
    elif args.command == 'config':
        cmd_config(args)
    elif args.command == 'logs':
        cmd_logs(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

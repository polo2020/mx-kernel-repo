#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ SHIELD MANAGER v2.0 - Interfaz Gráfica para ShieldLinux
Sincronizado con shield_daemon_updated.py
"""

import sys
import os
import subprocess
import re
import json
import socket
import tempfile
from datetime import datetime
from collections import Counter
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QMessageBox,
    QProgressBar, QSplitter, QTabWidget, QFrame, QScrollArea,
    QSystemTrayIcon, QMenu, QStatusBar, QToolBar, QDialog
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QIcon, QPalette, QBrush, QPixmap, QLinearGradient, QAction

# ==================== CONFIGURACIÓN ====================
CONFIG_DIR = "/etc/shield_linux"
STATE_FILE = f"{CONFIG_DIR}/shield_state.json"
WHITELIST_FILE = f"{CONFIG_DIR}/whitelist.json"
BLACKLIST_FILE = f"{CONFIG_DIR}/blacklist.json"
STATS_FILE = f"{CONFIG_DIR}/statistics.json"
LOG_PATH = "/var/log/ufw.log"
BAN_LOG_PATH = "/var/log/shield_bans.log"
THEME_FILE = os.path.join(os.path.dirname(__file__), "tema.jpg")

# ==================== HILO DE COMUNICACIÓN CON DAEMON ====================
class DaemonCommunicator(QThread):
    """Comunicación asíncrona con el daemon"""
    data_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            try:
                # Leer estado del daemon
                state = self.read_state_file()
                if state:
                    self.data_received.emit(state)
            except Exception as e:
                self.error_occurred.emit(str(e))
            self.msleep(2000)  # Actualizar cada 2 segundos

    def read_state_file(self) -> dict:
        """Lee el archivo de estado del daemon"""
        try:
            if os.path.exists(STATE_FILE):
                # Copiar con sudo si es necesario
                if os.geteuid() != 0:
                    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                        temp_path = tmp.name
                    subprocess.run(['sudo', 'cp', STATE_FILE, temp_path],
                                 capture_output=True)
                    with open(temp_path, 'r') as f:
                        data = json.load(f)
                    os.unlink(temp_path)
                    return data
                else:
                    with open(STATE_FILE, 'r') as f:
                        return json.load(f)
        except Exception as e:
            print(f"Error leyendo estado: {e}")
        return {}

    def stop(self):
        self.running = False


# ==================== HILO DE MONITOREO DE LOGS ====================
class LogMonitorThread(QThread):
    """Monitoreo en tiempo real de logs de UFW"""
    log_detected = Signal(dict)

    def __init__(self, log_path=LOG_PATH):
        super().__init__()
        self.log_path = log_path
        self.running = True
        self.position = 0

    def run(self):
        while self.running:
            try:
                if not os.path.exists(self.log_path):
                    self.msleep(5000)
                    continue

                # Leer log con sudo
                with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                    temp_path = tmp.name

                subprocess.run(['sudo', 'cp', self.log_path, temp_path],
                             capture_output=True, check=True)

                with open(temp_path, 'r') as f:
                    f.seek(self.position)
                    for line in f:
                        if "[UFW BLOCK]" in line:
                            match = re.search(r"SRC=([\d\.]+).*DPT=(\d+)", line)
                            if match:
                                self.log_detected.emit({
                                    'ip': match.group(1),
                                    'port': match.group(2),
                                    'line': line.strip(),
                                    'timestamp': datetime.now().isoformat()
                                })
                    self.position = f.tell()

                os.unlink(temp_path)
                self.msleep(1000)

            except Exception as e:
                print(f"Error monitoreando logs: {e}")
                self.msleep(5000)

    def stop(self):
        self.running = False


# ==================== VENTANA DE ESTADÍSTICAS ====================
class StatsDialog(QDialog):
    """Ventana emergente de estadísticas detalladas"""

    def __init__(self, stats_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📊 Estadísticas Detalladas")
        self.setMinimumSize(600, 500)
        self.setup_ui(stats_data)

    def setup_ui(self, stats):
        layout = QVBoxLayout(self)

        # Título
        title = QLabel("🛡️ Estadísticas de Seguridad")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff88;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Stats grid
        grid = QGroupBox()
        grid_layout = QFormLayout(grid)

        total_attacks = stats.get('total_attacks', 0)
        total_bans = stats.get('total_bans', 0)
        start_time = stats.get('start_time', 'N/A')
        last_attack = stats.get('last_attack', 'N/A')

        grid_layout.addRow("Total de Ataques:", QLabel(f"{total_attacks:,}"))
        grid_layout.addRow("Total de Bans:", QLabel(f"{total_bans:,}"))
        grid_layout.addRow("Desde:", QLabel(start_time))
        grid_layout.addRow("Último Ataque:", QLabel(last_attack or "N/A"))

        layout.addWidget(grid)

        # Top atacantes
        top_group = QGroupBox("Top 10 Atacantes")
        top_layout = QVBoxLayout(top_group)

        top_attackers = stats.get('top_attackers', [])
        table = QTableWidget(len(top_attackers), 3)
        table.setHorizontalHeaderLabels(["#", "IP", "Ataques"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, (ip, count) in enumerate(top_attackers[:10]):
            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            table.setItem(i, 1, QTableWidgetItem(ip))
            table.setItem(i, 2, QTableWidgetItem(str(count)))

        top_layout.addWidget(table)
        layout.addWidget(top_group)

        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)


# ==================== CLASE PRINCIPAL ====================
class ShieldManager(QMainWindow):
    """Interfaz principal de ShieldLinux Manager"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ ShieldLinux Manager v2.0")
        self.setMinimumSize(1400, 900)

        # Estado
        self.current_state = {}
        self.banned_ips = set()
        self.whitelist = set()
        self.blacklist = set()

        # Configurar UI
        self.setup_ui()
        self.setup_theme()

        # Iniciar monitores
        self.daemon_comm = DaemonCommunicator()
        self.daemon_comm.data_received.connect(self.update_from_daemon)
        self.daemon_comm.error_occurred.connect(self.show_error)
        self.daemon_comm.start()

        self.log_monitor = LogMonitorThread()
        self.log_monitor.log_detected.connect(self.on_log_detected)
        self.log_monitor.start()

        # Timer de refresco
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(3000)

        # Refresco inicial
        self.refresh_all()

    def setup_ui(self):
        """Configurar interfaz de usuario"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.create_header(main_layout)

        # Panel de estado
        self.create_status_panel(main_layout)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        tabs.addTab(self.create_logs_tab(), "📋 Logs")
        tabs.addTab(self.create_settings_tab(), "⚙️ Configuración")
        main_layout.addWidget(tabs, 1)

        # Status bar
        self.statusBar().showMessage("Conectado al daemon")

    def create_header(self, layout):
        """Crear header con logo y título"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)

        # Logo/Icono
        logo_label = QLabel("🛡️")
        logo_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(logo_label)

        # Título
        title_layout = QVBoxLayout()
        title = QLabel("SHIELD LINUX")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ff88;")
        subtitle = QLabel("Sistema de Defensa Automática con IA")
        subtitle.setStyleSheet("font-size: 14px; color: #888;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addWidget(header_frame)

    def create_status_panel(self, layout):
        """Crear panel de estado rápido"""
        status_frame = QFrame()
        status_frame.setObjectName("statusPanel")
        status_layout = QHBoxLayout(status_frame)

        # Estado del servicio
        self.service_status = QLabel("🔴 DESCONOCIDO")
        self.service_status.setObjectName("serviceStatus")
        status_layout.addWidget(self.service_status)

        # Contadores
        self.attacks_label = QLabel("⚔️ Ataques: 0")
        self.attacks_label.setObjectName("counterLabel")
        status_layout.addWidget(self.attacks_label)

        self.bans_label = QLabel("🚫 Baneos: 0")
        self.bans_label.setObjectName("counterLabel")
        status_layout.addWidget(self.bans_label)

        self.ips_label = QLabel("🎯 IPs Activas: 0")
        self.ips_label.setObjectName("counterLabel")
        status_layout.addWidget(self.ips_label)

        status_layout.addStretch()

        # Botones de acción
        self.btn_start = QPushButton("▶️ Iniciar")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.start_service)

        self.btn_stop = QPushButton("⏹️ Detener")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.clicked.connect(self.stop_service)

        self.btn_restart = QPushButton("🔄 Reiniciar")
        self.btn_restart.setObjectName("btnRestart")
        self.btn_restart.clicked.connect(self.restart_service)

        status_layout.addWidget(self.btn_start)
        status_layout.addWidget(self.btn_stop)
        status_layout.addWidget(self.btn_restart)

        layout.addWidget(status_frame)

    def create_dashboard_tab(self):
        """Crear pestaña de dashboard"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        splitter = QSplitter(Qt.Horizontal)

        # Panel izquierdo - Estadísticas
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Stats cards
        stats_layout = QHBoxLayout()
        self.card_attacks = self.create_stat_card("Total Ataques", "0", "#e74c3c")
        self.card_bans = self.create_stat_card("Total Baneos", "0", "#9b59b6")
        self.card_active = self.create_stat_card("IPs Baneadas", "0", "#f39c12")
        stats_layout.addWidget(self.card_attacks)
        stats_layout.addWidget(self.card_bans)
        stats_layout.addWidget(self.card_active)
        left_layout.addLayout(stats_layout)

        # Gráfico de ataques por día (tabla)
        attacks_group = QGroupBox("📈 Ataques por Día")
        attacks_layout = QVBoxLayout(attacks_group)
        self.attacks_by_day_table = QTableWidget(0, 2)
        self.attacks_by_day_table.setHorizontalHeaderLabels(["Día", "Ataques"])
        self.attacks_by_day_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        attacks_layout.addWidget(self.attacks_by_day_table)
        left_layout.addWidget(attacks_group)

        splitter.addWidget(left_panel)

        # Panel derecho - Top atacantes
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        top_group = QGroupBox("🎯 Top 10 Atacantes")
        top_layout = QVBoxLayout(top_group)
        self.top_attackers_table = QTableWidget(0, 3)
        self.top_attackers_table.setHorizontalHeaderLabels(["#", "IP", "Intentos"])
        self.top_attackers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        top_layout.addWidget(self.top_attackers_table)
        right_layout.addWidget(top_group)

        # Acciones rápidas
        actions_group = QGroupBox("⚡ Acciones Rápidas")
        actions_layout = QVBoxLayout(actions_group)

        self.manual_ip_input = QLineEdit()
        self.manual_ip_input.setPlaceholderText("Ingrese IP para banear...")
        actions_layout.addWidget(self.manual_ip_input)

        ban_btn = QPushButton("🚫 Banear IP")
        ban_btn.setObjectName("btnBan")
        ban_btn.clicked.connect(self.manual_ban)
        actions_layout.addWidget(ban_btn)

        unban_btn = QPushButton("✅ Unbanear IP")
        unban_btn.setObjectName("btnUnban")
        unban_btn.clicked.connect(self.manual_unban)
        actions_layout.addWidget(unban_btn)

        stats_btn = QPushButton("📊 Ver Estadísticas Completas")
        stats_btn.clicked.connect(self.show_full_stats)
        actions_layout.addWidget(stats_btn)

        right_layout.addWidget(actions_group)
        splitter.addWidget(right_panel)

        layout.addWidget(splitter)
        return tab

    def create_stat_card(self, title, value, color):
        """Crear tarjeta de estadística"""
        card = QFrame()
        card.setObjectName("statCard")
        layout = QVBoxLayout(card)

        label_title = QLabel(title)
        label_title.setStyleSheet(f"color: {color}; font-size: 14px;")
        layout.addWidget(label_title)

        label_value = QLabel(value)
        label_value.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        layout.addWidget(label_value)

        return card

    def create_logs_tab(self):
        """Crear pestaña de logs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Toolbar de logs
        log_toolbar = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.refresh_logs)
        log_toolbar.addWidget(refresh_btn)

        clear_btn = QPushButton("🗑️ Limpiar Vista")
        clear_btn.clicked.connect(lambda: self.logs_table.setRowCount(0))
        log_toolbar.addWidget(clear_btn)

        log_toolbar.addStretch()
        layout.addLayout(log_toolbar)

        # Tabla de logs
        self.logs_table = QTableWidget(0, 5)
        self.logs_table.setHorizontalHeaderLabels(["Fecha", "Hora", "IP", "Puerto", "Acción"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a2e;
                color: #eee;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #16213e;
                color: #00ff88;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.logs_table)

        return tab

    def create_settings_tab(self):
        """Crear pestaña de configuración"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Configuración de listas
        lists_layout = QHBoxLayout()

        # Whitelist
        whitelist_group = QGroupBox("✅ Whitelist (IPs Permitidas)")
        wl_layout = QVBoxLayout(whitelist_group)
        self.whitelist_display = QTextEdit()
        self.whitelist_display.setReadOnly(True)
        wl_layout.addWidget(self.whitelist_display)

        wl_input_layout = QHBoxLayout()
        self.wl_input = QLineEdit()
        self.wl_input.setPlaceholderText("Agregar IP a whitelist...")
        wl_add_btn = QPushButton("Agregar")
        wl_add_btn.clicked.connect(lambda: self.add_to_list('whitelist'))
        wl_input_layout.addWidget(self.wl_input)
        wl_input_layout.addWidget(wl_add_btn)
        wl_layout.addLayout(wl_input_layout)

        lists_layout.addWidget(whitelist_group)

        # Blacklist
        blacklist_group = QGroupBox("🚫 Blacklist (IPs Bloqueadas)")
        bl_layout = QVBoxLayout(blacklist_group)
        self.blacklist_display = QTextEdit()
        self.blacklist_display.setReadOnly(True)
        bl_layout.addWidget(self.blacklist_display)

        bl_input_layout = QHBoxLayout()
        self.bl_input = QLineEdit()
        self.bl_input.setPlaceholderText("Agregar IP a blacklist...")
        bl_add_btn = QPushButton("Agregar")
        bl_add_btn.clicked.connect(lambda: self.add_to_list('blacklist'))
        bl_input_layout.addWidget(self.bl_input)
        bl_input_layout.addWidget(bl_add_btn)
        bl_layout.addLayout(bl_input_layout)

        lists_layout.addWidget(blacklist_group)
        layout.addLayout(lists_layout)

        # Información del sistema
        info_group = QGroupBox("ℹ️ Información del Sistema")
        info_layout = QFormLayout(info_group)

        info_layout.addRow("Versión:", QLabel("2.0.0"))
        info_layout.addRow("Config Dir:", QLabel(CONFIG_DIR))
        info_layout.addRow("Log Path:", QLabel(LOG_PATH))

        health_btn = QPushButton("🔍 Verificar Salud del Sistema")
        health_btn.clicked.connect(self.check_health)
        info_layout.addRow(health_btn)

        layout.addWidget(info_group)
        layout.addStretch()

        return tab

    def setup_theme(self):
        """Aplicar tema cybersecurity"""
        # Paleta oscura
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor("#0f0f1a"))
        dark_palette.setColor(QPalette.WindowText, QColor("#eee"))
        dark_palette.setColor(QPalette.Base, QColor("#1a1a2e"))
        dark_palette.setColor(QPalette.AlternateBase, QColor("#16213e"))
        dark_palette.setColor(QPalette.Text, QColor("#eee"))
        dark_palette.setColor(QPalette.Button, QColor("#1a1a2e"))
        dark_palette.setColor(QPalette.ButtonText, QColor("#eee"))
        dark_palette.setColor(QPalette.Highlight, QColor("#00ff88"))
        dark_palette.setColor(QPalette.HighlightedText, QColor("#000"))
        QApplication.setPalette(dark_palette)

        # Hoja de estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f1a;
            }

            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #1a1a2e);
                border-radius: 15px;
                padding: 15px;
            }

            #statusPanel {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
            }

            #serviceStatus {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }

            #counterLabel {
                font-size: 14px;
                color: #888;
                padding: 5px;
            }

            #btnStart {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            #btnStart:hover {
                background-color: #2ecc71;
            }

            #btnStop {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            #btnStop:hover {
                background-color: #c0392b;
            }

            #btnRestart {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                min-width: 100px;
            }
            #btnRestart:hover {
                background-color: #2980b9;
            }

            #btnBan {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }

            #btnUnban {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }

            #statCard {
                background-color: #1a1a2e;
                border: 2px solid #333;
                border-radius: 15px;
                padding: 20px;
                min-width: 150px;
            }
            #statCard:hover {
                border-color: #00ff88;
            }

            QGroupBox {
                font-weight: bold;
                color: #00ff88;
                border: 2px solid #333;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
            }

            QTabWidget::pane {
                border: 2px solid #333;
                border-radius: 10px;
                background-color: #1a1a2e;
            }
            QTabBar::tab {
                background-color: #16213e;
                color: #888;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 5px;
            }
            QTabBar::tab:selected {
                background-color: #00ff88;
                color: #000;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #333;
            }

            QLineEdit {
                background-color: #0f0f1a;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 8px;
                color: #eee;
            }
            QLineEdit:focus {
                border-color: #00ff88;
            }

            QPushButton {
                background-color: #333;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }

            QStatusBar {
                background-color: #16213e;
                color: #888;
            }

            QScrollBar:vertical {
                background-color: #1a1a2e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #333;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00ff88;
            }
        """)

        # Intentar cargar imagen de tema si existe
        if os.path.exists(THEME_FILE):
            pixmap = QPixmap(THEME_FILE)
            if not pixmap.isNull():
                # Usar como fondo (opcional)
                palette = self.palette()
                palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(
                    self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
                self.setPalette(palette)

    # ==================== MÉTODOS DE ACTUALIZACIÓN ====================

    def update_from_daemon(self, state: dict):
        """Actualizar UI desde datos del daemon"""
        self.current_state = state

        # Actualizar contadores
        stats = state.get('statistics', {})
        attacks = stats.get('total_attacks', 0)
        bans = stats.get('total_bans', 0)
        banned_ips = state.get('banned_ips', [])

        self.attacks_label.setText(f"⚔️ Ataques: {attacks:,}")
        self.bans_label.setText(f"🚫 Baneos: {bans:,}")
        self.ips_label.setText(f"🎯 IPs Activas: {len(banned_ips)}")

        # Actualizar cards
        self.card_attacks.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(f"{attacks:,}")
        self.card_bans.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(f"{bans:,}")
        self.card_active.findChild(QLabel, "", Qt.FindChildrenRecursively).setText(f"{len(banned_ips)}")

        # Actualizar tablas
        self.update_top_attackers(stats.get('top_attackers', []))
        self.update_attacks_by_day(stats.get('attacks_by_day', {}))

        # Actualizar listas
        self.whitelist = set(state.get('whitelist', []))
        self.blacklist = set(state.get('blacklist', []))
        self.banned_ips = set(banned_ips)

    def on_log_detected(self, log_data: dict):
        """Manejar nuevo log detectado"""
        row = self.logs_table.rowCount()
        self.logs_table.insertRow(row)

        timestamp = log_data.get('timestamp', datetime.now().isoformat())
        date_part = timestamp.split('T')[0] if 'T' in timestamp else timestamp.split()[0]
        time_part = timestamp.split('T')[1][:8] if 'T' in timestamp else (timestamp.split()[1] if len(timestamp.split()) > 1 else '00:00:00')

        self.logs_table.setItem(row, 0, QTableWidgetItem(date_part))
        self.logs_table.setItem(row, 1, QTableWidgetItem(time_part))
        self.logs_table.setItem(row, 2, QTableWidgetItem(log_data['ip']))
        self.logs_table.setItem(row, 3, QTableWidgetItem(log_data['port']))
        self.logs_table.setItem(row, 4, QTableWidgetItem("Bloqueado"))

        # Auto-scroll
        self.logs_table.scrollToBottom()

    def update_top_attackers(self, top_attackers: list):
        """Actualizar tabla de top atacantes"""
        self.top_attackers_table.setRowCount(0)
        for i, (ip, count) in enumerate(top_attackers[:10]):
            row = self.top_attackers_table.rowCount()
            self.top_attackers_table.insertRow(row)
            self.top_attackers_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
            self.top_attackers_table.setItem(row, 1, QTableWidgetItem(ip))
            self.top_attackers_table.setItem(row, 2, QTableWidgetItem(str(count)))

    def update_attacks_by_day(self, attacks_by_day: dict):
        """Actualizar tabla de ataques por día"""
        self.attacks_by_day_table.setRowCount(0)
        for day, count in sorted(attacks_by_day.items(), reverse=True)[:7]:
            row = self.attacks_by_day_table.rowCount()
            self.attacks_by_day_table.insertRow(row)
            self.attacks_by_day_table.setItem(row, 0, QTableWidgetItem(day))
            self.attacks_by_day_table.setItem(row, 1, QTableWidgetItem(str(count)))

    def refresh_all(self):
        """Refrescar todos los datos"""
        # Verificar estado del servicio
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "shield-linux.service"],
                capture_output=True, text=True
            )
            status = result.stdout.strip()

            if status == "active":
                self.service_status.setText("🟢 ACTIVO")
                self.service_status.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 16px;")
            else:
                self.service_status.setText("🔴 INACTIVO")
                self.service_status.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 16px;")
        except:
            self.service_status.setText("⚪ DESCONOCIDO")

        # Leer archivos de configuración
        self.refresh_lists()

    def refresh_lists(self):
        """Refrescar visualización de listas"""
        # Whitelist
        try:
            if os.path.exists(WHITELIST_FILE):
                with open(WHITELIST_FILE, 'r') as f:
                    data = json.load(f)
                    self.whitelist = set(data.get('ips', []))
                    self.whitelist_display.setText('\n'.join(self.whitelist) or "Vacía")
        except:
            self.whitelist_display.setText("Error al cargar")

        # Blacklist
        try:
            if os.path.exists(BLACKLIST_FILE):
                with open(BLACKLIST_FILE, 'r') as f:
                    data = json.load(f)
                    self.blacklist = set(data.get('ips', []))
                    self.blacklist_display.setText('\n'.join(self.blacklist) or "Vacía")
        except:
            self.blacklist_display.setText("Error al cargar")

    def refresh_logs(self):
        """Refrescar tabla de logs"""
        self.logs_table.setRowCount(0)
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                temp_path = tmp.name
            subprocess.run(['sudo', 'cp', LOG_PATH, temp_path], capture_output=True)

            with open(temp_path, 'r') as f:
                for line in f.readlines()[-100:]:
                    if "[UFW BLOCK]" in line:
                        match = re.search(r"SRC=([\d\.]+).*DPT=(\d+)", line)
                        if match:
                            row = self.logs_table.rowCount()
                            self.logs_table.insertRow(row)
                            now = datetime.now()
                            self.logs_table.setItem(row, 0, QTableWidgetItem(now.strftime("%Y-%m-%d")))
                            self.logs_table.setItem(row, 1, QTableWidgetItem(now.strftime("%H:%M:%S")))
                            self.logs_table.setItem(row, 2, QTableWidgetItem(match.group(1)))
                            self.logs_table.setItem(row, 3, QTableWidgetItem(match.group(2)))
                            self.logs_table.setItem(row, 4, QTableWidgetItem("Bloqueado"))

            os.unlink(temp_path)
        except Exception as e:
            self.show_error(f"Error refrescando logs: {e}")

    # ==================== ACCIONES DE SERVICIO ====================

    def start_service(self):
        """Iniciar servicio"""
        try:
            subprocess.run(["sudo", "systemctl", "start", "shield-linux.service"], check=True)
            QMessageBox.information(self, "Éxito", "Servicio iniciado correctamente")
            self.refresh_all()
        except subprocess.CalledProcessError as e:
            self.show_error(f"No se pudo iniciar: {e}")

    def stop_service(self):
        """Detener servicio"""
        try:
            subprocess.run(["sudo", "systemctl", "stop", "shield-linux.service"], check=True)
            QMessageBox.information(self, "Éxito", "Servicio detenido")
            self.refresh_all()
        except subprocess.CalledProcessError as e:
            self.show_error(f"No se pudo detener: {e}")

    def restart_service(self):
        """Reiniciar servicio"""
        try:
            subprocess.run(["sudo", "systemctl", "restart", "shield-linux.service"], check=True)
            QMessageBox.information(self, "Éxito", "Servicio reiniciado")
            self.refresh_all()
        except subprocess.CalledProcessError as e:
            self.show_error(f"No se pudo reiniciar: {e}")

    # ==================== ACCIONES DE BANEO ====================

    def manual_ban(self):
        """Banear IP manualmente"""
        ip = self.manual_ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Advertencia", "Ingrese una IP")
            return

        if not self.is_valid_ip(ip):
            QMessageBox.warning(self, "Advertencia", "IP inválida")
            return

        try:
            subprocess.run(
                ["sudo", "ufw", "insert", "1", "deny", "from", ip],
                check=True
            )
            # Agregar a blacklist
            self.blacklist.add(ip)
            self.save_list(BLACKLIST_FILE, self.blacklist)

            QMessageBox.information(self, "Éxito", f"IP {ip} baneada")
            self.manual_ip_input.clear()
            self.refresh_all()
        except Exception as e:
            self.show_error(f"Error baneando: {e}")

    def manual_unban(self):
        """Unbanear IP manualmente"""
        ip = self.manual_ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Advertencia", "Ingrese una IP")
            return

        try:
            # Obtener reglas numeradas
            result = subprocess.run(
                ["sudo", "ufw", "status", "numbered"],
                capture_output=True, text=True
            )

            # Buscar y eliminar regla
            for i, line in enumerate(result.stdout.split('\n')):
                if ip in line and 'DENY' in line:
                    match = re.search(r'\[\s*(\d+)\]', line)
                    if match:
                        subprocess.run(
                            ["sudo", "ufw", "delete", match.group(1)],
                            check=True
                        )
                        break

            # Remover de blacklist
            self.blacklist.discard(ip)
            self.save_list(BLACKLIST_FILE, self.blacklist)

            QMessageBox.information(self, "Éxito", f"IP {ip} desbaneada")
            self.manual_ip_input.clear()
            self.refresh_all()
        except Exception as e:
            self.show_error(f"Error unbaneando: {e}")

    def add_to_list(self, list_type: str):
        """Agregar IP a whitelist/blacklist"""
        if list_type == 'whitelist':
            ip = self.wl_input.text().strip()
            if ip and self.is_valid_ip(ip):
                self.whitelist.add(ip)
                self.save_list(WHITELIST_FILE, self.whitelist)
                self.wl_input.clear()
                self.refresh_lists()
        else:
            ip = self.bl_input.text().strip()
            if ip and self.is_valid_ip(ip):
                self.blacklist.add(ip)
                self.save_list(BLACKLIST_FILE, self.blacklist)
                self.bl_input.clear()
                self.refresh_lists()

    def save_list(self, filepath: str, ips: set):
        """Guardar lista en archivo"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump({'ips': list(ips), 'updated': datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            self.show_error(f"Error guardando lista: {e}")

    def is_valid_ip(self, ip: str) -> bool:
        """Validar formato de IP"""
        import socket
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False

    def show_full_stats(self):
        """Mostrar estadísticas completas"""
        dialog = StatsDialog(self.current_state.get('statistics', {}), self)
        dialog.exec()

    def check_health(self):
        """Verificar salud del sistema"""
        issues = []

        # Check UFW
        try:
            result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
            if "Status: active" not in result.stdout:
                issues.append("UFW no está activo")
        except:
            issues.append("No se pudo verificar UFW")

        # Check logs
        if not os.path.exists(LOG_PATH):
            issues.append(f"Log {LOG_PATH} no existe")

        # Check daemon
        if not os.path.exists("/usr/local/bin/shield-linux"):
            issues.append("Daemon no instalado")

        if issues:
            QMessageBox.warning(
                self, "Problemas Detectados",
                "\n".join(issues)
            )
        else:
            QMessageBox.information(
                self, "Salud del Sistema",
                "✅ Todos los sistemas operativos correctamente"
            )

    def show_error(self, message: str):
        """Mostrar error"""
        self.statusBar().showMessage(f"❌ Error: {message}", 5000)

    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        self.daemon_comm.stop()
        self.daemon_comm.wait()
        self.log_monitor.stop()
        self.log_monitor.wait()
        event.accept()


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    # Verificar root
    if os.geteuid() != 0:
        print("⚠️ ShieldLinux Manager requiere privilegios de root")
        print("   Use: sudo python3 shield_manager.py")

    app = QApplication(sys.argv)
    app.setApplicationName("ShieldLinux Manager")

    window = ShieldManager()
    window.show()

    sys.exit(app.exec())

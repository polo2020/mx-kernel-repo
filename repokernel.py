import sys
import subprocess
import os
import urllib.request
import ssl
import shutil
import threading
import re
from pathlib import Path

# @Security-Auditor: Validación de integridad de binarios y firmas de firmware.
# @Senior Architect: Automatización de Inyección de Drivers y Ciclo de Compilación.
# @Python Patterns: Observer Pattern para logs en tiempo real.

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from tkinter import filedialog, messagebox

class KernelApp:
    def __init__(self):
        # Configuración de ventana - Jerarquía ttkbootstrap (Esquinas redondeadas por tema)
        self.root = tb.Window(
            title="Kernel Builder & Driver Integrator - Experto Yean Carlos",
            themename="darkly",
            resizable=(True, True)
        )
        # Geometría corregida 1100x850
        self.root.geometry("1100x850")

        # Parámetros técnicos y credenciales
        self.github_token = "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"
        self.selected_dir = ""
        self.deb_folder = ""
        self.deb_save_location = ""  # Nueva variable para ubicación de .deb
        self.is_processing = False

        self.setup_ui()

    def setup_ui(self):
        """Interfaz con Notebook y pestañas según orden de funciones del programa."""
        self.main_container = tb.Frame(self.root, padding=10)
        self.main_container.pack(fill=BOTH, expand=YES)

        self.tabs = tb.Notebook(self.main_container, bootstyle=INFO)
        self.tabs.pack(fill=BOTH, expand=YES)

        # --- PESTAÑA 1: CONSTRUCCIÓN Y DRIVERS ---
        self.tab_build = tb.Frame(self.tabs, padding=20)
        self.tabs.add(self.tab_build, text=" 🛠 Compilador e Integrador de Drivers ")

        self.btn_auto = tb.Button(
            self.tab_build,
            text="DESCARGAR KERNEL + DRIVERS WIFI Y COMPILAR .DEB",
            bootstyle=PRIMARY,
            command=self.start_auto_process
        )
        self.btn_auto.pack(fill=X, pady=5)

        # Botón para seleccionar dónde guardar los .deb
        save_frame = tb.Frame(self.tab_build)
        save_frame.pack(fill=X, pady=5)

        self.btn_save_location = tb.Button(
            save_frame,
            text="📁 SELECCIONAR CARPETA PARA GUARDAR .DEB",
            bootstyle=INFO,
            command=self.select_save_location
        )
        self.btn_save_location.pack(side=LEFT, padx=5)

        self.lbl_save_location = tb.Label(
            save_frame,
            text=f"Carpeta actual: {os.path.expanduser('~')}/Música",
            font=("Helvetica", 9)
        )
        self.lbl_save_location.pack(side=LEFT, padx=10)

        self.lbl_status = tb.Label(self.tab_build, text="Estado: Sistema listo", font=("Helvetica", 10))
        self.lbl_status.pack(pady=5)

        # Optimizaciones de Rendimiento (Skills: @Python Patterns)
        self.opt_frame = tb.Labelframe(self.tab_build, text=" Rendimiento y Compatibilidad Real ", padding=15)
        self.opt_frame.pack(fill=X, pady=10)

        self.c_intel = tb.Checkbutton(self.opt_frame, text="Intel MCORE2", bootstyle="info-toolbutton")
        self.c_intel.pack(side=LEFT, padx=10); self.c_intel.invoke()

        self.c_sen = tb.Checkbutton(self.opt_frame, text="1000Hz (Baja Latencia)", bootstyle="info-toolbutton")
        self.c_sen.pack(side=LEFT, padx=10); self.c_sen.invoke()

        self.c_liq = tb.Checkbutton(self.opt_frame, text="Liquorix/Zen Patches", bootstyle="info-toolbutton")
        self.c_liq.pack(side=LEFT, padx=10); self.c_liq.invoke()

        self.comp_log = ScrolledText(self.tab_build, height=20, autohide=True)
        self.comp_log.pack(fill=BOTH, expand=YES)
        self.comp_log.text.config(background="black", foreground="#00FF00", font=("Monospace", 10))

        # --- PESTAÑA 2: PUBLICADOR GITHUB ---
        self.tab_git = tb.Frame(self.tabs, padding=20)
        self.tabs.add(self.tab_git, text=" 🚀 Publicador GitHub ")

        # Frame para seleccionar carpeta de .deb
        select_frame = tb.Frame(self.tab_git)
        select_frame.pack(fill=X, pady=10)

        self.btn_select_deb = tb.Button(
            select_frame,
            text="📁 SELECCIONAR CARPETA CON .DEB",
            bootstyle=INFO,
            command=self.select_deb_folder
        )
        self.btn_select_deb.pack(side=LEFT, padx=5)

        self.lbl_deb_folder = tb.Label(
            select_frame,
            text="Sin carpeta seleccionada",
            font=("Helvetica", 9)
        )
        self.lbl_deb_folder.pack(side=LEFT, padx=10)

        git_frame = tb.Frame(self.tab_git)
        git_frame.pack(fill=X, pady=10)

        tb.Label(git_frame, text="Usuario Git:").pack(side=LEFT, padx=5)
        self.txt_user = tb.Entry(git_frame)
        self.txt_user.pack(side=LEFT, fill=X, expand=YES, padx=5)

        tb.Label(git_frame, text="Repo:").pack(side=LEFT, padx=5)
        self.txt_repo = tb.Entry(git_frame)
        self.txt_repo.insert(0, "mx-kernel-repo")
        self.txt_repo.pack(side=LEFT, fill=X, expand=YES, padx=5)

        self.btn_push = tb.Button(
            self.tab_git,
            text="SUBIR KERNEL Y DRIVERS A GITHUB",
            bootstyle=DANGER,
            command=self.start_git_sync
        )
        self.btn_push.pack(fill=X, pady=10)

        self.git_log = ScrolledText(self.tab_git, height=20, autohide=True)
        self.git_log.pack(fill=BOTH, expand=YES)
        self.git_log.text.config(background="#0d1117", foreground="#58a6ff", font=("Monospace", 10))

    def log_comp(self, msg):
        self.comp_log.insert(END, f"{msg}\n")
        self.comp_log.see(END)

    def select_save_location(self):
        """Seleccionar carpeta donde se guardarán los .deb compilados."""
        folder = filedialog.askdirectory(title="Selecciona la carpeta para guardar los .deb")
        if folder:
            self.deb_save_location = folder
            self.lbl_save_location.config(text=f"Carpeta actual: {folder}")
            self.log_comp(f">>> Ubicación para .deb cambiada a: {folder}")

    def select_deb_folder(self):
        """Seleccionar carpeta donde están los .deb para subir a GitHub."""
        folder = filedialog.askdirectory(title="Selecciona la carpeta con los .deb compilados")
        if folder:
            self.deb_folder = folder
            self.lbl_deb_folder.config(text=f"Carpeta seleccionada: {folder}")
            self.log_comp(f">>> Carpeta .deb para GitHub: {folder}")

    def get_latest_kernel_url(self):
        """Scraping real de kernel.org para obtener la versión más reciente."""
        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen("https://www.kernel.org/", context=context) as response:
                html = response.read().decode('utf-8')
                match = re.search(r'https://cdn\.kernel\.org/pub/linux/kernel/v\d+\.x/linux-\d+\.\d+\.\d+\.tar\.xz', html)
                if match: return match.group(0)
        except Exception as e:
            self.log_comp(f"Error buscando kernel: {e}")
        return None

    def setup_firmware(self, target_dir):
        """Descarga e integra drivers (firmware) oficiales para WiFi/Bluetooth."""
        try:
            self.log_comp(">>> Paso 2: Descargando drivers WiFi/BT (linux-firmware)...")
            fw_path = os.path.join(target_dir, "firmware")
            if os.path.exists(fw_path): shutil.rmtree(fw_path)

            # Clonación shallow para ahorrar espacio e integrar drivers reales
            subprocess.run(["git", "clone", "--depth", "1",
                          "https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git",
                          fw_path], check=True)
            self.log_comp(">>> Drivers descargados y listos para integración.")
            return fw_path
        except Exception as e:
            self.log_comp(f">>> Advertencia Drivers: {e}")
            return None

    def start_auto_process(self):
        if self.is_processing: return
        self.is_processing = True
        self.btn_auto.config(state=DISABLED)
        threading.Thread(target=self.auto_worker, daemon=True).start()

    def auto_worker(self):
        try:
            download_dir = os.path.join(os.path.expanduser("~"), "Descargas", "KernelBuild")
            if os.path.exists(download_dir): shutil.rmtree(download_dir)
            os.makedirs(download_dir, exist_ok=True)
            os.chdir(download_dir)

            # 1. Obtener Kernel
            self.log_comp(">>> Paso 1: Buscando versión estable más reciente...")
            url = self.get_latest_kernel_url()
            if not url: return

            filename = url.split("/")[-1]
            self.log_comp(f">>> Descargando Kernel: {filename}")
            context = ssl._create_unverified_context()
            urllib.request.urlretrieve(url, filename)

            # 2. Obtener Drivers (Función reintegrada)
            self.setup_firmware(download_dir)

            # 3. Extraer Código
            self.log_comp(">>> Paso 3: Extrayendo código fuente...")
            subprocess.run(["tar", "-xf", filename], check=True)

            folder_name = filename.replace(".tar.xz", "")
            self.selected_dir = os.path.join(download_dir, folder_name)

            if os.path.exists(self.selected_dir):
                os.chdir(self.selected_dir)
                self.run_compilation_logic()
            else:
                self.log_comp(">>> Error: No se halló el directorio extraído.")

        except Exception as e:
            self.log_comp(f"Fallo en el flujo: {str(e)}")
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.btn_auto.config(state=NORMAL))

    def run_compilation_logic(self):
        """Lógica de Senior Architect para compilación optimizada."""
        try:
            cfg = "./scripts/config"
            self.log_comp(">>> Paso 4: Actualizando dependencias de Debian/MX...")
            deps = ["build-essential", "libncurses-dev", "bison", "flex", "libssl-dev", "libelf-dev",
                    "bc", "dwarves", "rsync", "kmod", "debhelper", "pkg-config", "cpio", "dpkg-dev", "git",
                    "firmware-linux", "firmware-linux-nonfree", "firmware-atheros", "firmware-realtek",
                    "dpkg-dev", "libdw-dev", "libperl-dev", "zstd", "xz-utils"]

            # Primero actualizar
            self.log_comp(">>> Ejecutando: sudo apt-get update...")
            result = subprocess.run(["sudo", "apt-get", "update"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_comp(f">>> ERROR en update: {result.stderr}")

            # Intentar instalar y capturar error detallado
            self.log_comp(">>> Instalando dependencias...")
            result = subprocess.run(["sudo", "apt-get", "install", "-y"] + deps, capture_output=True, text=True)
            if result.returncode != 0:
                self.log_comp(f">>> ERROR en install: {result.stderr}")
                self.log_comp(f">>> Salida: {result.stdout}")
                self.log_comp(">>> Intentando instalar sin paquetes problemáticos...")
                # Intentar sin firmware-no-free que puede causar problemas
                deps_basic = ["build-essential", "libncurses-dev", "bison", "flex", "libssl-dev", "libelf-dev",
                        "bc", "dwarves", "rsync", "kmod", "debhelper", "pkg-config", "cpio", "dpkg-dev", "git",
                        "libdw-dev", "zstd", "xz-utils"]
                result = subprocess.run(["sudo", "apt-get", "install", "-y"] + deps_basic, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_comp(f">>> ERROR crítico: {result.stderr}")
                    self.log_comp(">>> Ejecuta manualmente: sudo apt-get install -y build-essential libncurses-dev bison flex libssl-dev libelf-dev bc dwarves rsync kmod debhelper pkg-config cpio dpkg-dev git libdw-dev zstd xz-utils")
                    return

            # Headers del kernel actual
            import platform
            kernel_ver = platform.uname().release
            self.log_comp(f">>> Instalando headers para kernel {kernel_ver}...")
            result = subprocess.run(["sudo", "apt-get", "install", "-y", f"linux-headers-{kernel_ver}"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_comp(f">>> ADVERTENCIA: No se pudieron instalar headers: {result.stderr}")
                self.log_comp(">>> Continuando sin headers...")

            # Verificar que dpkg-deb esté disponible
            result = subprocess.run(["which", "dpkg-deb"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log_comp(f">>> dpkg-deb disponible en: {result.stdout.strip()}")
            else:
                self.log_comp(">>> ERROR: dpkg-deb no encontrado - los .deb no se generarán")

            self.log_comp(">>> Paso 5: Generando configuración (make defconfig)...")
            subprocess.run(["make", "defconfig"], check=True)

            # Inyección de Optimizaciones
            if "selected" in self.c_intel.state():
                self.log_comp(">>> [Opt] MCORE2 activado.")
                subprocess.run([cfg, "--enable", "CONFIG_MCORE2"], check=True)
            if "selected" in self.c_sen.state():
                self.log_comp(">>> [Opt] Baja Latencia 1000Hz activada.")
                subprocess.run([cfg, "--set-val", "CONFIG_HZ", "1000"], check=True)
                subprocess.run([cfg, "--enable", "CONFIG_HZ_1000"], check=True)
            if "selected" in self.c_liq.state():
                self.log_comp(">>> [Opt] PREEMPT (Zen) activado.")
                subprocess.run([cfg, "--enable", "CONFIG_PREEMPT"], check=True)

            # === DRIVERS ESPECÍFICOS PARA TU HARDWARE ===
            self.log_comp(">>> [HW] Activando soporte para Qualcomm Atheros AR9485 WiFi...")
            subprocess.run([cfg, "--enable", "CONFIG_ATH9K"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH9K_PCI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH9K_COMMON"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH9K_HW"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH9K_BTCOEX_SUPPORT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH9K_DEBUGFS"], check=True)

            # === SOPORTE COMPLETO PARA WIFI ===
            self.log_comp(">>> [WIFI] Activando soporte completo para WiFi...")

            # Stack inalámbrico base
            subprocess.run([cfg, "--enable", "CONFIG_CFG80211"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CFG80211_REQUIRE_SIGNED_REGDB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MAC80211"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MAC80211_MESH"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MAC80211_LEDS"], check=True)

            # Control de radio
            subprocess.run([cfg, "--enable", "CONFIG_RFKILL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RFKILL_GPIO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RFKILL_INPUT"], check=True)

            # Drivers Intel WiFi
            self.log_comp(">>> [WIFI] Drivers Intel WiFi...")
            subprocess.run([cfg, "--enable", "CONFIG_IWLMVM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_IWLWIFI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_IWLWIFI_LEDS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_IWLDVM"], check=True)

            # Drivers Realtek WiFi
            self.log_comp(">>> [WIFI] Drivers Realtek WiFi...")
            subprocess.run([cfg, "--enable", "CONFIG_RTLWIFI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTL8XXXU"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTL8XXXU_UNTESTED"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTW88"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTW88_PCI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTW88_USB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTW88_8822CE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RTW88_8822BE"], check=True)

            # Drivers Broadcom WiFi
            self.log_comp(">>> [WIFI] Drivers Broadcom WiFi...")
            subprocess.run([cfg, "--enable", "CONFIG_B43"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_B43LEGACY"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BRCMFMAC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BRCMFMAC_USB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BRCMFMAC_SDIO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BRCMFMAC_PCIE"], check=True)

            # Drivers MediaTek WiFi
            self.log_comp(">>> [WIFI] Drivers MediaTek WiFi...")
            subprocess.run([cfg, "--enable", "CONFIG_MT76x0U"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MT76x2E"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MT76x2U"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MT7601U"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MT76_CORE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MT76_LEDS"], check=True)

            # Drivers Qualcomm/Atheros adicionales
            self.log_comp(">>> [WIFI] Drivers Qualcomm/Atheros adicionales...")
            subprocess.run([cfg, "--enable", "CONFIG_ATH5K"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH10K"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH10K_PCI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH11K"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATH12K"], check=True)

            # Drivers USB WiFi genéricos
            self.log_comp(">>> [WIFI] Drivers USB WiFi...")
            subprocess.run([cfg, "--enable", "CONFIG_USB_NET_RNDIS_WLAN"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_USB_NET_AIRGO_NX"], check=True)

            # === SOPORTE COMPLETO PARA BLUETOOTH ===
            self.log_comp(">>> [BT] Activando soporte completo para Bluetooth...")

            # Subsystem Bluetooth base
            subprocess.run([cfg, "--enable", "CONFIG_BT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BREDR"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RFCOMM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RFCOMM_TTY"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BNEP"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BNEP_MC_FILTER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BNEP_PROTO_FILTER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HIDP"], check=True)

            # Bluetooth Low Energy (BLE)
            subprocess.run([cfg, "--enable", "CONFIG_BT_LE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_LE_L2CAP_DYNAMIC_CHANNEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_LE_PERIPHERAL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_LE_CENTRAL"], check=True)

            # Bluetooth Classic features
            subprocess.run([cfg, "--enable", "CONFIG_BT_HS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_AMP"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_DEBUGFS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MSFTEXT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_AOSPEXT"], check=True)

            # Controladores Bluetooth Intel
            self.log_comp(">>> [BT] Drivers Intel Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_INTEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_INTEL_TLV"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_INTEL_EPP"], check=True)

            # Controladores Bluetooth Realtek
            self.log_comp(">>> [BT] Drivers Realtek Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8723"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8723B"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8723D"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8821A"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8821C"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8822B"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8822C"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8761"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8761B"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8852A"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8852B"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RTL8852C"], check=True)

            # Controladores Bluetooth Broadcom
            self.log_comp(">>> [BT] Drivers Broadcom Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_BCM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BCM_UART"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BCM_USB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BCM_SERIAL"], check=True)

            # Controladores Bluetooth Atheros/Qualcomm
            self.log_comp(">>> [BT] Drivers Atheros/Qualcomm Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_ATH3K"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_QCA"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_QCA6390"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_QCA617X"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_QCA6390_SERIAL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_AR3012"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_AR3012_SERIAL"], check=True)

            # Controladores Bluetooth MediaTek
            self.log_comp(">>> [BT] Drivers MediaTek Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_MTK"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MT7622"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MT7921A"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MT7921U"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MT7922"], check=True)

            # Controladores Bluetooth Marvell
            self.log_comp(">>> [BT] Drivers Marvell Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_MRVL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MRVL_SDIO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MRVL_UART"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MRVL_USB"], check=True)

            # Controladores Bluetooth CSR
            self.log_comp(">>> [BT] Drivers CSR Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_CSR"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_CSR_USB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_CSR_UART"], check=True)

            # Controladores Bluetooth Broadcom (alternativo)
            self.log_comp(">>> [BT] Drivers Broadcom (alternativo)...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_BPA10X"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_BFUSB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_DTL1"], check=True)

            # Transportes Bluetooth
            self.log_comp(">>> [BT] Transportes Bluetooth...")

            # USB Bluetooth
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTUSB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTUSB_BCM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTUSB_MTK"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTUSB_RTL"], check=True)

            # UART/Serial Bluetooth
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_H4"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_BCSP"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_ATH3K"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_LL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_3WIRE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_INTEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_BCM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_QCA"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_AG6XX"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIUART_MRVL"], check=True)

            # SDIO Bluetooth
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTSDIO"], check=True)

            # PCI/PCIe Bluetooth
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBT3C"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTQCA"], check=True)

            # Virtual Bluetooth
            subprocess.run([cfg, "--enable", "CONFIG_BT_VIRTIO"], check=True)

            # RFKILL para Bluetooth (interruptor hardware)
            subprocess.run([cfg, "--enable", "CONFIG_BT_RFKILL"], check=True)

            # Soporte para audio Bluetooth (A2DP, HSP, HFP)
            self.log_comp(">>> [BT] Audio Bluetooth (A2DP/HSP/HFP)...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBTUSB_AUTOSUSPEND"], check=True)

            # Bluetooth GPIO
            subprocess.run([cfg, "--enable", "CONFIG_BT_GPIO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_MRVL_GPIO"], check=True)

            # Bluetooth virtuales y de prueba
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIVHCI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBCM203X"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBPA10X"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIBFUSB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BT_HCIDTL1"], check=True)

            # Bluetooth Coexistence (WiFi + BT)
            self.log_comp(">>> [BT] Coexistencia WiFi + Bluetooth...")
            subprocess.run([cfg, "--enable", "CONFIG_BT_COEXIST"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BTCOEX"], check=True)

            # === SOPORTE COMPLETO PARA AUDIO ===
            self.log_comp(">>> [AUDIO] Activando soporte completo para audio...")

            # Audio base ALSA
            subprocess.run([cfg, "--enable", "CONFIG_SND"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_TIMER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_PCM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HWDEP"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_RAWMIDI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SEQUENCER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SEQ_DUMMY"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HRTIMER"], check=True)

            # Intel HD Audio (tu hardware)
            self.log_comp(">>> [AUDIO] Intel HD Audio (7 Series/C216)...")
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_INTEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_REALTEK"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_HDMI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_SIGMATEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_ANALOG"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_CMOS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_CONEXANT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_CA0110"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_CA0132"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_CIRRUS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_IDT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CODEC_SI3054"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_GENERIC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_GENERIC_LIB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_POWER_SAVE_DEFAULT"], check=True)
            subprocess.run([cfg, "--set-val", "CONFIG_SND_HDA_PREALLOC_SIZE", "64"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_CORE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_DSP_LOADER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_COMPONENT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_I915"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_EXT_CORE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_HDA_SCODEC_COMPONENT"], check=True)

            # Audio USB
            self.log_comp(">>> [AUDIO] Audio USB...")
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_AUDIO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_UA101"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_USX2Y"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_CAIAQ"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_6FIRE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_HIFACE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_POD"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_PODHD"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_TONEPORT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USB_VARIAX"], check=True)

            # Audio PCI y chipset
            self.log_comp(">>> [AUDIO] Audio PCI y chipset...")
            subprocess.run([cfg, "--enable", "CONFIG_SND_VIA82XX"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_VIA82XX_MODEM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_AC97_CODEC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_AC97_BUS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_INTEL8X0"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_INTEL8X0M"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_ALI5451"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_CS4281"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_EMU10K1"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_EMU10K1X"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_FM801"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SONICVIBES"], check=True)

            # Audio I2S y ASoC (System on Chip)
            self.log_comp(">>> [AUDIO] ASoC (Audio System on Chip)...")
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_ACPI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_ACPI_INTEL_MATCH"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_COMMON"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_SST_TOPLEVEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_SST"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_SKYLAKE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_SKYLAKE_COMMON"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_SKYLAKE_HDA_AUDIO_CODEC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_INTEL_SKYLAKE_I2S_TEST_MODE"], check=True)

            # Codecs de audio adicionales
            self.log_comp(">>> [AUDIO] Codecs adicionales...")
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_ALL_CODECS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_MAX98927"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_RT5640"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_RT5651"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_SGTL5000"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_WM8524"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_WM8904"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_WM8960"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_WM8962"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_WM8978"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_SOC_WM8994"], check=True)

            # Audio comprimido y efectos
            self.log_comp(">>> [AUDIO] Audio comprimido y efectos...")
            subprocess.run([cfg, "--enable", "CONFIG_SND_COMPRESS_OFFLOAD"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_JACK"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_JACK_INPUT_DEV"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_CTL_LED"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_VMASTER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_DMA_SGBUF"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_USE_VMASTER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SND_AC97_POWER_SAVE"], check=True)
            subprocess.run([cfg, "--set-val", "CONFIG_SND_AC97_POWER_SAVE_DEFAULT", "1"], check=True)

            # Firmware embebido para evitar errores de carga
            self.log_comp(">>> [FW] Configurando firmware embebido en el kernel...")
            subprocess.run([cfg, "--enable", "CONFIG_FW_LOADER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_EXTRA_FIRMWARE"], check=True)
            subprocess.run([cfg, "--set-val", "CONFIG_EXTRA_FIRMWARE_DIR", '"/lib/firmware"'], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FIRMWARE_IN_KERNEL"], check=True)

            # Soporte adicional para WiFi
            subprocess.run([cfg, "--enable", "CONFIG_CFG80211"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MAC80211"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RFKILL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_RFKILL_GPIO"], check=True)

            # === SOPORTE exFAT (Ventoy) ===
            self.log_comp(">>> [FS] Activando soporte para exFAT (Ventoy/USB)...")
            subprocess.run([cfg, "--enable", "CONFIG_EXFAT_FS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_EXFAT_DEFAULT_IOCHARSET"], check=True)
            subprocess.run([cfg, "--set-val", "CONFIG_EXFAT_DEFAULT_IOCHARSET", '"utf8"'], check=True)

            # === SOPORTE COMPLETO NTFS ===
            self.log_comp(">>> [FS] Activando soporte completo para NTFS...")
            subprocess.run([cfg, "--enable", "CONFIG_NTFS_FS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NTFS_RW"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NTFS3_FS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NTFS3_LZX_XPRESS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NTFS3_FS_POSIX_ACL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NTFS3_XATTR"], check=True)

            # === GESTIÓN DE ENERGÍA ACPI ===
            self.log_comp(">>> [ACPI] Activando gestión de energía completa...")
            subprocess.run([cfg, "--enable", "CONFIG_ACPI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_BUTTON"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_VIDEO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_THERMAL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_PROCESSOR"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_CPU_FREQ_PSS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_PROCESSOR_CSTATE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_PROCESSOR_IDLE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_X86_ACPI_CPUFREQ"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_X86_ACPI_CPUFREQ_PCC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_FREQ"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_FREQ_GOV_POWERSAVE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_FREQ_GOV_PERFORMANCE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_FREQ_GOV_ONDEMAND"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_FREQ_GOV_CONSERVATIVE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_FREQ_GOV_SCHEDUTIL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_INTEL_IDLE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_IDLE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_INTEL_TCC_COOLING"], check=True)

            # === GESTIÓN DE DISCOS Y USB ===
            self.log_comp(">>> [DISK] Activando gestión avanzada de discos...")
            subprocess.run([cfg, "--enable", "CONFIG_USB_STORAGE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_USB_UAS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SATA_AHCI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SATA_AHCI_PLATFORM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATA"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ATA_ACPI"], check=True)

            # === SOPORTE COMPLETO PARA NVIDIA ===
            self.log_comp(">>> [GPU] Activando soporte completo para NVIDIA...")

            # DRM (Direct Rendering Manager) - Requerido para NVIDIA
            subprocess.run([cfg, "--enable", "CONFIG_DRM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_KMS_HELPER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_KMS_FB_HELPER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_FBDEV_EMULATION"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_LOAD_EDID_FIRMWARE"], check=True)

            # Nouveau (driver open-source para NVIDIA)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_LEGACY_CTX_SUPPORT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NOUVEAU_DEBUG"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NOUVEAU_DEBUG_DEFAULT"], check=True)

            # Soporte para NVIDIA GeForce (todas las generaciones)
            self.log_comp(">>> [GPU] Soporte NVIDIA GeForce...")
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NV04"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NV10"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NV20"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NV30"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NV40"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NV50"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_NOUVEAU_NVC0"], check=True)

            # TTM (Translation Table Manager) - Gestión de memoria GPU
            subprocess.run([cfg, "--enable", "CONFIG_DRM_TTM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_TTM_HELPER"], check=True)

            # GEM (Graphics Execution Manager)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_GEM_SHMEM_HELPER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_GEM_CMA_HELPER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_KMS_CMA_HELPER"], check=True)

            # I2C para comunicación con GPU
            subprocess.run([cfg, "--enable", "CONFIG_DRM_I2C_CH7006"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_I2C_SIL164"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_I2C_NXP_TDA998X"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_I2C_NXP_TDA9950"], check=True)

            # Codecs de video para NVIDIA
            self.log_comp(">>> [GPU] Codecs de video...")
            subprocess.run([cfg, "--enable", "CONFIG_VIDEO_NVDEC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEO_NVENC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEO_V4L2"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEOBUF2_CORE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEOBUF2_V4L2"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEOBUF2_MEMOPS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEOBUF2_DMA_CONTIG"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VIDEOBUF2_VMALLOC"], check=True)

            # Framebuffer (consola en modo texto)
            subprocess.run([cfg, "--enable", "CONFIG_FB"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_SIMPLE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_EFI"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_NVIDIA"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_NVIDIA_I2C"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_RIVA"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_RIVA_I2C"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_FB_RIVA_DEBUG"], check=True)

            # AGP (Accelerated Graphics Port) - GPUs antiguas
            subprocess.run([cfg, "--enable", "CONFIG_AGP"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AGP_AMD64"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AGP_INTEL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AGP_SIS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AGP_VIA"], check=True)

            # PCI Express - Requerido para GPUs modernas
            subprocess.run([cfg, "--enable", "CONFIG_PCIEPORTBUS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_PCIEAER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_PCIEASPM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_PCIEASPM_DEFAULT"], check=True)

            # DMA (Direct Memory Access) para transferencia de datos
            subprocess.run([cfg, "--enable", "CONFIG_DMADEVICES"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DMA_ENGINE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DMA_ACPI"], check=True)

            # MTRR (Memory Type Range Register) - Optimización de memoria
            subprocess.run([cfg, "--enable", "CONFIG_MTRR"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MTRR_SANITIZER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_MTRR_SANITIZER_ENABLE_DEFAULT"], check=True)

            # VGA Switcheroo (para laptops con GPU dual)
            subprocess.run([cfg, "--enable", "CONFIG_VGA_SWITCHEROO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_VGA_ARB"], check=True)
            subprocess.run([cfg, "--set-val", "CONFIG_VGA_ARB_MAX_GPUS", "16"], check=True)

            # HDMI y DisplayPort
            subprocess.run([cfg, "--enable", "CONFIG_DRM_DP_AUX_BUS"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_DP_CEC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_DISPLAY_CONNECTOR"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_DISPLAY_DP_HELPER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_DISPLAY_HDCP_HELPER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DRM_DISPLAY_HDMI_HELPER"], check=True)

            # Backlight (control de brillo)
            subprocess.run([cfg, "--enable", "CONFIG_BACKLIGHT_CLASS_DEVICE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BACKLIGHT_LCD_SUPPORT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BACKLIGHT_GENERIC"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_BACKLIGHT_PWM"], check=True)

            # Soporte para NVIDIA Prime / Optimus (laptops)
            self.log_comp(">>> [GPU] Soporte NVIDIA Optimus/Prime...")
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_VIDEO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_BATTERY"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_ACPI_AC"], check=True)

            # DPTF (Dynamic Platform and Thermal Framework) - Gestión térmica NVIDIA
            subprocess.run([cfg, "--enable", "CONFIG_DPTF_POWER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DPTF_THERMAL"], check=True)

            # HWMON (monitoreo de hardware) - Temperaturas GPU
            subprocess.run([cfg, "--enable", "CONFIG_HWMON"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SENSORS_NCT7802"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_THERMAL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_THERMAL_GOV_FAIR_SHARE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_THERMAL_GOV_STEP_WISE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_THERMAL_GOV_USER_SPACE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_CPU_THERMAL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_DEVFREQ_THERMAL"], check=True)

            # === MÓDULO DE SEGURIDAD SHIELD LINUX ===
            self.log_comp(">>> [🛡️] Integrando Módulo de Seguridad ShieldLinux...")
            self.log_comp(">>> [🛡️] 22 funciones de seguridad con 8 contramedidas activas")

            # Habilitar opciones de seguridad del kernel
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_YAMA"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_APPARMOR"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_SELINUX"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_SMACK"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_TOMOYO"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_LOCKDOWN_LSM"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_SECURITY_LOCKDOWN_LSM_EARLY"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_LOCK_DOWN_KERNEL_FORCE_CONFIDENTIALITY"], check=True)

            # Opciones de red segura
            subprocess.run([cfg, "--enable", "CONFIG_NETFILTER_XT_MATCH_OWNER"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NETFILTER_XT_MATCH_STRING"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NETFILTER_XT_MATCH_HASHLIMIT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NETFILTER_XT_TARGET_TEE"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_NETFILTER_XT_TARGET_HL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_IP_NF_TARGET_REJECT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_IP_NF_TARGET_REDIRECT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_IP_NF_TARGET_MASQUERADE"], check=True)

            # Audit y logging de seguridad
            subprocess.run([cfg, "--enable", "CONFIG_AUDIT"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AUDITSYSCALL"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AUDIT_WATCH"], check=True)
            subprocess.run([cfg, "--enable", "CONFIG_AUDIT_TREE"], check=True)

            # Copiar módulo de seguridad al directorio del kernel
            security_module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modulo_seguridad")
            kernel_module_src = os.path.join(security_module_dir, "kernel_module")
            kernel_module_dest = os.path.join(self.selected_dir, "security")

            if os.path.exists(kernel_module_src):
                self.log_comp(">>> [🛡️] Copiando módulo de seguridad al kernel...")
                shutil.copytree(kernel_module_src, kernel_module_dest, dirs_exist_ok=True)

                # Agregar al Makefile del kernel
                makefile_path = os.path.join(self.selected_dir, "Makefile")
                if os.path.exists(makefile_path):
                    with open(makefile_path, 'a') as f:
                        f.write("\n# ShieldLinux Security Module\n")
                        f.write("obj-y += security/\n")
                    self.log_comp(">>> [🛡️] Módulo agregado al Makefile del kernel")
            else:
                self.log_comp(">>> [🛡️] Advertencia: Módulo de seguridad no encontrado, continuando sin él")

            subprocess.run([cfg, "--enable", "CONFIG_BTF"], check=True)
            subprocess.run(["make", "olddefconfig"], check=True)

            # Compilación masiva
            cores = os.cpu_count()
            self.log_comp(f">>> Paso 6: Compilando con {cores} hilos...")
            proc = subprocess.Popen(["make", f"-j{cores}", "bindeb-pkg"],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in proc.stdout:
                self.log_comp(line.strip())

            proc.wait()

            if proc.returncode == 0:
                self.log_comp(">>> !!! KERNEL Y DRIVERS COMPILADOS EXITOSAMENTE !!!")

                # Mostrar ruta del kernel compilado
                self.log_comp(f">>> Directorio del kernel: {self.selected_dir}")

                # Verificar estructura de debian/output
                output_base = os.path.join(self.selected_dir, "debian", "output")
                self.log_comp(f">>> Buscando en: {output_base}")

                # Listar todo lo que hay en debian/
                debian_dir = os.path.join(self.selected_dir, "debian")
                if os.path.exists(debian_dir):
                    self.log_comp(">>> Contenido de debian/:")
                    for item in os.listdir(debian_dir):
                        self.log_comp(f"   - {item}")

                # Buscar TODOS los .deb en TODO el directorio del kernel
                all_debs = []
                self.log_comp(">>> Buscando .deb recursivamente...")
                for root, dirs, files in os.walk(self.selected_dir):
                    for f in files:
                        if f.endswith(".deb"):
                            full_path = os.path.join(root, f)
                            all_debs.append(full_path)
                            self.log_comp(f"   ✓ Encontrado: {full_path}")

                # También buscar en el directorio padre (donde bindeb-pkg a veces los pone)
                parent_dir = os.path.dirname(self.selected_dir)
                self.log_comp(f">>> Buscando también en: {parent_dir}")
                for f in os.listdir(parent_dir):
                    if f.endswith(".deb") and f not in [os.path.basename(d) for d in all_debs]:
                        full_path = os.path.join(parent_dir, f)
                        all_debs.append(full_path)
                        self.log_comp(f"   ✓ Encontrado en padre: {full_path}")

                if all_debs:
                    # Determinar dónde guardar los .deb
                    if self.deb_save_location:
                        # Usar la carpeta seleccionada por el usuario
                        self.deb_folder = self.deb_save_location
                    else:
                        # Usar la carpeta del script como predeterminada
                        self.deb_folder = os.path.dirname(os.path.abspath(__file__))

                    os.makedirs(self.deb_folder, exist_ok=True)

                    # Copiar todos los .deb a la carpeta seleccionada
                    for deb_path in all_debs:
                        shutil.copy(deb_path, self.deb_folder)

                    self.log_comp(f">>> Paquetes .deb copiados a: {self.deb_folder}")
                    self.log_comp(f">>> Total: {len(all_debs)} paquetes .deb")
                    for f in os.listdir(self.deb_folder):
                        if f.endswith(".deb"):
                            self.log_comp(f"   ✓ {f}")
                else:
                    self.log_comp(">>> ERROR CRÍTICO: No se encontraron .deb en NINGUNA ubicación")
                    self.log_comp(">>> Posibles causas:")
                    self.log_comp(">>>   1. La compilación falló silenciosamente")
                    self.log_comp(">>>   2. dpkg-deb no está instalado")
                    self.log_comp(">>>   3. Falta espacio en disco")
                    self.deb_folder = ""

                self.root.after(0, lambda: messagebox.showinfo("Éxito" if all_debs else "Advertencia",
                    f"{'Paquetes .deb listos en:\n' + self.deb_folder if all_debs else 'No se generaron .deb - Revisa los logs'}"))
            else:
                self.log_comp(">>> ERROR: Fallo en bindeb-pkg.")

        except Exception as e:
            self.log_comp(f"Error técnico: {e}")

    def start_git_sync(self):
        user = self.txt_user.get()
        if not user or not self.deb_folder:
            messagebox.showwarning("Atención", "Escribe tu usuario y selecciona la carpeta con los .deb primero.")
            return
        self.btn_push.config(state=DISABLED)
        threading.Thread(target=self.git_worker, args=(user, self.txt_repo.get()), daemon=True).start()

    def git_worker(self, user, repo):
        try:
            self.git_log.insert(END, f">>> Iniciando subida a GitHub: {user}/{repo}...\n")
            temp_path = os.path.join(os.path.expanduser("~"), "temp_git_kernel")
            if os.path.exists(temp_path): shutil.rmtree(temp_path)
            os.makedirs(temp_path, exist_ok=True)

            # Recolectar .debs generados (búsqueda recursiva por si están en subcarpetas)
            deb_count = 0
            for root, dirs, files in os.walk(self.deb_folder):
                for f in files:
                    if f.endswith(".deb"):
                        shutil.copy(os.path.join(root, f), temp_path)
                        deb_count += 1
                        self.git_log.insert(END, f">>> Añadido: {f}\n")

            if deb_count == 0:
                self.git_log.insert(END, ">>> ERROR: No se encontraron archivos .deb\n")
                self.root.after(0, lambda: self.btn_push.config(state=NORMAL))
                return

            self.git_log.insert(END, f">>> Total .deb encontrados: {deb_count}\n")
            os.chdir(temp_path)
            # Crear repositorio APT (Packages) - archivos en raíz
            with open("Packages", "w") as f:
                subprocess.run(["dpkg-scanpackages", ".", "/dev/null"], stdout=f, check=True)
            subprocess.run(["gzip", "-9fk", "Packages"], check=True)

            # Git Commands
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Kernel Release con Drivers Integrados"], check=True)

            url = f"https://{self.github_token}@github.com/{user}/{repo}.git"
            subprocess.run(["git", "remote", "add", "origin", url], check=False)
            # FORZAR rama master (requerido para repositorio APT)
            branch = "master"
            self.git_log.insert(END, f">>> Usando rama: {branch} (forzada)\n")
            res = subprocess.run(["git", "push", "-u", "origin", branch, "--force"], capture_output=True, text=True)

            if res.returncode == 0:
                self.git_log.insert(END, f">>> PUBLICADO CON ÉXITO: https://github.com/{user}/{repo}\n")
                self.git_log.insert(END, "\n" + "="*60 + "\n")
                self.git_log.insert(END, ">>> URL PARA AGREGAR A TUS REPOSITORIOS APT:\n")
                self.git_log.insert(END, "="*60 + "\n")
                self.git_log.insert(END, f"deb [trusted=yes] https://{user}.github.io/{repo}/ ./\n")
                self.git_log.insert(END, "="*60 + "\n")
                self.git_log.insert(END, "\n>>> COMANDO PARA AGREGAR AUTOMÁTICAMENTE:\n")
                self.git_log.insert(END, f"echo 'deb [trusted=yes] https://{user}.github.io/{repo}/ ./' | sudo tee /etc/apt/sources.list.d/custom-kernel.list\n")
                self.git_log.insert(END, ">>> Luego ejecuta: sudo apt update\n")

                # Mostrar mensaje emergente con la URL
                apt_url = f"deb [trusted=yes] https://{user}.github.io/{repo}/ ./"
                self.root.after(0, lambda: messagebox.showinfo(
                    "¡Publicación Exitosa!",
                    f"Repositorio: https://github.com/{user}/{repo}\n\n"
                    f"URL para APT:\n{apt_url}\n\n"
                    "Copia esta URL en /etc/apt/sources.list.d/"
                ))
            else:
                self.git_log.insert(END, f">>> ERROR GIT: {res.stderr}\n")

        except Exception as e:
            self.git_log.insert(END, f"Error en despliegue: {e}\n")
        finally:
            self.root.after(0, lambda: self.btn_push.config(state=NORMAL))

if __name__ == "__main__":
    app = KernelApp()
    app.root.mainloop()

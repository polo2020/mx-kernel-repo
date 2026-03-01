# 🛡️ SHIELD LINUX - Makefile para Módulo del Kernel
# Compilación del módulo de seguridad

KERNEL_VERSION := $(shell uname -r)
KERNEL_DIR := /lib/modules/$(KERNEL_VERSION)/build
PWD := $(shell pwd)

# Nombre del módulo
MODULE_NAME := security_module

# Archivos fuente
obj-m := $(MODULE_NAME).o
$(MODULE_NAME)-objs := security_module.o countermeasures.o detection.o

# Flags de compilación
ccflags-y := -DDEBUG -O2 -Wall -Wextra

# Objetivos de compilación
all: modules clean

modules:
	@echo "╔════════════════════════════════════════════════════╗"
	@echo "║  🛡️  SHIELD LINUX - Compilando Módulo del Kernel  ║"
	@echo "╠════════════════════════════════════════════════════╣"
	@echo "║  Versión del Kernel: $(KERNEL_VERSION)"
	@echo "║  Directorio: $(KERNEL_DIR)"
	@echo "╚════════════════════════════════════════════════════╝"
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean
	rm -f *.o *.ko *.mod.c *.mod *.order *.symvers .*.cmd
	rm -rf .tmp_versions

install:
	@echo "Instalando módulo del kernel..."
	sudo cp $(MODULE_NAME).ko /lib/modules/$(KERNEL_VERSION)/kernel/security/
	sudo depmod -a
	sudo modprobe $(MODULE_NAME)
	@echo "✅ Módulo instalado y cargado"

uninstall:
	@echo "Desinstalando módulo del kernel..."
	sudo rmmod $(MODULE_NAME) 2>/dev/null || true
	sudo rm -f /lib/modules/$(KERNEL_VERSION)/kernel/security/$(MODULE_NAME).ko
	sudo depmod -a
	@echo "✅ Módulo desinstalado"

load:
	sudo insmod $(MODULE_NAME).ko
	@echo "✅ Módulo cargado"

unload:
	sudo rmmod $(MODULE_NAME)
	@echo "✅ Módulo descargado"

status:
	@echo "Estado del módulo:"
	lsmod | grep $(MODULE_NAME) || echo "Módulo no cargado"
	dmesg | grep -i shield | tail -20

test:
	@echo "Ejecutando pruebas básicas..."
	@echo "1. Verificando dependencias..."
	@which insmod >/dev/null && echo "   ✓ insmod disponible" || echo "   ✗ insmod no encontrado"
	@which rmmod >/dev/null && echo "   ✓ rmmod disponible" || echo "   ✗ rmmod no encontrado"
	@which dmesg >/dev/null && echo "   ✓ dmesg disponible" || echo "   ✗ dmesg no encontrado"
	@echo "2. Verificando headers del kernel..."
	@test -d $(KERNEL_DIR) && echo "   ✓ Headers encontrados" || echo "   ✗ Headers no encontrados"
	@echo "3. Verificando configuración del kernel..."
	@test -f /boot/config-$(KERNEL_VERSION) && echo "   ✓ Config encontrada" || echo "   ✗ Config no encontrada"

help:
	@echo "╔════════════════════════════════════════════════════╗"
	@echo "║  🛡️  SHIELD LINUX - Makefile Help                 ║"
	@echo "╠════════════════════════════════════════════════════╣"
	@echo "║  make all       - Compilar módulo                 ║"
	@echo "║  make clean     - Limpiar archivos                ║"
	@echo "║  make install   - Instalar y cargar módulo        ║"
	@echo "║  make uninstall - Desinstalar módulo              ║"
	@echo "║  make load      - Cargar módulo                   ║"
	@echo "║  make unload    - Descargar módulo                ║"
	@echo "║  make status    - Ver estado                      ║"
	@echo "║  make test      - Ejecutar pruebas                ║"
	@echo "║  make help      - Mostrar esta ayuda              ║"
	@echo "╚════════════════════════════════════════════════════╝"

.PHONY: all modules clean install uninstall load unload status test help

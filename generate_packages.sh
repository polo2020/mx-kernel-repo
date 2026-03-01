#!/bin/bash
# Script para generar el archivo Packages.gz para repositorio APT
# Usar en la carpeta donde están los archivos .deb

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ">>> Generando Packages.gz para repositorio APT..."
echo ">>> Directorio: $SCRIPT_DIR"

# Buscar archivos .deb
DEB_COUNT=$(find . -maxdepth 1 -name "*.deb" -type f | wc -l)
echo ">>> Archivos .deb encontrados: $DEB_COUNT"

if [ "$DEB_COUNT" -eq 0 ]; then
    echo ">>> ERROR: No hay archivos .deb en este directorio"
    echo ">>> Primero debes compilar el kernel o copiar los .deb aquí"
    exit 1
fi

# Listar los .deb encontrados
echo ">>> Archivos .deb:"
find . -maxdepth 1 -name "*.deb" -type f

# Generar Packages
echo ">>> Generando archivo Packages..."
dpkg-scanpackages . /dev/null > Packages

if [ -f "Packages" ]; then
    echo ">>> Packages generado exitosamente"
    
    # Comprimir con gzip
    echo ">>> Comprimiendo con gzip..."
    gzip -9fk Packages
    
    if [ -f "Packages.gz" ]; then
        echo ">>> Packages.gz generado exitosamente"
        echo ""
        echo "=== Archivos del repositorio ==="
        ls -lh Packages Packages.gz
        echo ""
        echo "=== Contenido de Packages (primeros 20 paquetes) ==="
        head -n 100 Packages
    else
        echo ">>> ERROR: No se pudo generar Packages.gz"
        exit 1
    fi
else
    echo ">>> ERROR: No se pudo generar el archivo Packages"
    exit 1
fi

echo ""
echo ">>> ¡Repositorio APT listo!"
echo ">>> Ahora ejecuta: git add . && git commit -m 'Update packages' && git push -u origin master --force"

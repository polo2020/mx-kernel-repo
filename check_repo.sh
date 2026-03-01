#!/bin/bash
# Diagnóstico del repositorio APT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  DIAGNÓSTICO DEL REPOSITORIO APT"
echo "========================================"
echo ""

# 1. Verificar rama git
echo "1. RAMA GIT:"
if [ -d ".git" ]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "   Rama actual: $CURRENT_BRANCH"
    if [ "$CURRENT_BRANCH" != "master" ]; then
        echo "   ⚠️  ADVERTENCIA: Debería estar en 'master', no en '$CURRENT_BRANCH'"
    else
        echo "   ✓ Correcto: Está en 'master'"
    fi
else
    echo "   ✗ ERROR: No es un repositorio git"
fi
echo ""

# 2. Verificar archivos .deb
echo "2. ARCHIVOS .DEB:"
DEB_COUNT=$(find . -maxdepth 1 -name "*.deb" -type f | wc -l)
echo "   .deb en raíz: $DEB_COUNT"
if [ "$DEB_COUNT" -eq 0 ]; then
    echo "   ✗ No hay archivos .deb en el directorio actual"
    echo "   → Ejecuta repokernel.py para compilar el kernel"
    echo "   → O copia los .deb aquí manualmente"
fi
find . -maxdepth 1 -name "*.deb" -type f -exec basename {} \; | sed 's/^/      /'

# Buscar en subcarpetas
DEB_SUB=$(find . -name "*.deb" -type f | wc -l)
if [ "$DEB_SUB" -gt "$DEB_COUNT" ]; then
    echo "   .deb en total (inc. subcarpetas): $DEB_SUB"
    find . -name "*.deb" -type f | sed 's/^\./      /'
fi
echo ""

# 3. Verificar Packages.gz
echo "3. ARCHIVO Packages.gz:"
if [ -f "Packages.gz" ]; then
    SIZE=$(stat -c%s "Packages.gz")
    echo "   Tamaño: $SIZE bytes"
    echo "   Paquetes registrados:"
    zcat Packages.gz | grep "^Package:" | sed 's/^/      /'
    
    # Verificar rutas
    echo "   Rutas en Packages.gz:"
    zcat Packages.gz | grep "^Filename:" | sed 's/^/      /'
    
    # Verificar si las rutas existen
    echo "   Verificando rutas..."
    zcat Packages.gz | grep "^Filename:" | while read -r line; do
        FILEPATH=$(echo "$line" | cut -d' ' -f2)
        if [ -f "$FILEPATH" ]; then
            echo "      ✓ $FILEPATH"
        else
            echo "      ✗ $FILEPATH (NO EXISTE)"
        fi
    done
else
    echo "   ✗ No existe Packages.gz"
fi
echo ""

# 4. Verificar GitHub Pages (si hay remote)
echo "4. CONFIGURACIÓN REMOTA:"
if git remote -v | grep -q origin; then
    REMOTE_URL=$(git remote get-url origin)
    echo "   Remote: $REMOTE_URL"
    
    # Extraer usuario y repo
    USER_REPO=$(echo "$REMOTE_URL" | sed -n 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/p')
    if [ -n "$USER_REPO" ]; then
        echo "   Repositorio: $USER_REPO"
        echo "   URL GitHub Pages: https://$USER_REPO"
        echo ""
        echo "   Verifica en el navegador:"
        echo "   → https://$USER_REPO (debe mostrar archivos)"
        echo "   → https://$USER_REPO/Packages.gz (debe descargar)"
    fi
else
    echo "   ✗ No hay repositorio remoto configurado"
    echo "   → Usa repokernel.py para subir a GitHub"
fi
echo ""

# 5. Resumen y recomendaciones
echo "========================================"
echo "  RESUMEN Y RECOMENDACIONES"
echo "========================================"

PROBLEMAS=0

if [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  CAMBIAR A RAMA MASTER:"
    echo "    git checkout -b master"
    echo "    git push -u origin master --force"
    PROBLEMAS=$((PROBLEMAS+1))
fi

if [ "$DEB_COUNT" -eq 0 ]; then
    echo "⚠️  FALTA ARCHIVOS .DEB:"
    echo "    1. Ejecuta repokernel.py y compila el kernel"
    echo "    2. O copia los .deb a: $SCRIPT_DIR"
    PROBLEMAS=$((PROBLEMAS+1))
fi

if [ "$DEB_COUNT" -gt 0 ]; then
    echo "✓ REGENERAR Packages.gz:"
    echo "    ./generate_packages.sh"
    echo "    git add ."
    echo "    git commit -m 'Update packages'"
    echo "    git push -u origin master --force"
fi

if [ $PROBLEMAS -eq 0 ]; then
    echo "✓ Todo parece correcto"
    echo ""
    echo "URL para agregar en /etc/apt/sources.list.d/:"
    if [ -n "$USER_REPO" ]; then
        echo "deb [trusted=yes] https://${USER_REPO}.github.io/ ./"
    else
        echo "deb [trusted=yes] https://TU_USUARIO.github.io/TU_REPO/ ./"
    fi
fi

echo ""

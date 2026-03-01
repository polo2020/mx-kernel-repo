# Repositorio APT para Kernel Personalizado

Este repositorio contiene paquetes `.deb` del kernel Linux compilado con drivers integrados.

## Estructura del Repositorio

```
/home/jean/Música/
├── *.deb              # Paquetes del kernel compilado
├── Packages           # Índice de paquetes (texto plano)
├── Packages.gz        # Índice comprimido (requerido por APT)
├── repokernel.py      # Aplicación GUI para compilar y publicar
└── generate_packages.sh  # Script para regenerar Packages.gz
```

## Configuración en el Cliente

Para agregar este repositorio a tu sistema Debian/Ubuntu/MX Linux:

### 1. Agregar el repositorio

```bash
# Si usas GitHub Pages (recomendado)
echo "deb [trusted=yes] https://TU_USUARIO.github.io/mx-kernel-repo/ ./" | sudo tee /etc/apt/sources.list.d/custom-kernel.list
```

### 2. Actualizar e instalar

```bash
sudo apt update
sudo apt dist-upgrade
```

## Problemas Comunes

### Los paquetes no aparecen en `apt update`

**Causas posibles:**

1. **Rama incorrecta**: El repositorio debe estar en la rama `master` (no `main`)
   - Solución: El script `repokernel.py` ahora fuerza la rama `master`

2. **Packages.gz desactualizado**: 
   - Ejecuta: `./generate_packages.sh`
   - Luego: `git add . && git commit -m 'Update packages' && git push -u origin master --force`

3. **GitHub Pages no configurado**:
   - Ve a: https://github.com/TU_USUARIO/mx-kernel-repo/settings/pages
   - En "Source", selecciona: **Deploy from a branch**
   - Branch: **master** / **/(root)**
   - Guarda y espera a que se publique

4. **URL incorrecta en sources.list**:
   - Verifica: `cat /etc/apt/sources.list.d/custom-kernel.list`
   - Debe terminar con `./` (punto slash)

### Verificar Packages.gz

```bash
# Ver contenido del Packages.gz
zcat Packages.gz | head -50

# Ver cuántos paquetes hay
zcat Packages.gz | grep "^Package:" | wc -l
```

## Flujo de Trabajo

### Compilar kernel y generar .deb

1. Ejecuta `repokernel.py`
2. Usa la pestaña "Compilador e Integrador de Drivers"
3. Selecciona carpeta para guardar .deb (opcional)
4. Click en "DESCARGAR KERNEL + DRIVERS WIFI Y COMPILAR .DEB"

### Publicar en GitHub

1. En `repokernel.py`, ve a la pestaña "Publicador GitHub"
2. Selecciona la carpeta con los .deb
3. Ingresa tu usuario de GitHub
4. Click en "SUBIR KERNEL Y DRIVERS A GITHUB"

### Actualizar repositorio manualmente

```bash
cd /home/jean/Música
./generate_packages.sh
git add .
git commit -m "Actualización de paquetes"
git push -u origin master --force
```

## Comandos Útiles

```bash
# Ver paquetes disponibles
zcat Packages.gz | grep "^Package:"

# Ver versión del kernel
zcat Packages.gz | grep "^Version:"

# Ver arquitectura
zcat Packages.gz | grep "^Architecture:"

# Regenerar Packages.gz
dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz

# Forzar actualización en cliente
sudo apt update --allow-insecure-repositories
```

## Requisitos del Sistema

- Debian/Ubuntu/MX Linux
- `dpkg-dev` para generar Packages
- `git` para publicar
- GitHub con token de acceso

## Seguridad

El repositorio usa `[trusted=yes]` que omite la verificación de firmas.
Para producción, considera firmar los paquetes con `debsign`.

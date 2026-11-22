# Compilar el frontend de Canica

Para instalar el tema en tu consola, usa la [guía de tres pasos](../../docs/canica-rg35xx-h.md). Esta página explica cómo reproducir el motor y empaquetar el instalador.

## Motor ARM64 para Scarab

Necesitas Git, Python 3, Bash y Docker con soporte para contenedores Linux ARM64. Descarga la [imagen original de Scarab para la RG35XX H](https://github.com/knulli-cfw/knulli-linux/releases/download/20260511/knulli-h700-rg35xx-h-scarab-20260511.img.gz) en un directorio nuevo y abre allí una terminal Bash. Esta ruta conserva la imagen oficial en la consola. El fork de firmware proporciona el instalador y el adaptador, el fork de EmulationStation proporciona el motor y el repositorio de bundles aporta las herramientas ARM64.

```bash
(
set -eu
git init -q firmware
git -C firmware remote add origin https://github.com/eduarbo/knulli-linux.git
git -C firmware sparse-checkout set tools/canica
git -C firmware fetch --depth 1 --filter=blob:none origin d315657339ec64848a1e2d9a3a0d3849edaa4a3c
git -C firmware checkout -q --detach FETCH_HEAD
git clone --single-branch --branch canica-scarab-build https://github.com/eduarbo/batocera-emulationstation.git frontend
git -C frontend checkout --detach 8ad22d6d1fa27ec9b9dafef6f8613adb868c67d4
git -C frontend submodule update --init --recursive
git clone https://github.com/eduarbo/knulli-console-bundles.git herramientas
git -C herramientas checkout --detach 5942f8a9681d0cfcb52f4658f56d32b367bdcd69
imagen="$PWD/knulli-h700-rg35xx-h-scarab-20260511.img.gz"
python3 - "$imagen" <<'PY'
import hashlib, sys
h = hashlib.sha256()
with open(sys.argv[1], 'rb') as src:
    for data in iter(lambda: src.read(1024 * 1024), b''):
        h.update(data)
if h.hexdigest() != 'c28a96f88b07e3adb4ea76b9874cd18ae177ec216bec2dac87c68795fb81291c':
    sys.exit("La imagen no coincide con Scarab RG35XX-H 20260511")
PY
unit=herramientas/units/07-es-api-events/install
mkdir bin
DOCKER_DEFAULT_PLATFORM=linux/arm64 bash "$unit/build/build-es.sh" "$imagen" "$PWD/frontend" "$PWD/bin"
bash firmware/tools/canica/prepare-kit.sh herramientas bin/emulationstation canica-kit
)
```

Al terminar tendrás `canica-kit/payload/emulationstation` y un manifiesto. Las revisiones están fijadas. El árbol `8ad22d6` incluye cuatro parches de empaquetado de Scarab para compilar fuera de Buildroot. En una compilación completa de firmware, la receta H700 fija `87a1319` y Buildroot aplica esos cuatro parches. [Motor](https://github.com/eduarbo/batocera-emulationstation) · [Firmware](https://github.com/eduarbo/knulli-linux) · [Herramientas](https://github.com/eduarbo/knulli-console-bundles)

1. Copia `canica-kit` a `system/canica-kit` en la carpeta compartida `share`. Usa un tema de fábrica y desactiva primero cualquier otro servicio que sustituya el menú. Reinicia si cambiaste de servicio.
2. Por SSH, ejecuta `cd /userdata/system/canica-kit && bash install.sh`. Esta ruta utiliza el servicio **ES_PATCHED**. Conserva el directorio para la recuperación.
3. Si tienes el tema, copia `es-theme-canica` a `share/themes/` y selecciónalo desde los ajustes de interfaz. Para usar el adaptador incluido, ejecuta lo siguiente por SSH.

```sh
src=/userdata/system/canica-kit/resume-emulatorlauncher
(
  set -eu
  dest=/userdata/system/configs/emulationstation/resume/emulatorlauncher
  printf '%s  %s\n' e746b025d1079289d176af8645c12a129b98b0bd8acec177a4a5ec2483d73e42 "$src" | sha256sum -c -
  mkdir -p "$(dirname "$dest")"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    cmp -s "$src" "$dest" || { echo 'Se conserva el adaptador existente. Compara las versiones.'; exit 1; }
  else
    cp "$src" "$dest"
    chmod 755 "$dest"
  fi
  test -x "$dest" && cmp -s "$src" "$dest" && echo 'Adaptador listo'
)
```

Para volver, selecciona el tema anterior, ejecuta `cd /userdata/system/canica-kit && bash rollback.sh` y reinicia. Si añadiste el adaptador durante estos pasos, puedes retirarlo tras comprobar que coincide con la copia del kit.

## Empaquetar la herramienta de instalación

Desde la raíz de este repositorio, ejecuta:

```sh
python3 -B tools/canica/installer/build.py 'Instalar Canica.sh'
```

La herramienta pública incluye el instalador y el adaptador de partidas. Para preparar una copia local que incluya el tema, añade `--kit /ruta/canica-1.0.1-rc27.2-rg35xx-h.zip`. El empaquetador acepta las candidatas RC27.1 y RC27.2 identificadas por SHA-256. La licencia del arte sigue pendiente. El kit privado se conserva fuera de este repositorio.

El instalador verifica el modelo, el firmware y el ejecutable original antes de instalar. Prepara y verifica los archivos en la partición de datos y habilita Canica para el siguiente arranque. Al volver a ejecutarlo después de una interrupción, recupera la operación pendiente. Las partidas, ROM y ajustes del tema quedan fuera de la lista de escritura. La aceptación física desde una microSD limpia sigue pendiente.

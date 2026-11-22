# Canica en la RG35XX-H

Esta guía reproduce el frontend de Canica sobre **KNULLI Scarab del 11 de mayo de 2026 para la Anbernic RG35XX-H**. El fork de EmulationStation aporta las funciones de interfaz. Este fork de KNULLI fija la revisión del frontend para H700, proporciona el adaptador de partidas y prepara el instalador. Puedes usar ambos desde la computadora y conservar la imagen oficial en la microSD.

**Alcance.** Con fuentes públicas puedes reconstruir e instalar el motor. Para obtener exactamente Iris o Ámbar necesitas además la carpeta `es-theme-canica` de la candidata, que se distribuye por separado mientras se decide la licencia de su arte. Los gestos de FN, Bluetooth, sincronización, ROM, BIOS y multimedia de una instalación personal se gestionan aparte.

## 1. Compilar en la computadora

Necesitas Git, Python 3, Bash y Docker con Linux ARM64. Descarga la [imagen oficial de Scarab para RG35XX-H](https://github.com/knulli-cfw/knulli-linux/releases/tag/20260511). Trabaja en un directorio nuevo. El instalador y la imagen se comprueban en el equipo donde compilas.

```sh
git clone --depth 1 --branch canica-scarab-20260511 https://github.com/eduarbo/knulli-linux.git firmware
git clone --branch canica-scarab-build https://github.com/eduarbo/batocera-emulationstation.git frontend
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
```

El compilador prueba la carga del binario con las bibliotecas de la imagen. La rama `canica-scarab-build` incluye los cuatro parches oficiales de empaquetado. El [fork del frontend en el último de los quince commits](https://github.com/eduarbo/batocera-emulationstation/commit/87a1319b60c241ddcdc802986a86316fe5569feb) los deja a cargo de Buildroot. La compilación de una imagen completa de este fork usa esa última revisión. La ruta ensayada aquí es la compilación del frontend por separado.

## 2. Instalar en la consola

Empieza en Inicio con la consola despierta y un tema que funcione en el frontend de fábrica. Usa una copia de tu tarjeta o conserva un respaldo. En **START → Ajustes del sistema → Servicios**, comprueba que `CANICA`, `FOSFORO` y `ES_PATCHED` estén desactivados. Si acabas de desactivar uno, reinicia. El servicio de esta guía se llama **ES_PATCHED**. Quienes ya usan el servicio CANICA del kit RC27.1 pueden conservar esa instalación.

Copia la carpeta `canica-kit` a `share/system/canica-kit` mediante SMB. Desde la consola, por SSH con tu propia configuración de acceso, ejecuta lo siguiente. El instalador verifica el modelo, la versión y el hash del ejecutable original, e intenta volver a él si falla la activación.

```sh
cd /userdata/system/canica-kit
bash install.sh
```

Guarda el directorio del kit para recuperar la instalación. Para reproducir la selección de partidas de la candidata, instala también el adaptador en su ruta opcional. Estos pasos conservan un adaptador ya instalado si difiere del incluido en el kit. En ese caso, compara ambos antes de cambiar el existente.

```sh
cd /userdata/system/canica-kit
dest=/userdata/system/configs/emulationstation/resume/emulatorlauncher
mkdir -p "$(dirname "$dest")"
if [ -e "$dest" ]; then
    cmp -s "$dest" resume-emulatorlauncher || { echo "Ya existe otro adaptador. Se conserva."; exit 1; }
else
    install -m 755 resume-emulatorlauncher "$dest"
fi
test -x "$dest" && cmp -s resume-emulatorlauncher "$dest"
```

Si dispones de la candidata, copia solo `es-theme-canica` a `share/themes/`. Selecciónalo en **Ajustes de interfaz → Tema**. Elige **Iris** o **Ámbar** en los ajustes del tema. Esta ruta ya ejecuta el frontend mediante ES_PATCHED.

## 3. Comprobar y deshacer

Desde una lista con juegos, prueba **Y** y completa una palabra con **L2**. Con un juego de RetroArch que admita estados, comprueba que **A** arranca el juego y **X** abre las partidas. En una ROM de prueba, elige un estado manual reconocible y después *Nueva partida*. El adaptador interpreta `-2` como inicio sin cargar el estado automático, `-1` como carga del automático y los valores desde cero como ranuras explícitas. Los guardados internos del juego se conservan.

Para volver, selecciona tu tema anterior y sal de cualquier juego. En `/userdata/system/canica-kit` ejecuta `bash rollback.sh`. Reinicia y comprueba que abre el tema anterior. Si esta guía creó el adaptador, puedes moverlo fuera de su ruta después de comparar su contenido con `resume-emulatorlauncher`. Un adaptador preexistente pertenece a la instalación anterior.

La cualificación del motor incluye compilación ARM64, carga con las bibliotecas oficiales y comparación con las fuentes de la candidata. El arranque en frío desde una microSD física limpia sigue pendiente. Las ramas de esta guía son independientes del canal firmado de actualizaciones.

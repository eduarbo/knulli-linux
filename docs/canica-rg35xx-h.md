# Instalar Canica en una Anbernic RG35XX H

Canica RC27.1 combina las variantes **Iris** y **Ámbar** con un EmulationStation modificado para la pantalla de 640 × 480. La base probada es **KNULLI Scarab 20260511 para RG35XX H**. El paquete visual todavía se comparte por separado mientras se decide la licencia de su arte. Los tres repositorios públicos permiten reconstruir el motor.

| Tu punto de partida | Qué hacer |
| --- | --- |
| Ya usas Canica RC27.1 | Ve a [elegir y configurar la variante](#elegir-y-configurar-la-variante). |
| Tienes `canica-1.0.1-rc27.1-rg35xx-h.zip` | Sigue la [instalación con el ZIP](#instalar-con-el-zip). Incluye el frontend listo para usar. |
| Tienes solo la carpeta `es-theme-canica`, o quieres construir el motor | Sigue la [instalación desde fuentes](#instalar-desde-fuentes). Sin la carpeta puedes probar el motor con un tema compatible que ya tengas. |

## Preparar la consola

1. Comprueba el modelo en la carcasa y la versión de KNULLI en la información del sistema. Si ya usas Scarab 20260511 en la RG35XX H, conserva tu instalación. Para empezar desde cero, graba la imagen **RG35XX H** en una microSD de repuesto, colócala en **TF1/INT** y deja que termine el primer arranque. Grabar una imagen borra el contenido de la tarjeta elegida. [Imagen oficial para este modelo](https://github.com/knulli-cfw/knulli-linux/releases/download/20260511/knulli-h700-rg35xx-h-scarab-20260511.img.gz) · [Instalar KNULLI](https://knulli.org/play/install/)
2. Guarda una copia de tus partidas y ajustes antes de cambiar el frontend. Conecta la consola y la computadora a la misma red. En **START → Ajustes del sistema → Servicios**, activa **SAMBA**. En Finder abre `smb://KNULLI/share`. En el Explorador de Windows abre `\\KNULLI\share`. Si el nombre no responde, usa la IP mostrada por KNULLI. La raíz de esa ventana corresponde a `/userdata` en la consola. [Transferencia por red](https://knulli.org/play/add-games/network-transfer/)
3. Selecciona primero un tema de fábrica que puedas reconocer al volver. Si vas a cambiar de instalador, desactiva el servicio anterior (**CANICA**, **FOSFORO** o **ES_PATCHED**) y reinicia. Cada ruta de esta guía utiliza un solo servicio. Las ROM, BIOS, imágenes y vídeos de tu biblioteca se gestionan por separado. [Añadir juegos](https://knulli.org/play/add-games/)

## Instalar con el ZIP

1. Usa el ZIP **`canica-1.0.1-rc27.1-rg35xx-h.zip`** que recibiste con la candidata. Comprueba que su SHA-256 sea `113e8b662fee7083ecd2383600ca6f4cfd7383065088f9def055383be6605828`. En macOS usa `shasum -a 256 ARCHIVO`, en Linux `sha256sum ARCHIVO` y en PowerShell `Get-FileHash ARCHIVO`. Extráelo en la computadora cuando coincida.
2. Abre la carpeta `share` extraída y copia por separado estos tres elementos. Los destinos de la tabla son **relativos a la ventana de red `share`**. Crea `services` si falta y respalda cualquier elemento del mismo nombre antes de sustituirlo. Copia solo las carpetas indicadas para conservar el resto de `system`.

   | Elemento dentro del ZIP | Destino dentro de la carpeta compartida |
   | --- | --- |
   | Carpeta `share/themes/es-theme-canica` | `themes/es-theme-canica` |
   | Carpeta `share/system/canica` | `system/canica` |
   | Archivo `share/system/services/canica` | `system/services/canica` |

3. En Inicio, con la consola despierta, activa **START → Ajustes del sistema → Servicios → CANICA** y sal del menú. Si el frontend sigue pendiente de arranque, reinicia EmulationStation desde **Salir**. Por SSH puedes ejecutar `knulli-services status canica`. La respuesta **Canica en ejecución** confirma el relevo. El servicio verifica el modelo, la versión y la integridad de los archivos.
4. [Elige Iris o Ámbar](#elegir-y-configurar-la-variante). Para replicar también cómo se elige entre nueva partida, autoguardado y ranura, [instala el adaptador](#adaptador-de-partidas).

Si ya tienes **Fósforo RC25 o RC26** en este modelo y quieres conservar su frontend, copia únicamente `themes/es-theme-canica` y selecciónalo. Para heredar tus preferencias, con el tema de fábrica activo, duplica `system/configs/emulationstation/themesettings/es-theme-fosforo.cfg` como `es-theme-canica.cfg` si el destino aún no existe. Puedes seguir usando el servicio FOSFORO de esa instalación.

## Elegir y configurar la variante

En **START → Ajustes de la interfaz de usuario → Tema**, selecciona **es-theme-canica**. Abre **Ajustes del tema → Variante** y elige **Iris** (lavanda) o **Ámbar** (dorado). Puedes cambiar entre las dos desde ese menú. [Ajustes de temas de KNULLI](https://knulli.org/configure/customization/themes/)

| Ajuste | Qué verás |
| --- | --- |
| Tarjetas de juegos | Grandes o compactas. Con la cuadrícula en automático, PICO-8 usa tres columnas. |
| Vídeo en la tarjeta seleccionada | Reproducir el vídeo de la ficha o conservar la imagen. |
| Imagen de la ficha | Dar prioridad a la carátula o a la captura, según la biblioteca. |
| Vistas previas de consolas | Mostrar vistas animadas o imágenes fijas. |

Para comprobarlo, abre una consola con juegos. **L1/R1** cambian de consola, **L2/R2** pasan de página, **Y** abre el teclado y **L2** acepta la primera palabra sugerida dentro del teclado. En la lista **A** inicia el juego y **X** abre sus partidas. Un vídeo o una carátula aparecerán cuando ese juego tenga el recurso en su ficha. El atajo FN+A, el emparejamiento Bluetooth y la sincronización con otro equipo son ajustes independientes de esta instalación.

## Instalar desde fuentes

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

1. Copia `canica-kit` a `system/canica-kit` dentro de la carpeta de red `share`. En una sesión SSH de la consola ejecuta `cd /userdata/system/canica-kit && bash install.sh`. El servicio de esta ruta se llama **ES_PATCHED**. Conserva el kit para la recuperación. [Acceso por SSH en KNULLI](https://knulli.org/configure/ssh/)
2. Para usar Iris o Ámbar, copia la carpeta visual a `themes/es-theme-canica` y sigue [los ajustes de la variante](#elegir-y-configurar-la-variante). Esta ruta ya incorpora el frontend mediante **ES_PATCHED**.
3. El archivo `system/canica-kit/resume-emulatorlauncher` permite instalar el [adaptador de partidas](#adaptador-de-partidas).

## Adaptador de partidas

Para reproducir el comportamiento de la candidata con juegos de RetroArch que admiten estados, usa el adaptador público. Si **ya lo tenías instalado**, conserva tu copia hasta comparar su contenido. En la ruta del **ZIP**, guarda el [adaptador fijado para RC27.1](https://raw.githubusercontent.com/eduarbo/knulli-linux/d315657339ec64848a1e2d9a3a0d3849edaa4a3c/tools/canica/resume/emulatorlauncher) como `canica-resume-candidate` dentro de `share/system` y usa la primera línea siguiente. En la ruta **desde fuentes**, sustituye esa primera línea por `src=/userdata/system/canica-kit/resume-emulatorlauncher`. Ejecuta el bloque en una sesión **SSH de la consola**.

```sh
src=/userdata/system/canica-resume-candidate
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

Desde **X → Partidas**, prueba una ranura reconocible y luego **Nueva partida** con una ROM de prueba. El adaptador distingue el inicio sin cargar un estado automático, la carga del autoguardado y la elección de una ranura concreta. Los guardados internos del juego siguen disponibles.

## Volver al menú anterior

- **Con el ZIP:** elige tu tema anterior, desactiva **CANICA** en Servicios y reinicia. Para retirar el paquete, mueve fuera de sus rutas únicamente los tres elementos indicados en la tabla. Si el menú no arranca, con la consola apagada retira de la tarjeta de datos `system/services/canica` y `themes/es-theme-canica`. Conserva las ROM y partidas.
- **Desde fuentes:** elige el tema anterior, sal de cualquier juego y ejecuta por SSH `cd /userdata/system/canica-kit && bash rollback.sh`. Reinicia y comprueba que vuelve el frontend de fábrica.
- **Adaptador:** si lo instalaste durante estos pasos, puedes moverlo fuera de `system/configs/emulationstation/resume/` después de comprobar que coincide con el archivo que copiaste. Un adaptador que ya estaba presente forma parte de la instalación anterior.

**Si ves el tema pero faltan columnas o sugerencias**, comprueba que elegiste la variante y que el servicio correspondiente a tu ruta está activo con la versión exacta de Scarab. Si el tema no aparece en la lista, comprueba que `share/themes/es-theme-canica/theme.xml` existe y que no hay una carpeta `share` duplicada. Si vas a actualizar KNULLI, vuelve primero al menú anterior. Se probaron la carga ARM64 con las bibliotecas de Scarab y la recuperación en laboratorio. Sigue pendiente el arranque en frío desde una microSD física limpia.

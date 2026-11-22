# Replicar Canica en una RG35XX H

Esta es la configuración de mi Anbernic RG35XX H. Usa KNULLI Scarab del **11 de mayo de 2026** como base, con **mi fork de EmulationStation**, el tema **Canica** y el **adaptador de partidas**. La combinación con esos componentes es la que mantengo. El paquete está en fase de candidata.

[Ver las demostraciones grabadas en la consola](canica-en-accion.md)

## Instalar desde la consola

1. **Consigue el kit RC30 para RG35XX H.** Si ya tienes el archivo **Instalar Canica.sh** con el kit integrado (unos 5,2 MB), sólo necesitas ese archivo. Si recibiste **canica-1.0.1-rc30-rg35xx-h.zip**, conserva su nombre y descarga el instalador ligero para acompañarlo. El tema y su arte todavía se entregan por separado de los repositorios públicos. [Descargar el instalador ligero](https://raw.githubusercontent.com/eduarbo/knulli-linux/main/tools/canica/Instalar%20Canica.sh)
2. **Copia los archivos en Herramientas.** Abre el recurso compartido de la consola. En Finder, **Ir → Conectarse al servidor →** `smb://KNULLI/share`. En el Explorador de Windows, abre `\\KNULLI\share`. Dentro de **roms/tools** coloca el instalador completo, o el ligero junto al ZIP sin extraer. También puedes copiarlos desde la partición de datos de la tarjeta. [Transferencia en KNULLI](https://knulli.org/play/add-games/network-transfer/)
3. **Abre Herramientas → Instalar Canica** y pulsa **A**. Si la herramienta aún no aparece, abre **START → Ajustes de juegos → Actualizar listas de juegos**. El instalador comprueba el modelo, la versión del firmware y la integridad del kit. Si detecta otro servicio que controla el menú o un archivo personalizado en conflicto, muestra cuál es y conserva el archivo. Espera el mensaje **Canica está listo** y reinicia al terminar tu partida.
4. **Selecciona el tema.** En **START → Ajustes de la interfaz de usuario → Tema**, elige **es-theme-canica**. En **Ajustes del tema → Variante**, elige **Iris** o **Ámbar**. Deja **Tamaño pred. de cuadrícula** en **Automático** para usar la distribución de cada sistema.
5. **Comprueba la instalación.** Abre una consola con juegos. **Y** debe mostrar un teclado con tarjetas de palabras. **X** debe abrir Partidas y **A** debe iniciar el juego. Si tienes SSH, `knulli-services status canica` debe responder **Canica en ejecución**.

Para una tarjeta nueva, instala primero la imagen Scarab de la **RG35XX H**. La instalación del kit en este modelo se probó sobre una tarjeta en uso. Queda pendiente su primer arranque en una microSD recién preparada. [Imagen base de la RG35XX H](https://github.com/knulli-cfw/knulli-linux/releases/download/20260511/knulli-h700-rg35xx-h-scarab-20260511.img.gz) · [Preparar la tarjeta](https://knulli.org/play/install/)

## Fondos y partidas

El instalador prepara las capturas de los juegos con la proporción de su sistema. Game Boy usa cuatro tonos verdes, Arcade Tate conserva la orientación vertical y las tarjetas de juegos de DS conservan ambas pantallas cuando están juntas. Los originales siguen en tu biblioteca. Después de añadir medios, vuelve a ejecutar el instalador para actualizar las capturas que cambiaron. Para los vídeos de los juegos, selecciona **Ajustes del tema → Vídeo en la tarjeta seleccionada → Reproducir**.

Con **A**, el adaptador compara el guardado automático y las ranuras compatibles del juego. Si la partida interna cambió por sincronización, preserva ese avance. Con **X**, tú eliges la ranura. Algunos sistemas, como PICO-8, guardan dentro del propio juego.

## Qué instala cada fork

| Componente | Procedencia y función |
| --- | --- |
| Menú | El binario ARM64 procede de la revisión `4215ca1` del fork de EmulationStation. Ejecuta las categorías, los atajos, las tarjetas de búsqueda y las vistas previas. [Fuentes del frontend](https://github.com/eduarbo/batocera-emulationstation/tree/4215ca1eb833688a7b34f8f0b2c026584b9110b9) |
| Partidas y firmware | El fork de KNULLI aporta la receta para H700, el instalador y el adaptador que comunica la ranura seleccionada al lanzador de juegos. [Instalador y adaptador](../tools/canica/README.md) |
| Compilación y recuperación | El repositorio de herramientas aporta las bibliotecas y scripts para construir el motor en ARM64 y recuperar el menú de fábrica. El kit integrado activa el servicio **CANICA**. La instalación manual desde fuentes emplea **ES_PATCHED**. Activa sólo el de tu método. [Herramientas fijadas](https://github.com/eduarbo/knulli-console-bundles/tree/5942f8a9681d0cfcb52f4658f56d32b367bdcd69) |

Si ya tienes **KNULLI Scarab** en esa consola, el instalador conserva su sistema base y añade el frontend en la partición de datos. Compilar el firmware completo es opcional. El catálogo, las carátulas, los vídeos y las partidas provienen de tu tarjeta. [Compilar los forks y el adaptador](../tools/canica/README.md)

## Volver al menú anterior

Selecciona primero el tema que usabas. En **Ajustes del sistema → Servicios**, desactiva **CANICA** y reinicia. Tu biblioteca y los archivos instalados permanecen en la tarjeta. Si la instalación se interrumpió, vuelve a abrir el instalador. El resultado queda en `system/logs/canica-instalacion.txt` dentro de `share`. Para una instalación manual con **ES_PATCHED**, usa la recuperación de su guía de compilación.

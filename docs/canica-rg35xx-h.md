# Instalar Canica en una RG35XX H

Necesitas una **Anbernic RG35XX H con KNULLI Scarab del 11 de mayo de 2026**. Si ya tienes **Instalar Canica.sh** con el tema incluido, es el único archivo que necesitas. Si recibiste el ZIP de Canica RC27.1 o RC27.2, descarga el instalador público y pon ambos archivos juntos. [Descargar Instalar Canica.sh](https://raw.githubusercontent.com/eduarbo/knulli-linux/main/tools/canica/Instalar%20Canica.sh)

1. **Copia** el instalador a `share/roms/tools` en la consola. Si usas el instalador público, copia allí también el ZIP para RG35XX H **sin descomprimirlo**. Puedes hacerlo desde la tarjeta o por red. En Finder abre `smb://KNULLI/share` y en Windows `\\KNULLI\share`. [Conectar por red](https://knulli.org/play/add-games/network-transfer/)
2. **Abre Herramientas → Instalar Canica** y pulsa **A**. Cuando aparezca «Canica está listo», reinicia la consola. Si la herramienta aún no aparece, ve a **START → Ajustes de juegos → Actualizar listas de juegos**.
3. **Elige el tema** en **START → Ajustes de la interfaz de usuario → Tema → es-theme-canica**. En **Ajustes del tema → Variante** elige **Iris** o **Ámbar**.

Para comprobarlo, entra en una consola con juegos. **Y** abre la búsqueda, **X** muestra las partidas y **A** inicia el juego.

**Para volver al menú anterior**, elige tu tema anterior, desactiva **CANICA** en **Ajustes del sistema → Servicios** y reinicia. Si hubo un corte durante la instalación, vuelve a abrir el instalador. El último resultado queda en `share/system/logs/canica-instalacion.txt`.

Para una tarjeta nueva, [Instalar Scarab](https://knulli.org/play/install/) · [Imagen exacta para RG35XX H](https://github.com/knulli-cfw/knulli-linux/releases/download/20260511/knulli-h700-rg35xx-h-scarab-20260511.img.gz). Para desarrollo, consulta la [compilación desde fuentes](../tools/canica/README.md).

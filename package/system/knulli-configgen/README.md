## Directory navigation

 - `configgen` Go here for the generators themselves.
 - `configs` A set of default settings, for both global and per-platform. If defining a new emulator/system, it will need to be defined in [configgen-defaults](https://github.com/batocera-linux/batocera.linux/blob/master/package/batocera/core/batocera-configgen/configs/configgen-defaults.yml).
   A system can also list per-game defaults under `games`, keyed by the game title without its `(...)`/`[...]` tags and matched without regard to case, for example `"GoldenEye 007": { core: mupen64plus-next }`. They apply on top of the system defaults; anything the user sets in `knulli.conf` still takes precedence.
 - `datainit` Some extraneous files required for emulators.

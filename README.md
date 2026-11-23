# Canica for the Anbernic RG35XX H

A handheld game library with in-card gameplay videos, D-pad word completion and visual save slots. Recorded on my RG35XX H.

[![Advance Wars on Game Boy Advance in Amber and Iris](docs/media/canica/previews/home.gif)](docs/media/canica/iris-ambar.gif)

*Advance Wars on Game Boy Advance.* The recording switches between Amber and Iris, large and compact cards, and still and moving previews. **A** plays, **X** picks a save and **Y** searches.

[Install Canica RC30](docs/canica-rg35xx-h.md) · [Watch all 32 demos](docs/canica-en-accion.md) · [Bring your own ROMs](docs/canica-rg35xx-h.md#bring-your-own-roms) · [My RomM and TV setup](docs/canica-rg35xx-h.md#from-the-handheld-to-a-tv-with-romm)

## From Game Boy to the arcade

[![Browse Game Boy, Game Boy Advance and Nintendo DS shelves](docs/media/canica/previews/consolas.gif)](docs/media/canica/consolas.gif) [![Battle Garegga playing vertically inside its arcade card](docs/media/canica/previews/arcade-tate.gif)](docs/media/canica/arcade-tate.gif)

Game Boy screenshots keep their green LCD palette. *Battle Garegga* stays upright in its portrait card. **L1 / R1** move from one console to the next without backing out. Open either clip to see the original 640 × 480 screen.

## Find a game. Pick a save.

[![Complete a search word using the shoulder buttons](docs/media/canica/previews/buscar.gif)](docs/media/canica/buscar.gif) [![Choose an earlier Adventure Island III save and resume it](docs/media/canica/previews/elegir-ranura.gif)](docs/media/canica/elegir-ranura.gif)

**Y** opens a keyboard that completes words from your library. **X** opens dated save slots with screenshots. In the second clip, choosing slot 0 takes *Adventure Island III* back to that save even though a newer autosave exists.

## Rediscover a favorite

[![The Simpsons rotating through Chef’s Picks](docs/media/canica/previews/chef.gif)](docs/media/canica/chef.gif) [![Dragon Ball: Advanced Adventure in the fullscreen media viewer](docs/media/canica/previews/visor.gif)](docs/media/canica/visor.gif)

Chef’s Picks rotates through favorites across systems, including *The Simpsons* in this clip. Open the media viewer for a full-screen look at *Dragon Ball: Advanced Adventure*.

## From my handheld to my TVs

I sync my handheld library and saves with RomM. My custom TV launchers include a game browser backed by the same library, so I can pick a game on the couch and carry on from a compatible in-game save. Canica runs locally on the handheld. The RomM sync client and TV launchers are separate parts of my setup. [How the handoff works](docs/canica-rg35xx-h.md#from-the-handheld-to-a-tv-with-romm)

## What you need

Canica RC30 pairs the May 11, 2026 KNULLI Scarab image for the **RG35XX H** with my EmulationStation fork, save adapter and theme. Get the theme kit separately; its artwork license is pending. The public installer accepts that kit. The guide covers setup, controls and how to restore the original menu. [Install and verify](docs/canica-rg35xx-h.md) · [Build the frontend](tools/canica/README.md)

This firmware fork carries the H700 integration and save adapter. The [frontend fork](https://github.com/eduarbo/batocera-emulationstation) implements the cards, navigation and search. The [build tools](https://github.com/eduarbo/knulli-console-bundles) provide the ARM64 build and recovery scripts. At `ff02e3d` the firmware had nine commits beyond Scarab, covering suspend, battery, DraStic, per-game settings and Wi-Fi. At integration revision `f6a4e9e`, the difference was 12 commits across 18 files. [Pinned firmware comparison](https://github.com/eduarbo/knulli-linux/compare/c1c7de479e56691c6665723046d9f25500e5ee74...f6a4e9ed39c6cc49c6f5eecbcf08c22a6020ff3a) · [Integration PR](https://github.com/eduarbo/knulli-linux/pull/1)

## Upstream KNULLI

[![Activity](https://img.shields.io/github/commit-activity/m/knulli-cfw/distribution)](https://github.com/knulli-cfw/distribution)
[![PR](https://img.shields.io/github/issues-pr-closed/knulli-cfw/distribution)](https://github.com/knulli-cfw/distribution)
[![Stars](https://img.shields.io/github/stars/knulli-cfw?style=social)](https://github.com/knulli-cfw/distribution)
[![Forks](https://img.shields.io/github/forks/knulli-cfw/distribution?style=social)](https://github.com/knulli-cfw/distribution)
[![Website](https://img.shields.io/website?down_color=red&down_message=down&up_color=green&up_message=up&url=https%3A%2F%2Fwww.knulli.org)](https://knulli.org)
[![Discord Server](https://img.shields.io/discord/357518249883205632.svg)](https://discord.gg/HXPS3DAeeB)

## :video_game::penguin: Knulli CFW :video_game::penguin:
Knulli CFW is a fork of the open-source and completely free retro-gaming distribution batocera that can be copied to an SD card with the aim of improving many of the emulation handhelds on the market that usually ship with incomplete and often non GPL compliant software. It supports [many emulators and game engines](https://www.batocera.org/compatibility.php) out of the box. 

## Get information on the project

 - :globe_with_meridians: Browse our [website](https://knulli.org) for general information (Downloads coming soon)
 - :memo: Documentation is available on our [wiki](https://knulli.org) and frequently updated
 - :speech_balloon: Discuss any topic with the community on our [Discord Server](https://discord.gg/HXPS3DAeeB)

## Do you need help with KNULLI?

 - :sos: The most effective way is to join our [Discord Server](https://discord.gg/HXPS3DAeeB) and go to the \#questions channel

## How can you help Knulli?

 - :wrench: If you want to help with development, [we accept PRs](https://makeapullrequest.com/) -- anyone is welcome, we embrace the [Bazaar development principles](https://en.wikipedia.org/wiki/The_Cathedral_and_the_Bazaar)

## Directory navigation

 - `board` Platform-specific build configuration. This is where to include special patches/configuration files needed to have particular components work on a particular platform. It is instead encouraged to apply patches at the location of the package itself, but this may not always be possible.
 - `buildroot` Buildroot, the tool used to create the final compiled images. For newcomers, you can safely ignore this folder. Compilation instructions can be found [on the wiki](https://wiki.batocera.org/compile_knulli.linux).
 - `configs` Build flags, which define what components will be built with your image depending on your chose architecture. If you're trying to port Batocera to a new architecture (device, platform, new bit mode, etc.) this is the file you'll need to edit. More information on [the build configuration section on the buildroot compiling page](https://wiki.batocera.org/knulli.linux_buildroot_modifications#define_your_configuration).
 - `package` The "meat and potatoes" of Batocera. This is where the majority of emulator data, config generators, core packages, system utilities, etc. all go into. This is the friendliest place to start dev-work for new devs, as most of it is handled by Python and Makefile.
 - `scripts` Various miscellanous scripts that handle aspects external to Batocera, such as the report data sent to the [compatibility page](https://batocera.org/compatibility.php) or info about the Bezel Project.

A cheatsheet of notable files/folders can be found [on the wiki](https://wiki.batocera.org/notable_files).

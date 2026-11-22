"""Offline installer launched from the RG35XX H Tools list."""
from contextlib import contextmanager
import fcntl
import hashlib
import io
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from urllib import error, request
from zipfile import BadZipFile, ZipFile

MODEL = 'Anbernic RG35XX-H'
FIRMWARE = 'scarab 2026/05/11 00:09'
STOCK = 'd02c1f349952151ba5cd5b67125e848e95279483230d1582203efd44cf37af64'
THEME = 'themes/es-theme-canica'
ENGINE = 'system/canica'
SERVICE = 'system/services/canica'
ADAPTER = 'system/configs/emulationstation/resume/emulatorlauncher'
ADAPTER_SHA = '4e36929f93928371f3d151fa7cd71b3198b9246b2fd74a0bd0d5870874613b8e'
PACKAGES = {
    'canica-1.0.1-rc30-rg35xx-h.zip': '10005c911c49fa46312f734874ef78148dec1b8e4b9f829987bc8c98e169f727',
    'canica-1.0.1-rc29.1-rg35xx-h.zip': '5f6e44e0ef228a0d2062b3cc2555730c44d5e3a331e66160d0530fe8d4e11504',
    'canica-1.0.1-rc29-rg35xx-h.zip': 'e7a76df26626d5f1b36da884bb83e697d0202424a8b68b88419cf9d045e2f50b',
    'canica-1.0.1-rc28-rg35xx-h.zip': 'fff74d3af75fd613954c5e16ae69244bf07501976c3636a7fab74604144d6951',
    'canica-1.0.1-rc27.2-rg35xx-h.zip': 'c1133da6a93a8b94f8126fea8f43d69cdcbde5a4976e4497f85e1b20194b8021',
    'canica-1.0.1-rc27.1-rg35xx-h.zip': '113e8b662fee7083ecd2383600ca6f4cfd7383065088f9def055383be6605828',
}
# An upgrade may replace an untouched file from a known earlier kit.
# Each destination digest is paired with its permitted predecessors.
PREVIOUS = {
    # RC30 upgrades from sealed earlier kits.
    ('system/canica/SHA256SUMS',
     '2b311fdffadd2e464101d2bbf40cc4fc2548f1aa62bc239bac68a3dcbf050107'): {
        '3375eb0db2b58c67df329805dadb27cc82489a11781838e9c1638bf625ac2015',
        '575482d4cdfe578cc7660e4a093f57a2e1c3004684d963f30e3852974708f7a1',
        '63caf5e4d9f8e95d77631cc56b7a404d951f8e94d0578f31d91f2294c25741a2',
        '71d4f6ae6249c63941efa237cb63f068dd5a0ecdcbad10d2be0675cdec27429c',
        'a04d84433887d06e3d0bec8d451a0363a2b7744c380c616091012ef52681f62c',
    },
    ('system/canica/bin/emulationstation',
     'e01811482186db924a2c855f81084c800d6782621445b43a2cdc2600ba812c4f'): {
        '39235ef32ef9aa0ee3ec6274ab0877346cc5594446e2535f4e80cd41661f8314',
    },
    ('system/services/canica',
     'ffdf96c6d9cb19f2d0845d178270b617949536ec88641725ec3134d214c0c4f1'): {
        '27928228e36e2db417cf46ac11d674580a7c12efa95ed7e728c986e1cbbc8794',
        '2d834b0414ff1fca8378a617ac6a2b50f8589ea3dec5baa573d48900e148c7cd',
        '390bc1dcc4e1e4f0875d30c3c56c8d61fc06d7dcc05e566ecb89bd4bb61f2993',
        '71eca699c971d070e33cb97a9ae1fee11829f6a8c6340cf240b707271b3475c8',
        'ffafa4c743a60732b553a376247e158f4ae65be8a063c7899dcd296d04051dc2',
    },
    ('themes/es-theme-canica/README.md',
     '20b609bb34f7975494483d7b94e855043d96821126d1b25317a546f2ec36d27a'): {
        '1acd949b55259b54399d41d64bc4a1828de7120acf3bcaa12632011d60945631',
        '32bf92075794123dc9c73349a46a93c0ad3958a6e8d57f50ebd6008d023adce3',
        '403305aa227666b4b589cd0e6bcfcae6fd2cefc0c27c12a0f5f82a445df69766',
        '7080f0ecdc7a1ab968b5159eeb2efdfa792fbc5ee81da43e446178824f25e398',
        'ffdc7da73ac53f78922b132c9428d2155f08093fbbf5c1307003bcb17a46deea',
    },
    ('themes/es-theme-canica/bindings.xml',
     'f74f7135e30cf585d96e400a615ede64667b0f202584882786cf4fd9bd2c197f'): {
        '3e3693e568a04c22fe55092d7bf824005253bf7adc2d612ca6ba64a8c0f3772a',
        'e4a254f171403edd55c557f0392f9f6f03425b6517d8c31b8e5eac549207e9bb',
    },
    ('themes/es-theme-canica/card_screens.py',
     '8bb64bfbb189ee52a6233f39e70873d2c01f2c0e111d25e2d93e73b77f6cab12'): {
        '34e5b8b3b02e7dbf96060c45e0acfd600ed04649915af3f5e433c3633e7913b7',
    },
    ('themes/es-theme-canica/theme.xml',
     '020c13cbd8de6c67e46a412fb62b208bcb9128b64b6e8f80836b7917c4b1ef7f'): {
        '1c42716796064bfbca89312a2650211f5645a1f2370675eedad86b3d81f4f9f7',
        '9c3783ab4cf9a0c8487932fd3ff8adcc2efa6d0e55c3a91f9c6792088906b546',
        'e55d1a85b4127318ef2f257c0850817b46b2ccfd8ad177b9303e69e8c92ff33e',
        'f6fcec2b712284c21a107c2694ac0b2f45879fdf577dd357d5f7dcb625fdf142',
    },
    # RC29.1 upgrades
    ('system/canica/SHA256SUMS',
     '3375eb0db2b58c67df329805dadb27cc82489a11781838e9c1638bf625ac2015'): {
        '575482d4cdfe578cc7660e4a093f57a2e1c3004684d963f30e3852974708f7a1',
        '63caf5e4d9f8e95d77631cc56b7a404d951f8e94d0578f31d91f2294c25741a2',
        '71d4f6ae6249c63941efa237cb63f068dd5a0ecdcbad10d2be0675cdec27429c',
        'a04d84433887d06e3d0bec8d451a0363a2b7744c380c616091012ef52681f62c',
    },
    ('system/services/canica',
     '2d834b0414ff1fca8378a617ac6a2b50f8589ea3dec5baa573d48900e148c7cd'): {
        '27928228e36e2db417cf46ac11d674580a7c12efa95ed7e728c986e1cbbc8794',
        '390bc1dcc4e1e4f0875d30c3c56c8d61fc06d7dcc05e566ecb89bd4bb61f2993',
        '71eca699c971d070e33cb97a9ae1fee11829f6a8c6340cf240b707271b3475c8',
        'ffafa4c743a60732b553a376247e158f4ae65be8a063c7899dcd296d04051dc2',
    },
    ('themes/es-theme-canica/README.md',
     '403305aa227666b4b589cd0e6bcfcae6fd2cefc0c27c12a0f5f82a445df69766'): {
        '1acd949b55259b54399d41d64bc4a1828de7120acf3bcaa12632011d60945631',
        '32bf92075794123dc9c73349a46a93c0ad3958a6e8d57f50ebd6008d023adce3',
        '7080f0ecdc7a1ab968b5159eeb2efdfa792fbc5ee81da43e446178824f25e398',
        'ffdc7da73ac53f78922b132c9428d2155f08093fbbf5c1307003bcb17a46deea',
    },
    ('themes/es-theme-canica/theme.xml',
     'e55d1a85b4127318ef2f257c0850817b46b2ccfd8ad177b9303e69e8c92ff33e'): {
        '1c42716796064bfbca89312a2650211f5645a1f2370675eedad86b3d81f4f9f7',
        '9c3783ab4cf9a0c8487932fd3ff8adcc2efa6d0e55c3a91f9c6792088906b546',
        'f6fcec2b712284c21a107c2694ac0b2f45879fdf577dd357d5f7dcb625fdf142',
    },
    # RC29 predecessors from the sealed RC27.1, RC27.2 and RC28 kits.
    ('system/canica/SHA256SUMS',
     '575482d4cdfe578cc7660e4a093f57a2e1c3004684d963f30e3852974708f7a1'): {
        '63caf5e4d9f8e95d77631cc56b7a404d951f8e94d0578f31d91f2294c25741a2',
        '71d4f6ae6249c63941efa237cb63f068dd5a0ecdcbad10d2be0675cdec27429c',
        'a04d84433887d06e3d0bec8d451a0363a2b7744c380c616091012ef52681f62c',
    },
    ('system/services/canica',
     'ffafa4c743a60732b553a376247e158f4ae65be8a063c7899dcd296d04051dc2'): {
        '27928228e36e2db417cf46ac11d674580a7c12efa95ed7e728c986e1cbbc8794',
        '390bc1dcc4e1e4f0875d30c3c56c8d61fc06d7dcc05e566ecb89bd4bb61f2993',
        '71eca699c971d070e33cb97a9ae1fee11829f6a8c6340cf240b707271b3475c8',
    },
    ('themes/es-theme-canica/Preparar fondos de Canica.sh',
     'c5a3bf13612d8d505063135c875a7cd2cd09f8bb8d3625096ffaa59643ff79ab'): {
        '01c87df60a66aa18fa9ccc27410cfe790e3410f78c70433783be099ad7c45b85',
    },
    ('themes/es-theme-canica/README.md',
     '7080f0ecdc7a1ab968b5159eeb2efdfa792fbc5ee81da43e446178824f25e398'): {
        '1acd949b55259b54399d41d64bc4a1828de7120acf3bcaa12632011d60945631',
        '32bf92075794123dc9c73349a46a93c0ad3958a6e8d57f50ebd6008d023adce3',
        'ffdc7da73ac53f78922b132c9428d2155f08093fbbf5c1307003bcb17a46deea',
    },
    ('themes/es-theme-canica/bindings.xml',
     '3e3693e568a04c22fe55092d7bf824005253bf7adc2d612ca6ba64a8c0f3772a'): {
        'e4a254f171403edd55c557f0392f9f6f03425b6517d8c31b8e5eac549207e9bb',
    },
    ('themes/es-theme-canica/theme.xml',
     '9c3783ab4cf9a0c8487932fd3ff8adcc2efa6d0e55c3a91f9c6792088906b546'): {
        '1c42716796064bfbca89312a2650211f5645a1f2370675eedad86b3d81f4f9f7',
        'f6fcec2b712284c21a107c2694ac0b2f45879fdf577dd357d5f7dcb625fdf142',
    },
    (ADAPTER, ADAPTER_SHA): {"e746b025d1079289d176af8645c12a129b98b0bd8acec177a4a5ec2483d73e42"},
    ('system/canica/SHA256SUMS',
     '71d4f6ae6249c63941efa237cb63f068dd5a0ecdcbad10d2be0675cdec27429c'): {
        '63caf5e4d9f8e95d77631cc56b7a404d951f8e94d0578f31d91f2294c25741a2',
        'a04d84433887d06e3d0bec8d451a0363a2b7744c380c616091012ef52681f62c',
    },
    ('system/canica/SHA256SUMS',
     'a04d84433887d06e3d0bec8d451a0363a2b7744c380c616091012ef52681f62c'): {
        '63caf5e4d9f8e95d77631cc56b7a404d951f8e94d0578f31d91f2294c25741a2',
    },
    ('system/services/canica',
     '390bc1dcc4e1e4f0875d30c3c56c8d61fc06d7dcc05e566ecb89bd4bb61f2993'): {
        '27928228e36e2db417cf46ac11d674580a7c12efa95ed7e728c986e1cbbc8794',
    },
    ('system/services/canica',
     '71eca699c971d070e33cb97a9ae1fee11829f6a8c6340cf240b707271b3475c8'): {
        '27928228e36e2db417cf46ac11d674580a7c12efa95ed7e728c986e1cbbc8794',
        '390bc1dcc4e1e4f0875d30c3c56c8d61fc06d7dcc05e566ecb89bd4bb61f2993',
    },
    ('themes/es-theme-canica/README.md',
     '1acd949b55259b54399d41d64bc4a1828de7120acf3bcaa12632011d60945631'): {
        '32bf92075794123dc9c73349a46a93c0ad3958a6e8d57f50ebd6008d023adce3',
    },
    ('themes/es-theme-canica/README.md',
     'ffdc7da73ac53f78922b132c9428d2155f08093fbbf5c1307003bcb17a46deea'): {
        '1acd949b55259b54399d41d64bc4a1828de7120acf3bcaa12632011d60945631',
        '32bf92075794123dc9c73349a46a93c0ad3958a6e8d57f50ebd6008d023adce3',
    },
    ('themes/es-theme-canica/theme.xml',
     'f6fcec2b712284c21a107c2694ac0b2f45879fdf577dd357d5f7dcb625fdf142'): {
        '1c42716796064bfbca89312a2650211f5645a1f2370675eedad86b3d81f4f9f7',
    },
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    if not path.exists():
        return None
    with path.open('rb') as stream:
        return stream_digest(stream)


def stream_digest(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(128 * 1024), b''):
        h.update(block)
    return h.hexdigest()


def child(root, name):
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise ValueError('Ruta de instalación inválida')
    if name not in (SERVICE, ADAPTER) and not name.startswith((THEME + '/', ENGINE + '/')):
        raise ValueError('Archivo fuera del paquete de Canica')
    path = root / rel
    if path.resolve() != path:
        raise ValueError('Se conserva el enlace existente en ' + name)
    return path


class Console:
    def services(self):
        result = subprocess.run(['/usr/bin/knulli-settings-get', 'system.services'], capture_output=True, text=True)
        # Scarab returns 1 without a diagnostic when the key has never been set.
        if result.returncode == 1 and not result.stderr and not result.stdout:
            return []
        if result.returncode:
            raise RuntimeError('No se pudieron leer los servicios de KNULLI.')
        return result.stdout.split()

    def enable(self, value):
        subprocess.run(['/usr/bin/knulli-services', 'enable' if value else 'disable', 'canica'], check=True)
        if ('canica' in self.services()) != value:
            raise RuntimeError('KNULLI no guardó el ajuste de Canica.')

    def check(self):
        if Path('/proc/device-tree/model').read_bytes().rstrip(b'\0').decode() != MODEL:
            raise ValueError('Se necesita una Anbernic RG35XX H.')
        if Path('/usr/share/knulli/knulli.version').read_text().strip() != FIRMWARE:
            raise ValueError('Se necesita KNULLI Scarab del 11 de mayo de 2026.')
        conflicts = sorted(set(self.services()) & {'fosforo', 'es_patched'})
        if conflicts:
            raise ValueError('En Servicios, desactiva ' + ', '.join(conflicts) + ', reinicia y vuelve a abrir el instalador.')
        live = Path('/usr/bin/emulationstation')
        launcher = Path('/var/run/canica/launcher')
        stock = Path('/var/run/canica/emulationstation.stock') if launcher.exists() and live.samefile(launcher) else live
        if file_digest(stock) != STOCK:
            raise ValueError('El menú instalado no coincide con Scarab para la RG35XX H.')


@contextmanager
def read_package(tool):
    with ZipFile(tool) as app:
        adapter = app.read('resume-emulatorlauncher')
        if digest(adapter) != ADAPTER_SHA:
            raise ValueError('Vuelve a copiar el instalador completo.')
        embedded = next((name for name in PACKAGES if name in app.namelist()), None)
        if embedded:
            # The sealed embedded ZIP is small. Keeping its compressed bytes seekable
            # avoids writing a temporary archive to the card or rereading the outer ZIP.
            stream = io.BytesIO(app.read(embedded))
            expected = PACKAGES[embedded]
        else:
            sibling = next((tool.with_name(n) for n in PACKAGES if tool.with_name(n).is_file()), None)
            if sibling is None:
                raise ValueError('Copia también el ZIP de Canica para RG35XX H junto al instalador, sin extraerlo.')
            stream = sibling.open('rb')
            expected = PACKAGES[sibling.name]
        with stream:
            if stream_digest(stream) != expected:
                raise ValueError('El ZIP está incompleto o pertenece a otra versión. Vuelve a copiarlo.')
            stream.seek(0)
            with ZipFile(stream) as archive:
                yield archive, adapter


def source(kit, name, adapter):
    return io.BytesIO(adapter) if name == ADAPTER else kit.open('share/' + name)


def changes(root, kit, adapter):
    sizes = {entry.filename[6:]: entry.file_size for entry in kit.infolist()
             if entry.filename.startswith('share/') and not entry.is_dir()}
    sizes[ADAPTER] = len(adapter)
    result = []
    custom_adapter = False
    for name, size in sizes.items():
        if name == ADAPTER and (root / name).is_symlink():
            custom_adapter = True
            continue
        path = child(root, name)
        old = file_digest(path)
        with source(kit, name, adapter) as member:
            new = stream_digest(member)
        if name == ADAPTER and old and (not os.access(path, os.X_OK) or
                (old != new and old not in PREVIOUS.get((name, new), ()))):
            custom_adapter = True
            continue
        if old == new:
            continue
        if old is not None and old not in PREVIOUS.get((name, new), ()):
            raise ValueError('Se conserva tu archivo modificado: ' + name)
        result.append((name, old, new, size))
    return result, custom_adapter


def recover(root, work, console):
    if not work.exists():
        return
    if work.is_symlink() or not work.is_dir():
        raise ValueError('La ruta temporal de Canica ya está ocupada.')
    # This reserved directory is ours only when empty or carrying the installer marker.
    if any(work.iterdir()) and not (work / 'installer-v1').is_file():
        raise ValueError('Se conserva la carpeta temporal existente: ' + str(work))
    owned = {'installer-v1', 'pending.json', 'plan.tmp', 'committed', 'restore'}
    extras = []
    for item in work.iterdir():
        if item.name not in owned and not re.fullmatch(r'(?:old|new)-[0-9]+', item.name):
            extras.append(item.name)
        elif item.is_symlink() or not item.is_file():
            raise ValueError('Se conserva la entrada inesperada en la carpeta temporal: ' + item.name)
    journal = work / 'pending.json'
    if journal.exists():
        state = json.loads(journal.read_text())
        for index, (name, old, new) in reversed(list(enumerate(state['files']))):
            dest = child(root, name)
            if (work / ('new-' + str(index))).exists():
                continue  # The staged file never replaced its destination.
            current = file_digest(dest)
            if current == old:
                continue
            if current != new:
                raise ValueError('La recuperación conserva el cambio manual en ' + name)
            if old is None:
                dest.unlink()
            else:
                backup = work / ('old-' + str(index))
                if file_digest(backup) != old:
                    raise ValueError('Respaldo incompleto para ' + name)
                temporary = work / 'restore'
                shutil.copy2(backup, temporary)
                os.replace(temporary, dest)
        if ('canica' in console.services()) != state['enabled']:
            console.enable(state['enabled'])
        os.sync()
        journal.unlink()
    # Discard only installer-owned files. Keep the marker until cleanup is complete.
    for item in work.iterdir():
        if item.name != 'installer-v1' and item.name not in extras:
            item.unlink()
    if extras:
        raise ValueError('Se conserva el archivo inesperado en la carpeta temporal: ' + ', '.join(sorted(extras)))
    (work / 'installer-v1').unlink(missing_ok=True)
    work.rmdir()


def install(tool, root, console):
    console.check()
    root = root.resolve()
    work = root / 'system/.canica-installer-v1'
    if work.parent.resolve() != work.parent:
        raise ValueError('Se conserva la ruta alternativa de configuración.')
    recover(root, work, console)
    with read_package(tool) as (archive, adapter):
        files, custom_adapter = changes(root, archive, adapter)
        commit_files(root, work, console, archive, adapter, files)
        generator = 'share/' + THEME + '/card_screens.py'
        card_warning = ''
        if generator in archive.namelist() and root == Path('/userdata'):
            # Run the verified kit member, independent of the contents of the SD card.
            result = subprocess.run([sys.executable, '-I', '-'], input=archive.read(generator))
            if result.returncode:
                card_warning = ' No se pudieron preparar los fondos. Vuelve a abrir el instalador para reintentar.'
    message = 'Canica está listo. Reinicia la consola y elige es-theme-canica en los ajustes de interfaz.'
    if custom_adapter:
        message += ' Se conservó tu adaptador de partidas.'
    return message + card_warning


def commit_files(root, work, console, archive, adapter, files):
    enabled = 'canica' in console.services()
    if files or not enabled:
        needed = sum(size + ((root/name).stat().st_size if old else 0) for name, old, new, size in files)
        if shutil.disk_usage(work.parent).free < needed + 1024 * 1024:
            raise ValueError('Libera espacio en la tarjeta de datos y vuelve a intentarlo.')
        work.mkdir(mode=0o700)
        try:
            (work / 'installer-v1').touch()
            for index, (name, old, new, size) in enumerate(files):
                dest = child(root, name)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.parent.stat().st_dev != work.stat().st_dev:
                    raise ValueError('El destino usa otro volumen: ' + name)
                if old:
                    shutil.copy2(dest, work / ('old-' + str(index)))
                staged = work / ('new-' + str(index))
                with source(archive, name, adapter) as member, staged.open('wb') as output:
                    shutil.copyfileobj(member, output, 128 * 1024)
                staged.chmod(0o755 if name in (ADAPTER, THEME + "/Preparar fondos de Canica.sh") else 0o644)
            journal = work / 'pending.json'
            pending = work / 'plan.tmp'
            pending.write_text(json.dumps(dict(enabled=enabled, files=[entry[:3] for entry in files])))
            os.sync()
            pending.replace(journal)
            os.sync()
            for index, (name, old, new, size) in enumerate(files):
                dest = child(root, name)
                if file_digest(dest) != old:
                    raise ValueError('El archivo cambió durante la instalación: ' + name)
                os.replace(work / ('new-' + str(index)), dest)
                if file_digest(dest) != new:
                    raise OSError('Copia incompleta: ' + name)
            if not enabled:
                console.enable(True)
            os.sync()
            journal.rename(work / 'committed')
            os.sync()
        finally:
            recover(root, work, console)


def report(message):
    print(message, flush=True)
    try:
        log = Path('/userdata/system/logs/canica-instalacion.txt')
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(message + '\n')
    except OSError:
        pass
    try:
        req = request.Request('http://127.0.0.1:1234/messagebox', data=message.encode(), headers={'Content-Type': 'text/plain; charset=utf-8'})
        with request.build_opener(request.ProxyHandler({})).open(req, timeout=2):
            pass
    except (OSError, error.URLError):
        pass


def main():
    try:
        with open('/var/run/canica-installer.lock', 'a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            message = install(Path(sys.argv[0]).resolve(), Path('/userdata'), Console())
    except (ValueError, RuntimeError, OSError, KeyError, BadZipFile, subprocess.SubprocessError) as exc:
        report('Canica no se instaló. ' + str(exc))
        return 1
    report(message)
    return 0


if __name__ == '__main__':
    sys.exit(main())

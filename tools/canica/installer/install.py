"""Offline installer launched from the RG35XX H Tools list."""
import fcntl
import hashlib
import io
import json
import os
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
ADAPTER_SHA = 'e746b025d1079289d176af8645c12a129b98b0bd8acec177a4a5ec2483d73e42'
PACKAGES = {
    'canica-1.0.1-rc27.2-rg35xx-h.zip': 'c1133da6a93a8b94f8126fea8f43d69cdcbde5a4976e4497f85e1b20194b8021',
    'canica-1.0.1-rc27.1-rg35xx-h.zip': '113e8b662fee7083ecd2383600ca6f4cfd7383065088f9def055383be6605828',
}
# Only these previous release files changed in RC27.2. Preserve all user edits.
PREVIOUS = {'system/canica/SHA256SUMS': '63caf5e4d9f8e95d77631cc56b7a404d951f8e94d0578f31d91f2294c25741a2',
 'system/services/canica': '27928228e36e2db417cf46ac11d674580a7c12efa95ed7e728c986e1cbbc8794',
 'themes/es-theme-canica/README.md': '32bf92075794123dc9c73349a46a93c0ad3958a6e8d57f50ebd6008d023adce3'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    if not path.exists():
        return None
    with path.open('rb') as stream:
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


def read_package(tool):
    with ZipFile(tool) as app:
        adapter = app.read('resume-emulatorlauncher')
        if digest(adapter) != ADAPTER_SHA:
            raise ValueError('Vuelve a copiar el instalador completo.')
        embedded = next((name for name in PACKAGES if name in app.namelist()), None)
        if embedded:
            data = app.read(embedded)
            expected = PACKAGES[embedded]
        else:
            sibling = next((tool.with_name(n) for n in PACKAGES if tool.with_name(n).is_file()), None)
            if sibling is None:
                raise ValueError('Copia también el ZIP de Canica para RG35XX H junto al instalador, sin extraerlo.')
            data = sibling.read_bytes()
            expected = PACKAGES[sibling.name]
    if digest(data) != expected:
        raise ValueError('El ZIP está incompleto o pertenece a otra versión. Vuelve a copiarlo.')
    return ZipFile(io.BytesIO(data)), adapter


def changes(root, kit, adapter):
    files = {name[6:]: kit.read(name) for name in kit.namelist() if name.startswith('share/')}
    files[ADAPTER] = adapter
    result = []
    custom_adapter = False
    for name, data in files.items():
        if name == ADAPTER and (root / name).is_symlink():
            custom_adapter = True
            continue
        path = child(root, name)
        old = file_digest(path)
        new = digest(data)
        if name == ADAPTER and old and (old != new or not os.access(path, os.X_OK)):
            custom_adapter = True
            continue
        if old == new:
            continue
        if old is not None and old != PREVIOUS.get(name):
            raise ValueError('Se conserva tu archivo modificado: ' + name)
        result.append((name, old, new, data))
    return result, custom_adapter


def recover(root, work, console):
    if not work.exists():
        return
    if work.is_symlink() or not work.is_dir():
        raise ValueError('La ruta temporal de Canica ya está ocupada.')
    # This reserved directory is ours only when empty or carrying the installer marker.
    if any(work.iterdir()) and not (work / 'installer-v1').is_file():
        raise ValueError('Se conserva la carpeta temporal existente: ' + str(work))
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
        if item.name != 'installer-v1':
            item.unlink()
    (work / 'installer-v1').unlink(missing_ok=True)
    work.rmdir()


def install(tool, root, console):
    console.check()
    root = root.resolve()
    work = root / 'system/.canica-installer-v1'
    if work.parent.resolve() != work.parent:
        raise ValueError('Se conserva la ruta alternativa de configuración.')
    recover(root, work, console)
    archive, adapter = read_package(tool)
    with archive:
        files, custom_adapter = changes(root, archive, adapter)
    enabled = 'canica' in console.services()
    if files or not enabled:
        needed = sum(len(data) + ((root/name).stat().st_size if old else 0) for name, old, new, data in files)
        if shutil.disk_usage(work.parent).free < needed + 1024 * 1024:
            raise ValueError('Libera espacio en la tarjeta de datos y vuelve a intentarlo.')
        work.mkdir(mode=0o700)
        try:
            (work / 'installer-v1').touch()
            for index, (name, old, new, data) in enumerate(files):
                dest = child(root, name)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.parent.stat().st_dev != work.stat().st_dev:
                    raise ValueError('El destino usa otro volumen: ' + name)
                if old:
                    shutil.copy2(dest, work / ('old-' + str(index)))
                staged = work / ('new-' + str(index))
                staged.write_bytes(data)
                staged.chmod(0o755 if name == ADAPTER else 0o644)
            journal = work / 'pending.json'
            pending = work / 'plan.tmp'
            pending.write_text(json.dumps(dict(enabled=enabled, files=[entry[:3] for entry in files])))
            os.sync()
            pending.replace(journal)
            os.sync()
            for index, (name, old, new, data) in enumerate(files):
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
    message = 'Canica está listo. Reinicia la consola y elige es-theme-canica en los ajustes de interfaz.'
    if custom_adapter:
        message += ' Se conservó tu adaptador de partidas.'
    return message


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

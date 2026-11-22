"""Build the Tools entry. Without --kit the output contains public code only."""
import argparse
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from runpy import run_path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

HERE = Path(__file__).resolve().parent


def build(output, kit=None):
    settings = run_path(str(HERE / 'install.py'))
    adapter = (HERE.parent / 'resume/emulatorlauncher').read_bytes()
    if sha256(adapter).hexdigest() != settings['ADAPTER_SHA']:
        raise ValueError('Revisa la versión del adaptador antes de empaquetar.')
    files = [('__main__.py', (HERE / 'install.py').read_bytes(), ZIP_DEFLATED),
             ('resume-emulatorlauncher', adapter, ZIP_DEFLATED)]
    if kit is not None:
        data = kit.read_bytes()
        if sha256(data).hexdigest() != settings['PACKAGES'].get(kit.name):
            raise ValueError('ZIP de Canica desconocido')
        files.append((kit.name, data, ZIP_STORED))
    buffer = BytesIO()
    buffer.write(b'#!/bin/bash\nexec /usr/bin/python3 -I "$0" "$@"\nexit 1\n')
    with ZipFile(buffer, 'a') as archive:
        for name, content, compression in files:
            archive.writestr(ZipInfo(name), content, compress_type=compression)
    output.write_bytes(buffer.getvalue())
    output.chmod(0o755)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--kit', type=Path)
    args = parser.parse_args()
    build(args.output, args.kit)

#!/usr/bin/env python3
"""User-local installer for the Garuda CRT Community preset. Python 3.9+."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shlex
import shutil
import sqlite3
import subprocess
import sys

NAME = 'Garuda CRT Community'
KEYS = ('_CURRENT_SETTINGS', '_CURRENT_PROFILE', '_CUSTOM_PROFILES')

def paths():
    data = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')).absolute()
    return data, data / 'garuda-crt-community', data / 'applications/garuda-crt-community.desktop'

def closed():
    result = subprocess.run(['pgrep', '-x', 'cool-retro-term'], capture_output=True)
    if result.returncode == 0:
        raise RuntimeError('Close every Cool Retro Term window normally, then retry.')
    if result.returncode != 1:
        raise RuntimeError('Could not check whether Cool Retro Term is running.')

def database(data):
    matches = []
    for p in (data / 'cool-retro-term').rglob('*.sqlite'):
        with sqlite3.connect(p.as_uri() + '?mode=ro', uri=True) as con:
            if con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'").fetchone():
                matches.append(p)
    if len(matches) != 1:
        raise RuntimeError('Open Cool Retro Term once, close it normally, then retry. Expected one settings database.')
    return matches[0]

def get(con, key):
    row = con.execute('SELECT value FROM settings WHERE setting=?', (key,)).fetchone()
    return row[0] if row else None

def put(con, key, value):
    if value is None:
        con.execute('DELETE FROM settings WHERE setting=?', (key,))
    else:
        con.execute('INSERT OR REPLACE INTO settings(setting,value) VALUES (?,?)', (key, value))

def install():
    data, root, desktop = paths()
    if root.exists() or desktop.exists():
        raise RuntimeError('Community installation already exists. Restore/uninstall it before reinstalling.')
    for command in ('cool-retro-term', 'fish', 'fc-match'):
        if not shutil.which(command):
            raise RuntimeError('Missing dependency: ' + command)
    module = Path('/usr/lib/qt6/qml/QMLTermWidget')
    if not (module / 'kb-layouts').is_dir():
        raise RuntimeError('Expected Arch Qt6 QMLTermWidget layout not found; no changes made.')
    source = Path(__file__).resolve().parent / 'preset'
    profile = json.loads((source / 'profile.json').read_text())
    settings = json.loads((source / 'settings.json').read_text())
    font = subprocess.check_output(['fc-match', '-f', '%{family}', profile['fontName']], text=True)
    if profile['fontName'].lower() not in font.lower():
        raise RuntimeError('Install Adwaita Mono first; fontconfig currently selects: ' + font)
    db = database(data)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = data / 'garuda-crt-community-backups' / stamp
    backup.mkdir(parents=True)
    with sqlite3.connect(db) as con:
        old = {k: get(con, k) for k in KEYS}
        previous_profiles = json.loads(old['_CUSTOM_PROFILES'] or '[]')
        if any(p.get('text') == NAME for p in previous_profiles):
            raise RuntimeError('A profile with this name already exists; no settings changed.')
        with sqlite3.connect(backup / 'settings.sqlite') as out:
            con.backup(out)
        state = {'database': str(db), 'before': old, 'root': str(root), 'desktop': str(desktop)}
        (backup / 'restore.json').write_text(json.dumps(state, indent=2))
        try:
            schemes = root / 'qml/QMLTermWidget/color-schemes'
            schemes.mkdir(parents=True)
            shutil.copy2(source / 'cool-retro-term.colorscheme', schemes)
            (schemes.parent / 'kb-layouts').symlink_to(module / 'kb-layouts', target_is_directory=True)
            fish = shutil.which('fish')
            launcher = root / 'launch'
            launcher.write_text('#!/bin/sh\nexport QML_IMPORT_PATH=' + shlex.quote(str(root / 'qml')) +
                '"${QML_IMPORT_PATH:+:$QML_IMPORT_PATH}"\nexec ' + shlex.quote(shutil.which('cool-retro-term')) +
                ' --profile ' + shlex.quote(NAME) + ' -e ' + shlex.quote(fish) + ' -i\n')
            launcher.chmod(0o755)
            subprocess.run(['sh', '-n', str(launcher)], check=True)
            # Desktop Entry escaping differs from shell escaping.
            quoted = str(launcher).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
            desktop.parent.mkdir(parents=True, exist_ok=True)
            desktop.write_text('[Desktop Entry]\nType=Application\nName=' + NAME +
                '\nComment=Sweet-inspired CRT preset with interactive Fish\nExec="' + quoted +
                '"\nIcon=cool-retro-term\nTerminal=false\nCategories=System;TerminalEmulator;\n')
            merged = json.loads(old['_CURRENT_SETTINGS'] or '{}')
            merged.update(settings)
            merged['customCommand'] = shlex.quote(fish) + ' -i'
            previous_profiles.append({'text': NAME, 'obj_string': json.dumps(profile), 'builtin': False})
            put(con, '_CURRENT_SETTINGS', json.dumps(merged))
            put(con, '_CURRENT_PROFILE', json.dumps(profile))
            put(con, '_CUSTOM_PROFILES', json.dumps(previous_profiles))
            (root / 'backup-path').write_text(str(backup))
            con.commit()
        except Exception:
            con.rollback()
            desktop.unlink(missing_ok=True)
            if root.exists():
                shutil.rmtree(root)
            raise
    print('Installed. Open Garuda CRT Community from your application menu.')
    print('Backup:', backup)
    print('Font: Adwaita Mono; scale: 60%. Window rules were not changed.')

def restore():
    data, root, desktop = paths()
    pointer = root / 'backup-path'
    if not pointer.is_file():
        raise RuntimeError('No managed installation found. See README for manual recovery.')
    backup = Path(pointer.read_text())
    state = json.loads((backup / 'restore.json').read_text())
    db = database(data)
    if state['database'] != str(db) or state['root'] != str(root) or state['desktop'] != str(desktop):
        raise RuntimeError('Backup paths do not match this installation; no changes made.')
    # Keep a recovery snapshot of any changes made since installation.
    with sqlite3.connect(db) as con:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        with sqlite3.connect(backup / ('before-restore-' + stamp + '.sqlite')) as out:
            con.backup(out)
        for key in KEYS:
            put(con, key, state['before'][key])
        con.commit()
    desktop.unlink(missing_ok=True)
    shutil.rmtree(root)
    print('Previous settings restored; community launcher and assets removed.')
    print('Recovery backups retained:', backup)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'restore', 'uninstall'])
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise RuntimeError('Run as your desktop user, without sudo.')
    closed()
    install() if args.action == 'install' else restore()

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, sqlite3.Error, subprocess.SubprocessError) as exc:
        sys.exit('ERROR: ' + str(exc))

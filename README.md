# Garuda CRT Community
# Garuda CRT Community

![Garuda CRT with Sweet colors and CRT effects](screenshot.png)

A Sweet-inspired color preset for Cool Retro Term, paired with interactive Fish and the original CRT glow, curvature, noise, and motion effects.

The included preset is the actual user-approved export: **Adwaita Mono at 60% scale**, dark blue-gray background, multicolored Sweet palette, and the retained CRT effects. It does not install a complete Garuda desktop or copy anyone's shell configuration.

## Supported starting point

Garuda / Arch Linux with Qt6 Cool Retro Term. The source setup worked with:

```
cool-retro-term 2.0.0beta2-1
qmltermwidget 2.0.0.git1-1
fish 4.9.3-1
```

This installer targets `/usr/lib/qt6/qml/QMLTermWidget`. Other distributions and newer versions may require adaptation. The installer has been tested against temporary settings databases, not a second live Garuda desktop. The preset itself was verified by its original user on Garuda.

## Install

1. Install `cool-retro-term`, `fish`, Python 3, fontconfig, procps/pgrep, and **Adwaita Mono** using your package manager. On Garuda most supporting tools are already installed. The font may be supplied by an Adwaita fonts package; the installer checks that fontconfig resolves it correctly.
2. Open Cool Retro Term once, then close **all** its windows normally. This creates its settings database.
3. Extract this archive and open a terminal in the extracted directory.
4. Review the installer, then run as your normal desktop user:

   ```sh
   python3 manage.py install
   ```

5. Open **Garuda CRT Community** from the application menu.

No sudo is used by the installer. It does not download code, replace system packages, modify Fish configuration, start an updater, or add an autostart entry. The existing `Garuda CRT` launcher from the original setup is left intact.

### What changes

- Adds a separate `Garuda CRT Community` profile.
- Installs a private palette and launcher under `$XDG_DATA_HOME/garuda-crt-community` (normally `~/.local/share/garuda-crt-community`).
- Adds a desktop entry under the user's applications directory.
- Updates Cool Retro Term's **shared current settings** for the supplied 60% font scale and interactive Fish. These settings can also affect other Cool Retro Term launches; they are not isolated per profile.
- Backs up the database and the three changed settings records before editing them. Existing unrelated database records are preserved.

Always use the **community launcher** for this preset. Selecting only the named profile from a normal Cool Retro Term launch does not enable the private ANSI palette.

## Appearance and behavior

- The export says `Adwaita Mono`, not FiraCode Nerd Font. This is intentional: it preserves the final accepted appearance.
- Font scaling is a global setting, outside the named profile. Ctrl+- and Ctrl++ adjust it. Close normally to save.
- The CRT shader tints the underlying Sweet palette; this is not a pixel-exact Konsole match.
- Fish uses your own existing prompt, greeting, and configuration. Fastfetch appears automatically only if your Fish setup already starts it. No prompt, Fastfetch configuration, or shell history is included.
- The preset retains flicker, jitter, noise, burn-in, and a moving glow from the preferred default CRT appearance. All can be adjusted in Settings if desired.
- **No KDE window rule is included or changed.** Window size is user-controlled. The original user's preferred 53 rows × 169 columns is a reference, not an installer setting.

## Quick verification

After launching, confirm your prompt appears and text is readable. In Fish:

```fish
status is-interactive; and echo "Interactive Fish: OK"
stty size
printf '\033[31mRed\033[0m  \033[32mGreen\033[0m  \033[34mBlue\033[0m\n'
```

Then check these manually:

- Copy a short word using Ctrl+Shift+C and paste with Ctrl+Shift+V.
- Generate scrollback with `seq 1 150`, then scroll back up.
- Run `sleep 30`, then press Ctrl+C; the prompt should return immediately.
- Run `top`, then press `q`; the screen should return to the prompt.
- Close normally and reopen the community launcher; confirm font scale, colors, and Fish persist.

Do not run a system update merely to test the terminal.

## Restore / uninstall

Close every Cool Retro Term window, then from this package directory run:

```sh
python3 manage.py restore
```

`python3 manage.py uninstall` performs the same operation. It restores the three pre-install records (current profile, global settings, custom profile list), removes the community launcher and palette, and retains backups. **Profiles or settings added after installation in those records will be reverted too.** A fresh full database backup is saved immediately before restoration so those later changes remain recoverable. Unrelated database records are not changed.

Backups live under `~/.local/share/garuda-crt-community-backups/` or the equivalent XDG data directory. Keep this package until you uninstall. If the launcher assets were manually removed, use the saved `restore.json` and database snapshot for manual recovery; do not replace an active SQLite database while the app is running.

Re-running install refuses to overwrite an existing managed installation. Restore/uninstall first before reinstalling.

## Sharing

See `REDDIT.md` for a ready-to-edit post and GitHub release checklist. Add a fresh screenshot or short screen recording of your final setup. This package deliberately includes no screenshots containing a personal username or hardware inventory.

## Credits and licensing

See `ATTRIBUTION.md` and `LICENSE`. This is an independent community preset, not an official Garuda or Cool Retro Term release.

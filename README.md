# DVD Screensaver

Bouncing DVD logo screensaver for Linux with idle detection and lock integration.

## Requirements

```bash
# Arch / CachyOS
sudo pacman -S python-pyqt5 sxhkd
```

## Files

| File | Purpose |
|------|---------|
| `dvd_screensaver.py` | The screensaver (PyQt5 window) |
| `dvd-idle-watch.sh` | Launches screensaver after 5 min idle, kills it on activity |
| `lock-with-screensaver.sh` | Launches screensaver + locks session simultaneously |
| `index.html` | Browser-based version (open in any browser) |

## Setup

### 1. Clone

```bash
git clone https://github.com/DeveshB-1/dvd-screensaver.git
cd dvd-screensaver
chmod +x dvd_screensaver.py dvd-idle-watch.sh lock-with-screensaver.sh
```

### 2. Idle watcher (auto-launch after 5 min idle)

```bash
cp dvd-idle-watch.service ~/.config/systemd/user/dvd-screensaver.service
# Edit ExecStart path inside the file to match your clone location
systemctl --user daemon-reload
systemctl --user enable --now dvd-screensaver.service
```

Or manually create `~/.config/systemd/user/dvd-screensaver.service`:

```ini
[Unit]
Description=DVD Idle Screensaver Watcher
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/dvd-idle-watch.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
```

### 3. Alt+L shortcut (screensaver + lock)

Requires `sxhkd`. Add to `~/.config/sxhkd/sxhkdrc`:

```
alt + l
    /path/to/lock-with-screensaver.sh
```

Then run sxhkd as a systemd user service:

```bash
# Create ~/.config/systemd/user/sxhkd.service
[Unit]
Description=Simple X Hotkey Daemon
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/sxhkd
Restart=on-failure
RestartSec=3

[Install]
WantedBy=graphical-session.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now sxhkd.service
```

## Usage

| Action | Result |
|--------|--------|
| `Alt+L` | Launch screensaver + lock session |
| `python3 dvd_screensaver.py` | Launch screensaver manually |
| Idle 5 min | Screensaver auto-launches |
| Any activity | Idle watcher kills screensaver |
| Press `D` | Exit screensaver |

## Browser version

Open `index.html` in any browser. No dependencies.

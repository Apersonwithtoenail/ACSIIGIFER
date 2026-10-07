# ACSIIGIFER

**Play GIFs and videos as colored ASCII art inside a real GTK window.**

Renders images, GIFs, and videos as live colored ASCII art in a native GTK window. Built on chafa, mpv, and VTE.

## Features

- Play GIFs, images, and videos as ASCII
- 7 symbol sets
- Original view (toggle with Space)
- Resizable window
- Fullscreen (F11)

## Requirements

- chafa
- mpv (optional)
- python3-gi
- gir1.2-vte-2.91
- python3-pil

## Install

    git clone https://github.com/Apersonwithtoenail/ACSIIGIFER.git
    cd ACSIIGIFER
    ./install.sh

## Usage

    asciigif

Then open a GIF or video file from the app.

## Controls

| Key | Action |
|-----|--------|
| Space | Toggle original view |
| F11 | Fullscreen |

## Platform status

| Platform | Status |
|----------|--------|
| Linux (Debian / Ubuntu / Kali) | Tested |
| macOS | Untested — installer written, needs verification |
| Windows | Requires WSL2 (VTE doesn't work natively) |

## Uninstall

    ./uninstall.sh

## License

MIT — see LICENSE.


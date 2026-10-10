# ACSIIGIFER

**Play GIFs and videos as colored ASCII art inside a real GTK window.**

Renders images, GIFs, and videos as live colored ASCII art in a native GTK window. Built on `chafa`, `mpv`, and VTE.

## Features

- Play GIFs, images, and videos as ASCII
- Seven symbol sets (ascii, block, braille, narrow, and more)
- Original view toggle
- Resizable window
- Fullscreen

## Requirements

- `chafa`
- `mpv` (optional)
- `python3-gi`
- `gir1.2-vte-2.91`
- `python3-pil`

## Install

    git clone https://github.com/Apersonwithtoenail/ACSIIGIFER.git
    cd ACSIIGIFER
    ./install.sh

Then launch from your app menu, or run:

    asciigifer

Uninstall with `./uninstall.sh`.

## Terminal edition

The repo also ships a terminal-only script:

    ./asciigif.sh               # random GIF from ~/Videos/GIF
    ./asciigif.sh my.gif        # specific file
    ./asciigif.sh -S braille -l # loop with smooth dots

Options: `-d DIR`, `-s WxH`, `-S STYLE`, `-l` (loop), `-h`, `-v`.

## Controls (GTK window)

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

## License

MIT — see [LICENSE](LICENSE).

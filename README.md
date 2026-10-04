# asciigif

Play GIFs and videos as colored ASCII art inside a real GTK window.

Works on Linux (native), macOS (Homebrew), and Windows (via WSL2).


Play GIFs as colored ASCII art inside a real GTK window.

## Install

    git clone https://github.com/Apersonwithtoenail/ACSIIGIFER.git
    cd ACSIIGIFER
    ./install.sh
    asciigif

## Features

- Play GIFs, images, videos as ASCII
- Original view (Space key)
- Fullscreen (F11)
- 7 symbol sets
- Resizable window

## Requirements

- chafa
- mpv (optional)
- python3-gi
- gir1.2-vte-2.91
- python3-pil

## Uninstall

    ./uninstall.sh

## License

MIT

## Platform status

| Platform | Status |
|---|---|
| Linux (Debian/Ubuntu/Kali) | ✅ Tested |
| macOS | ⚠️ Untested — installer written, needs verification |
| Windows | ⚠️ Requires WSL2 (VTE doesn't work natively) |

#!/bin/bash
# asciigif — play any GIF in your terminal as ASCII art

VERSION="1.0.0"
GIF_DIR="${ASCIIGIF_DIR:-$HOME/Videos/GIF}"
SIZE="100x40"
STYLE="ascii"
LOOP=false
FILE=""

usage() {
    cat << HELP
asciigif v$VERSION — terminal GIF player

USAGE:
    asciigif [options] [file.gif]

OPTIONS:
    -d, --dir DIR      GIF folder (default: ~/Videos/GIF)
    -s, --size WxH     Output size (default: 100x40)
    -S, --style NAME   ascii | block | braille | all | narrow
    -l, --loop         Loop forever (Ctrl+C to stop)
    -h, --help         Show this help
    -v, --version      Show version

EXAMPLES:
    asciigif                    # random GIF from default folder
    asciigif my.gif             # specific file
    asciigif -S braille         # smooth dots
    asciigif -l                 # loop forever
HELP
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dir) GIF_DIR="$2"; shift 2 ;;
        -s|--size) SIZE="$2"; shift 2 ;;
        -S|--style) STYLE="$2"; shift 2 ;;
        -l|--loop) LOOP=true; shift ;;
        -h|--help) usage; exit 0 ;;
        -v|--version) echo "asciigif v$VERSION"; exit 0 ;;
        -*) echo "Unknown option: $1"; usage; exit 1 ;;
        *) FILE="$1"; shift ;;
    esac
done

if ! command -v chafa >/dev/null; then
    echo "Error: chafa not installed. Run: sudo apt install chafa"
    exit 1
fi

if [ -z "$FILE" ]; then
    if [ ! -d "$GIF_DIR" ]; then
        echo "Error: folder not found: $GIF_DIR"
        exit 1
    fi
    FILE=$(find "$GIF_DIR" -iname '*.gif' | shuf -n 1)
fi

if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
    echo "Error: no GIF found"
    exit 1
fi

play() {
    chafa -f symbols --symbols="$STYLE" --size="$SIZE" --animate=on "$FILE"
}

if [ "$LOOP" = true ]; then
    while true; do play; done
else
    play
fi

#!/bin/bash
export GDK_BACKEND=x11
 export LIBGL_ALWAYS_SOFTWARE=1
# asciigif-gui — graphical frontend for asciigif

VERSION="1.0.0"
GIF_DIR="${ASCIIGIF_DIR:-$HOME/Videos/GIF}"
TERM_APP="konsole"

# Check tools
command -v zenity >/dev/null || { echo "Install zenity: sudo apt install zenity"; exit 1; }
command -v chafa >/dev/null || { echo "Install chafa: sudo apt install chafa"; exit 1; }

show_menu() {
    zenity --list --title="asciigif v$VERSION" \
        --text="<b>🎬 Terminal GIF Player</b>\n\nPick an action:" \
        --column="Action" --column="Description" \
        --width=500 --height=380 \
        "🎲 Random GIF"        "Play a random GIF from your folder" \
        "📁 Browse GIFs"       "Pick a specific GIF to play" \
        "🎨 Choose Style"      "Change rendering style + play random" \
        "📐 Custom Size"       "Set output size + play random" \
        "🔁 Loop Mode"         "Loop a random GIF forever" \
        "⚙️  Settings"          "Change GIF folder" \
        "❌ Quit"              "Close"
}

play_in_terminal() {
    local file="$1"
    local style="$2"
    local size="$3"
    local loop="$4"

    if [ "$loop" = "yes" ]; then
        CMD="while true; do chafa -f symbols --symbols=$style --size=$size --animate=on '$file'; done"
    else
        CMD="chafa -f symbols --symbols=$style --size=$size --animate=on '$file'; echo; read -p 'Press Enter to close...'"
    fi

    case "$TERM_APP" in
        konsole)              konsole --hold -e bash -c "$CMD" & ;;
        gnome-terminal)       gnome-terminal -- bash -c "$CMD" & ;;
        x-terminal-emulator)  $TERM_APP -e bash -c "$CMD" & ;;
        xterm)                xterm -e bash -c "$CMD" & ;;
        *)                    $TERM_APP -e bash -c "$CMD" & ;;
    esac
}

pick_random() {
    find "$GIF_DIR" -iname '*.gif' -type f | shuf -n 1
}

while true; do
    CHOICE=$(show_menu)
    [ -z "$CHOICE" ] && exit 0

    case "$CHOICE" in
        "🎲 Random GIF"*)
            FILE=$(pick_random)
            [ -z "$FILE" ] && zenity --error --text="No GIFs found in $GIF_DIR" && continue
            play_in_terminal "$FILE" "block" "100x40" "no"
            ;;

        "📁 Browse GIFs"*)
            FILE=$(zenity --file-selection --title="Pick a GIF" \
                --filename="$GIF_DIR/" \
                --file-filter="GIF files | *.gif" \
                --file-filter="All files | *")
            [ -z "$FILE" ] && continue
            play_in_terminal "$FILE" "block" "100x40" "no"
            ;;

        "🎨 Choose Style"*)
            STYLE=$(zenity --list --title="Pick a style" \
                --text="How should the GIF render?" \
                --column="Style" --column="Look" \
                --width=400 --height=320 \
                "ascii"   "Classic @ # % * . :" \
                "block"   "Solid blocks ▀ ▄ █" \
                "braille" "Fine dots (smooth)" \
                "all"     "Mixed (best detail)" \
                "narrow"  "Thin characters")
            [ -z "$STYLE" ] && continue
            FILE=$(pick_random)
            play_in_terminal "$FILE" "$STYLE" "100x40" "no"
            ;;

        "📐 Custom Size"*)
            SIZE=$(zenity --entry --title="Output size" \
                --text="Enter size (columns x rows):" \
                --entry-text="100x40")
            [ -z "$SIZE" ] && continue
            FILE=$(pick_random)
            play_in_terminal "$FILE" "block" "$SIZE" "no"
            ;;

        "🔁 Loop Mode"*)
            FILE=$(pick_random)
            [ -z "$FILE" ] && zenity --error --text="No GIFs found" && continue
            play_in_terminal "$FILE" "block" "100x40" "yes"
            ;;

        "⚙️  Settings"*)
            NEWDIR=$(zenity --file-selection --directory \
                --title="Pick GIF folder" \
                --filename="$GIF_DIR/")
            [ -z "$NEWDIR" ] && continue
            GIF_DIR="$NEWDIR"
            zenity --info --text="GIF folder set to:\n$GIF_DIR\n\n(Export ASCIIGIF_DIR=$GIF_DIR to make permanent)"
            ;;

        "❌ Quit"*)
            exit 0
            ;;
    esac
done

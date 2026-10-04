#!/bin/bash
set -e
echo "asciigif installer"
echo "==================="

if [ ! -f /etc/debian_version ]; then
    echo "Only Debian / Ubuntu / Kali supported for auto-install."
    echo "Manual deps: chafa mpv python3-gi gir1.2-vte-2.91 python3-pil"
    exit 1
fi

echo "→ Installing dependencies..."
sudo apt update
sudo apt install -y chafa mpv python3-gi python3-gi-cairo \
                    gir1.2-vte-2.91 python3-pil

echo "→ Copying files..."
INSTALL_DIR="$HOME/.local/share/asciigif"
mkdir -p "$INSTALL_DIR"
cp asciigif-app.py "$INSTALL_DIR/"
cp asciigif.sh     "$INSTALL_DIR/" 2>/dev/null || true
chmod +x "$INSTALL_DIR/asciigif-app.py"

echo "→ Creating launcher..."
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/asciigif" << 'WRAP'
#!/bin/bash
exec python3 "$HOME/.local/share/asciigif/asciigif-app.py" "$@"
WRAP
chmod +x "$HOME/.local/bin/asciigif"

echo "→ Creating desktop entry..."
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/asciigif.desktop" << 'DESK'
[Desktop Entry]
Type=Application
Name=asciigif
Comment=Play GIFs as ASCII art in a GTK window
Exec=/home/kavish/.local/bin/asciigif
Icon=utilities-terminal
Terminal=false
Categories=Graphics;Utility;
DESK
update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true

echo ""
echo "✅ Installed!"
echo "Run: asciigif"
echo "Or find 'asciigif' in your app menu."
echo ""
echo "If 'asciigif' isn't found, add to PATH:"
echo '  export PATH="$HOME/.local/bin:$PATH"'

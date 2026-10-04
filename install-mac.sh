#!/bin/bash
set -e
echo "asciigif installer (macOS)"
echo "========================"

# Check for Homebrew
if ! command -v brew >/dev/null; then
    echo "→ Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "→ Installing dependencies..."
brew install chafa mpv gtk+3 vte3 python3 pygobject3

echo "→ Copying files..."
INSTALL_DIR="$HOME/.local/share/asciigif"
mkdir -p "$INSTALL_DIR"
cp asciigif-app.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/asciigif-app.py"

echo "→ Creating launcher..."
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/asciigif" << 'WRAP'
#!/bin/bash
exec python3 "$HOME/.local/share/asciigif/asciigif-app.py" "$@"
WRAP
chmod +x "$HOME/.local/bin/asciigif"

echo ""
echo "✅ Installed! Add ~/.local/bin to PATH if needed:"
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo ""
echo "Run: asciigif"

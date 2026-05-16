#!/bin/bash
# Mac first-time setup. Double-click to run.
set -e
cd "$(dirname "$0")"

echo "=============================================="
echo "  Check Splitter - First-time setup (Mac)"
echo "=============================================="
echo

# --- 1. Python 3 check ---
if ! command -v python3 >/dev/null 2>&1; then
    echo "[!] python3 not found."
    echo
    echo "Install it from https://www.python.org/downloads/macos/"
    echo "or with Homebrew: brew install python"
    echo
    read -n 1 -s -r -p "Press any key to close..."
    exit 1
fi
echo "[OK] python3 found: $(python3 --version)"
echo

# --- 2. Homebrew check (used to install tesseract) ---
if ! command -v brew >/dev/null 2>&1; then
    echo "[!] Homebrew not found. Homebrew is the easiest way to install Tesseract."
    echo
    echo "Install Homebrew by pasting this in Terminal:"
    echo '   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo
    echo "Then run this setup.command again."
    echo
    read -n 1 -s -r -p "Press any key to close..."
    exit 1
fi
echo "[OK] Homebrew found."
echo

# --- 3. Tesseract + Hebrew language data ---
if ! command -v tesseract >/dev/null 2>&1; then
    echo "Installing Tesseract OCR..."
    brew install tesseract
fi
echo "[OK] Tesseract found: $(tesseract --version 2>&1 | head -n 1)"

if ! tesseract --list-langs 2>&1 | grep -q "^heb$"; then
    echo "Installing Tesseract Hebrew language pack (tesseract-lang)..."
    brew install tesseract-lang
fi
if tesseract --list-langs 2>&1 | grep -q "^heb$"; then
    echo "[OK] Hebrew language pack installed."
else
    echo "[!] Hebrew language pack still missing after install. Try: brew reinstall tesseract-lang"
    read -n 1 -s -r -p "Press any key to close..."
    exit 1
fi
echo

# --- 4. Python packages ---
echo "Installing Python packages (pymupdf, pytesseract, pillow)..."
# --break-system-packages is needed on newer Python on macOS that ships PEP 668 markers.
# --user keeps it out of the system Python's site-packages.
python3 -m pip install --user --upgrade -r requirements.txt 2>/dev/null \
    || python3 -m pip install --user --upgrade --break-system-packages -r requirements.txt

echo
echo "=============================================="
echo "  Setup complete. Double-click run.command"
echo "  to start the tool."
echo "=============================================="
read -n 1 -s -r -p "Press any key to close..."

# מפצל שוברי תשלום (Check Splitter)

Splits a multi-page Hebrew check PDF into one PDF per check, named after each recipient.
Runs **100% locally on your computer** — no files are uploaded anywhere.

---

## Mac

### Setup (one time)

1. **Install Python 3** if you don't have it: `python3 --version` in Terminal should print a version. If not, install from <https://www.python.org/downloads/macos/>.
2. **Double-click `setup.command`**. It installs Homebrew prerequisites (Tesseract + Hebrew language pack) and the Python packages. First run takes a few minutes.
   - If macOS blocks it with *"cannot be opened because it is from an unidentified developer"*: right-click the file → **Open** → **Open**. You only need to do this once.

### Run

Double-click **`run.command`**. Your browser opens to `http://127.0.0.1:8000`. Close the Terminal window to stop.

---

## Windows

### Setup (one time)

1. **Install Python 3** from <https://www.python.org/downloads/>.
   > ⚠️ On the first install screen, **tick "Add python.exe to PATH"** before clicking *Install Now*.
2. **Install Tesseract OCR** from <https://github.com/UB-Mannheim/tesseract/wiki> (the latest `tesseract-ocr-w64-setup-*.exe`).
   - During install, on the **"Choose components"** screen, expand **"Additional language data"** and tick **Hebrew**.
   - Use the default install location (`C:\Program Files\Tesseract-OCR`).
3. **Double-click `setup.bat`**. It checks your installs and installs the Python packages.

### Run

Double-click **`run.bat`**. Your browser opens to `http://127.0.0.1:8000`. Close the command window to stop.

---

## Using the tool

1. Drag a PDF into the page (or click to pick one).
2. Click **"פצל והורד ZIP"**.
3. A ZIP downloads containing one PDF per check, each named after the recipient.

## How it works

Each page of the input PDF is rendered as an image and read with Tesseract OCR (Hebrew).
The recipient name is taken from the line that begins with **"תשלום זה ניתן עבור:"**.
Each page becomes its own output PDF; when the same recipient appears on multiple pages
the files are numbered `שם.pdf`, `שם (2).pdf`, `שם (3).pdf`, etc.

## Troubleshooting

**Mac**
- *"`brew: command not found`" during setup* — install Homebrew first, the setup script tells you how.
- *"`tesseract is not installed`" when running* — `brew install tesseract tesseract-lang` in Terminal, then try again.

**Windows**
- *"python is not recognized"* — Python wasn't added to PATH. Re-install Python and tick the PATH box on the first screen.
- *"tesseract is not installed or it's not in your PATH"* — install Tesseract from the link above. The tool also auto-detects it at `C:\Program Files\Tesseract-OCR\tesseract.exe`.

**Both**
- *Names come out wrong / empty* — the Hebrew language pack wasn't installed with Tesseract. Re-run setup; it will install it.
- *Browser shows "site can't be reached"* — the launcher window must stay open. Wait a couple seconds after launching, then refresh.

## Privacy

All processing happens on your machine. The web interface is only reachable from your own
computer (bound to `127.0.0.1` — localhost). Nothing is sent over the internet.

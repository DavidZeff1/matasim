# Check Splitter

Splits a Hebrew check PDF into one PDF per recipient. Runs locally — no files leave your computer.

## What to install (one time)

1. **Python 3** — https://www.python.org/downloads/
   *On Windows: tick "Add python.exe to PATH" on the first install screen.*
2. **Tesseract OCR with Hebrew**
   - **Mac:** `brew install tesseract tesseract-lang`
   - **Windows:** installer at https://github.com/UB-Mannheim/tesseract/wiki — during install, expand "Additional language data" and tick **Hebrew**.
3. **Python packages** — open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   ```

## How to use it

In a terminal, from this folder:

```
python server.py
```

Open http://127.0.0.1:8000 in your browser. Drag a PDF in, click the button, a ZIP downloads.

To stop: press Ctrl+C in the terminal (or close the window).

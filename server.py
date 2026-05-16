#!/usr/bin/env python3
"""Minimal web UI for split_checks: upload a PDF, download a ZIP of split files."""

from __future__ import annotations

import io
import tempfile
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from split_checks import split_pdf

PORT = 8000
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

INDEX_HTML = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>פיצול שוברי תשלום</title>
<style>
  :root { color-scheme: light dark; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    max-width: 560px; margin: 4rem auto; padding: 0 1rem; line-height: 1.5;
  }
  h1 { font-size: 1.5rem; margin-bottom: .25rem; }
  p.sub { color: #666; margin-top: 0; }
  form {
    border: 2px dashed #bbb; border-radius: 12px;
    padding: 2rem; text-align: center; margin-top: 2rem;
  }
  form.drag { border-color: #4a90e2; background: rgba(74,144,226,.05); }
  input[type=file] { margin: 1rem 0; }
  button {
    background: #4a90e2; color: white; border: 0; padding: .7rem 1.4rem;
    border-radius: 8px; font-size: 1rem; cursor: pointer;
  }
  button:disabled { opacity: .6; cursor: wait; }
  .status { margin-top: 1rem; color: #555; min-height: 1.5em; }
  .error { color: #c0392b; }
</style>
</head>
<body>
  <h1>פיצול שוברי תשלום</h1>
  <p class="sub">העלאת PDF רב-עמודי. כל עמוד יזוהה לפי שם הנמען וימוזג לקובץ נפרד.</p>
  <form id="f" method="post" action="/split" enctype="multipart/form-data">
    <div>גרור קובץ PDF לכאן או:</div>
    <input id="file" type="file" name="pdf" accept="application/pdf" required>
    <div>
      <button type="submit">פצל והורד ZIP</button>
    </div>
    <div class="status" id="status"></div>
  </form>
<script>
  const form = document.getElementById('f');
  const status = document.getElementById('status');
  const fileInput = document.getElementById('file');
  const button = form.querySelector('button');

  ['dragenter','dragover'].forEach(e => form.addEventListener(e, ev => {
    ev.preventDefault(); form.classList.add('drag');
  }));
  ['dragleave','drop'].forEach(e => form.addEventListener(e, ev => {
    ev.preventDefault(); form.classList.remove('drag');
  }));
  form.addEventListener('drop', ev => {
    if (ev.dataTransfer.files.length) fileInput.files = ev.dataTransfer.files;
  });

  form.addEventListener('submit', async ev => {
    ev.preventDefault();
    if (!fileInput.files.length) return;
    status.className = 'status';
    status.textContent = 'מעבד... זה עשוי להימשך דקה (OCR לכל עמוד).';
    button.disabled = true;
    try {
      const fd = new FormData(form);
      const resp = await fetch('/split', { method: 'POST', body: fd });
      if (!resp.ok) {
        const msg = await resp.text();
        throw new Error(msg || resp.statusText);
      }
      const blob = await resp.blob();
      const cd = resp.headers.get('Content-Disposition') || '';
      const m = cd.match(/filename\\*=UTF-8''([^;]+)/) || cd.match(/filename="?([^";]+)"?/);
      const name = m ? decodeURIComponent(m[1]) : 'split.zip';
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = name; document.body.appendChild(a); a.click();
      a.remove(); URL.revokeObjectURL(url);
      status.textContent = 'הורדה התחילה.';
    } catch (e) {
      status.className = 'status error';
      status.textContent = 'שגיאה: ' + e.message;
    } finally {
      button.disabled = false;
    }
  });
</script>
</body>
</html>
"""


def parse_multipart(body: bytes, boundary: bytes) -> tuple[str, bytes] | None:
    """Extract (filename, file_bytes) for the first file part. Tiny parser
    sufficient for a single <input type=file> form."""
    delimiter = b"--" + boundary
    parts = body.split(delimiter)
    for part in parts:
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        header_blob, _, content = part.partition(b"\r\n\r\n")
        header_lines = header_blob.decode("utf-8", errors="replace").split("\r\n")
        disposition = next(
            (h for h in header_lines if h.lower().startswith("content-disposition:")),
            "",
        )
        if "filename=" not in disposition:
            continue
        filename = ""
        for token in disposition.split(";"):
            token = token.strip()
            if token.startswith("filename="):
                filename = token.split("=", 1)[1].strip().strip('"')
                break
        # content has a trailing \r\n before the next boundary
        if content.endswith(b"\r\n"):
            content = content[:-2]
        return filename, content
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter log
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self):
        if self.path != "/split":
            self.send_error(404)
            return

        ctype = self.headers.get("Content-Type", "")
        if not ctype.startswith("multipart/form-data"):
            self._send_text(400, "expected multipart/form-data")
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_UPLOAD_BYTES:
            self._send_text(413, "file too large or missing")
            return

        boundary = None
        for token in ctype.split(";"):
            token = token.strip()
            if token.startswith("boundary="):
                boundary = token.split("=", 1)[1].strip().strip('"').encode()
        if not boundary:
            self._send_text(400, "no multipart boundary")
            return

        body = self.rfile.read(length)
        parsed = parse_multipart(body, boundary)
        if not parsed:
            self._send_text(400, "no file uploaded")
            return
        filename, data = parsed
        if not data:
            self._send_text(400, "empty file")
            return

        try:
            zip_bytes, zip_name = self._process(filename, data)
        except Exception as e:
            self._send_text(500, f"processing failed: {e}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(zip_bytes)))
        encoded = quote(zip_name)
        self.send_header(
            "Content-Disposition",
            f"attachment; filename=\"split.zip\"; filename*=UTF-8''{encoded}",
        )
        self.end_headers()
        self.wfile.write(zip_bytes)

    def _send_text(self, code: int, msg: str) -> None:
        body = msg.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _process(self, original_name: str, data: bytes) -> tuple[bytes, str]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / (original_name or "input.pdf")
            src.write_bytes(data)
            out_dir = tmp_path / "out"
            written = split_pdf(src, out_dir, dpi=300)

            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for p in written:
                    zf.write(p, arcname=p.name)
            zip_name = (Path(original_name).stem or "split") + ".zip"
            return buf.getvalue(), zip_name


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://127.0.0.1:{PORT}  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()

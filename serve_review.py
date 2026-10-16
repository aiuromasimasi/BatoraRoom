#!/usr/bin/env python3
"""clips_review.html 用の簡易サーバー（Range対応版 http.server）。
python3 serve_review.py → http://localhost:8899/clips_review.html
- Steamトレーラーのシーク再生（Rangeリクエスト）OK
- YouTube埋め込み視聴（http origin が必要）OK
Ctrl+C で終了。"""
import http.server, os, re, socketserver

PORT = 8899

class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        rng = self.headers.get("Range")
        if os.path.isfile(path) and rng:
            m = re.match(r"bytes=(\d+)-(\d*)", rng)
            if m:
                size = os.path.getsize(path)
                a = int(m.group(1))
                b = int(m.group(2)) if m.group(2) else size - 1
                b = min(b, size - 1)
                if a >= size:
                    self.send_error(416, "Requested Range Not Satisfiable")
                    return None
                f = open(path, "rb"); f.seek(a)
                self.send_response(206)
                self.send_header("Content-Type", self.guess_type(path))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
                self.send_header("Content-Length", str(b - a + 1))
                self.end_headers()
                self._range = (a, b)
                return f
        return super().send_head()

    def copyfile(self, src, dst):
        if hasattr(self, "_range"):
            a, b = self._range; n = b - a + 1
            del self._range
            while n > 0:
                chunk = src.read(min(65536, n))
                if not chunk: break
                dst.write(chunk); n -= len(chunk)
        else:
            super().copyfile(src, dst)

    def log_message(self, *a): pass  # 静かに

os.chdir(os.path.dirname(os.path.abspath(__file__)))
socketserver.ThreadingTCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(("", PORT), RangeHandler) as srv:
    print(f"→ http://localhost:{PORT}/clips_review.html  (Ctrl+Cで終了)")
    srv.serve_forever()

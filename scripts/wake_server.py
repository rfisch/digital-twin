#!/usr/bin/env python3
"""
Lightweight wake server for the Digital Twin service.

Runs on port 9090 with near-zero resource usage. Jacqueline can visit
http://Ryans-Mac-Studio.local:9090 from any device on the network to
start/stop the full service on demand — no SSH or terminal needed.
"""

import http.server
import json
import os
import signal
import subprocess
import sys

PORT = 9090
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_SCRIPT = os.path.join(PROJECT_DIR, "scripts", "service.sh")
ROOT_CA_PATH = os.path.join(PROJECT_DIR, "caddy-root-ca.crt")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jacq's Digital Twin</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0a0a0a; color: #e5e5e5;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh; padding: 1rem;
  }
  .card {
    background: #171717; border: 1px solid #262626; border-radius: 12px;
    padding: 2.5rem; max-width: 400px; width: 100%; text-align: center;
  }
  h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
  .subtitle { color: #737373; font-size: 0.875rem; margin-bottom: 2rem; }
  .status {
    padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1.5rem;
    font-weight: 500; font-size: 0.9rem;
  }
  .status.running { background: #052e16; color: #4ade80; border: 1px solid #166534; }
  .status.stopped { background: #1c1917; color: #a8a29e; border: 1px solid #292524; }
  .status.loading { background: #1e1b4b; color: #a5b4fc; border: 1px solid #312e81; }
  .actions { display: flex; gap: 0.75rem; }
  button {
    flex: 1; padding: 0.75rem; border: none; border-radius: 8px;
    font-size: 0.95rem; font-weight: 600; cursor: pointer;
    transition: opacity 0.15s;
  }
  button:hover { opacity: 0.85; }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
  .btn-start { background: #16a34a; color: #fff; }
  .btn-stop { background: #dc2626; color: #fff; }
  .link {
    display: block; margin-top: 1.5rem; color: #737373;
    font-size: 0.8rem; text-decoration: none;
  }
  .link.active { color: #60a5fa; text-decoration: underline; }
</style>
</head>
<body>
<div class="card">
  <h1>Jacq's Digital Twin</h1>
  <p class="subtitle">Writing assistant service</p>
  <div id="status" class="status loading">Checking...</div>
  <div class="actions">
    <button class="btn-start" id="startBtn" onclick="action('start')" disabled>Start</button>
    <button class="btn-stop" id="stopBtn" onclick="action('stop')" disabled>Stop</button>
  </div>
  <a id="appLink" class="link" href="/">Open App</a>
</div>
<script>
  async function checkStatus() {
    try {
      const r = await fetch('/api/status');
      const d = await r.json();
      const el = document.getElementById('status');
      const startBtn = document.getElementById('startBtn');
      const stopBtn = document.getElementById('stopBtn');
      const link = document.getElementById('appLink');
      if (d.running) {
        el.className = 'status running';
        el.textContent = 'Running';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        link.href = 'https://' + window.location.hostname;
        link.className = 'link active';
        link.textContent = 'Open App \\u2192';
      } else {
        el.className = 'status stopped';
        el.textContent = 'Stopped';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        link.className = 'link';
        link.textContent = 'Start the service to use the app';
        link.removeAttribute('href');
      }
    } catch(e) {
      document.getElementById('status').textContent = 'Error checking status';
    }
  }

  async function action(act) {
    const el = document.getElementById('status');
    el.className = 'status loading';
    el.textContent = act === 'start' ? 'Starting...' : 'Stopping...';
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = true;
    try {
      await fetch('/api/' + act, { method: 'POST' });
      // Give services a moment to come up / shut down
      setTimeout(checkStatus, act === 'start' ? 3000 : 1500);
    } catch(e) {
      el.textContent = 'Error';
      setTimeout(checkStatus, 2000);
    }
  }

  checkStatus();
  setInterval(checkStatus, 10000);
</script>
</body>
</html>"""


class WakeHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Suppress default access logs; only log errors
        pass

    def _respond(self, code, body, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode())

    def _service_running(self):
        result = subprocess.run(
            ["bash", SERVICE_SCRIPT, "status"],
            capture_output=True, text=True,
        )
        # If any line says "running", service is up
        return "running" in result.stdout.lower()

    def do_GET(self):
        if self.path == "/api/status":
            running = self._service_running()
            self._respond(200, json.dumps({"running": running}))
        elif self.path == "/cert":
            try:
                with open(ROOT_CA_PATH, "rb") as f:
                    cert_data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/x-x509-ca-cert")
                self.send_header("Content-Disposition", "attachment; filename=caddy-root-ca.crt")
                self.send_header("Content-Length", str(len(cert_data)))
                self.end_headers()
                self.wfile.write(cert_data)
            except FileNotFoundError:
                self._respond(404, json.dumps({"error": "cert not found"}))
        elif self.path == "/" or self.path == "/wake":
            self._respond(200, HTML_PAGE, "text/html")
        else:
            self._respond(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path == "/api/start":
            subprocess.Popen(
                ["bash", SERVICE_SCRIPT, "start"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            self._respond(200, json.dumps({"ok": True, "action": "starting"}))
        elif self.path == "/api/stop":
            subprocess.Popen(
                ["bash", SERVICE_SCRIPT, "stop"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            self._respond(200, json.dumps({"ok": True, "action": "stopping"}))
        else:
            self._respond(404, json.dumps({"error": "not found"}))


def main():
    server = http.server.HTTPServer(("0.0.0.0", PORT), WakeHandler)
    try:
        signal.signal(signal.SIGTERM, lambda *_: (server.shutdown(), sys.exit(0)))
    except ValueError:
        pass  # Running in a thread — signals handled by parent
    print(f"Wake server listening on port {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

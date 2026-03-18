#!/usr/bin/env python3
"""
Launcher for wake server + Caddy HTTPS proxy.
Runs as a single launchd agent. Starts the Python wake server in a thread
and execs Caddy as the main process.
"""

import os
import signal
import subprocess
import sys
import threading

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def run_wake_server():
    """Run the wake server in-process (same interpreter, no subprocess)."""
    sys.path.insert(0, PROJECT_DIR)
    from scripts.wake_server import main
    main()


def main():
    # Start wake server in a background thread
    wake_thread = threading.Thread(target=run_wake_server, daemon=True)
    wake_thread.start()

    # Run Caddy as the main process (blocks until signal)
    caddy_log = open(os.path.join(LOG_DIR, "caddy.log"), "a")
    caddy = subprocess.Popen(
        ["/opt/homebrew/bin/caddy", "run", "--config", os.path.join(PROJECT_DIR, "Caddyfile")],
        stdout=caddy_log,
        stderr=caddy_log,
    )

    def shutdown(*_):
        caddy.terminate()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    caddy.wait()


if __name__ == "__main__":
    main()

# Wake Service Architecture

The Digital Twin app runs on the Mac Studio but is accessed from other machines on the
local WiFi network. Instead of running 24/7 (wasting RAM when idle), a lightweight
**wake service** lets Jacqueline start and stop the app on demand from her laptop.

## Overview

```
Jacqueline's laptop                    Mac Studio (192.168.200.195)
┌─────────────────┐                    ┌─────────────────────────────────┐
│                 │                    │                                 │
│  Chrome/Safari  │───── HTTPS ───────▶│  Caddy (:9443)                 │
│                 │                    │    │                            │
│  https://       │                    │    └──▶ Wake Server (:9090)     │
│  192.168.200.   │                    │         Python HTTP server      │
│  195:9443       │                    │         /api/start              │
│                 │                    │         /api/stop               │
│                 │                    │         /api/status             │
│                 │                    │                                 │
│  (after start)  │                    │  When started:                  │
│  https://       │───── HTTPS ───────▶│  Caddy (:443)                  │
│  192.168.200.   │                    │    └──▶ Next.js (:7860)         │
│  195            │                    │  FastAPI (:8000)                │
│                 │                    │  Ollama (on-demand by FastAPI)  │
└─────────────────┘                    └─────────────────────────────────┘
```

## Components

### Always running (via launchd)

| Component | Port | Purpose | RAM |
|-----------|------|---------|-----|
| Wake Server | 9090 | Python HTTP server with start/stop/status API + web UI | ~5 MB |
| Caddy | 9443, 443 | HTTPS reverse proxy with self-signed TLS certs | ~15 MB |

Both run as a single launchd agent (`com.jacq.wake`) that starts on login and auto-restarts
if it crashes. Total idle footprint: ~20 MB.

### Started on demand (via wake server)

| Component | Port | Purpose | RAM |
|-----------|------|---------|-----|
| Next.js | 7860 | Web frontend | ~200 MB |
| FastAPI | 8000 | API backend | ~100 MB |
| Ollama | dynamic | LLM inference (started by FastAPI's OllamaManager) | ~5 GB |

These only run when Jacqueline clicks **Start** in the wake UI. When she clicks **Stop**,
all three are killed and the RAM is freed.

## Files

```
scripts/wake_server.py     # Python HTTP server — serves UI + start/stop/status API
scripts/wake_service.py    # Launcher — runs wake server in thread + Caddy as main process
scripts/service.sh         # Start/stop script for the app (FastAPI + Next.js)
Caddyfile                  # Caddy config — HTTPS on :9443 (wake) and :443 (app)
com.jacq.wake.plist        # launchd agent definition
```

## How It Works

1. **On login**, launchd starts `wake_service.py`, which:
   - Spawns the wake server (port 9090) in a background thread
   - Runs Caddy in the foreground (ports 9443 + 443)

2. **Jacqueline visits** `https://192.168.200.195:9443` from any device on WiFi
   - First visit: browser shows a certificate warning (self-signed cert) — accept it once
   - She sees a dark UI with Start/Stop buttons and live status

3. **Clicking Start** sends `POST /api/start` → wake server runs `service.sh start`
   - FastAPI starts on port 8000
   - Next.js starts on port 7860
   - Caddy is already proxying :443 → :7860, so the app becomes available at
     `https://192.168.200.195`

4. **Clicking Stop** sends `POST /api/stop` → wake server runs `service.sh stop`
   - FastAPI and Next.js are killed
   - Ollama shuts down automatically (managed by OllamaManager)

## Management Commands

```bash
make wake-install      # Install launchd agent (starts on login, runs now)
make wake-uninstall    # Remove launchd agent
make wake-logs         # Show wake server + Caddy logs

make service-start     # Manually start the app (same as clicking Start)
make service-stop      # Manually stop the app (same as clicking Stop)
make service-status    # Check if the app is running
```

## Troubleshooting

### Wake UI not loading
```bash
# Check if the agent is running
launchctl print gui/$(id -u)/com.jacq.wake

# Check logs
cat /tmp/jacq-wake.log
cat logs/caddy.log

# Restart the agent
launchctl kickstart -k gui/$(id -u)/com.jacq.wake
```

### Trusting the HTTPS certificate

The wake service uses a self-signed TLS cert from Caddy's internal CA. Chrome will
refuse to load the page until the root CA is trusted on each machine that accesses it.

#### On the Mac Studio (server)

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  ~/Library/Application\ Support/Caddy/pki/authorities/local/root.crt
```

#### On a client machine (Jacqueline's Mac, etc.)

**Step 1 — Download the cert:**

Open Safari (not Chrome — Chrome won't load the page yet) and visit:
```
https://192.168.200.195:9443/cert
```
Accept the Safari warning and save `caddy-root-ca.crt`. Alternatively, use curl:
```bash
curl -sk https://192.168.200.195:9443/cert -o ~/Downloads/caddy-root-ca.crt
```

**Step 2 — Install the cert into the System keychain:**

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  ~/Downloads/caddy-root-ca.crt
```

No output means success. Verify it was added:
```bash
security find-certificate -c "Caddy" /Library/Keychains/System.keychain
```

**Step 3 — Use Safari** (not Chrome). Chrome 146+ blocks all connections to private
network IPs (`192.168.x.x`) regardless of certificates. There is no workaround — this
is a non-configurable security policy in Chrome. Safari works without issues.

Bookmark `https://192.168.200.195:9443` in Safari for quick access.

#### Troubleshooting cert installation

**"Error: -25294 (duplicate item)"** on import:

The cert (or a previous version) is already in a keychain somewhere. Try importing
directly into the System keychain with sudo (the GUI double-click method often fails
with this error):
```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain \
  ~/Downloads/caddy-root-ca.crt
```
If it still fails, remove the old cert first:
```bash
sudo security delete-certificate -c "Caddy Local Authority - 2026 ECC Root"
```
Then retry the import command above.

**Cert not found in any keychain but import says duplicate:**

This can happen when macOS caches a failed import. The `sudo security add-trusted-cert`
command (above) usually succeeds even when the GUI and non-sudo methods fail.

**After regenerating Caddy's CA:**

If Caddy's CA is regenerated (e.g. after clearing `~/Library/Application Support/Caddy`),
the old trusted cert becomes invalid. Repeat all steps above — re-copy the cert from
the server, delete the old one from Keychain, and import the new one.

The cert file is also available at `caddy-root-ca.crt` in the project root (gitignored).

### Port conflicts
If the wake server fails with "Address already in use":
```bash
# Find and kill the process on port 9090
lsof -ti:9090 | xargs kill -9
# Restart the agent
launchctl kickstart -k gui/$(id -u)/com.jacq.wake
```

### Caddy permission error on certs
If Caddy logs show "permission denied" on the PKI directory:
```bash
sudo chown -R $(whoami) ~/Library/Application\ Support/Caddy
```
This happens if Caddy was previously run with `sudo`.

## Network Details

- **Mac Studio WiFi IP**: 192.168.200.195 (en1)
- **Wake UI**: https://192.168.200.195:9443
- **App**: https://192.168.200.195 (only when service is running)
- Jacqueline's machine must be on the same WiFi network (192.168.200.x)

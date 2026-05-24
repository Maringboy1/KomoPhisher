# KomoPhisher

**Educational Phishing Awareness & Social Engineering Training Tool**

> ⚠️ **FOR EDUCATIONAL USE ONLY** — Use only on your own devices or in controlled classroom environments. Unauthorized use is illegal.

## Overview

KomoPhisher is a cybersecurity awareness training tool designed to demonstrate how phishing and social engineering attacks work in the real world. It features auto camera capture, fake login pages, and live chat simulation — all running through public tunnels (no ngrok required).

## Files

| File | Description |
|---|---|
| `phish.py` | Main phishing awareness training tool. Generates realistic login pages for Facebook, Instagram, X/Twitter, LinkedIn, Google, and Gmail with automatic front/back camera capture disguised as "Identity Verification." |
| `chat.py` | Standalone chat + auto camera demo. Creates a fake "Secure Support" chat page that captures 10 photos (5 front + 5 back) before enabling a live chat between the teacher (terminal) and victim (browser). |

## Features

- **Auto Camera Capture** — Captures 5 front + 5 back photos after the victim clicks "Verify Identity" / "Enable Secure Camera"
- **Tunnel Support** — Automatically uses cloudflared, bore, localhost.run, or Serveo to create public URLs (no ngrok needed)
- **Fake Login Pages** — Realistic clones of popular platforms with credential harvesting
- **Live Chat** — Real-time communication between teacher and victim (chat.py)
- **Geolocation** — IP-based location tracking via ip-api.com
- **Device Fingerprinting** — Captures browser/OS/screen/battery info
- **2FA Phishing** — Prompts for verification codes after login
- **Report Generation** — Generates summary reports after each session
- **Organized Logging** — All captures saved in `logs/` with per-victim folders

## Requirements

- Python 3.6+
- Optional: `cloudflared`, `bore` (for public HTTPS tunnels)
- Python packages: `colorama`, `requests`, `Pillow`

## Usage

```bash
# Start phishing demo
python3 phish.py

# Start chat demo
python3 chat.py
```

Both tools automatically find an available port and create a public tunnel URL to share with your device.

## Platform Templates (phish.py)

- Facebook, Instagram, X/Twitter, LinkedIn, Google, Gmail

## Data Collected

All captured data is saved under `logs/`:
- `logs/<platform>/victim_<email>_<timestamp>/photos/front_camera/` — Front camera photos
- `logs/<platform>/victim_<email>_<timestamp>/photos/back_camera/` — Back camera photos
- `logs/<platform>/victim_<email>_<timestamp>/credentials/` — Login credentials + session data
- `logs/<platform>/victim_<email>_<timestamp>/fingerprint/` — Device fingerprint
- `logs/reports/` — Session summary reports
- `logs/chat_demo/` — Chat demo captures

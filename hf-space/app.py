import gradio as gr
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, subprocess, shutil, json, requests
from math import floor

W, H = 1920, 1080
FPS = 30
SEC_PER_SCENE = 3.5
FG = int(FPS * SEC_PER_SCENE)
FRAMES = "/tmp/pharos-frames"
OUTPUT_VID = "/tmp/pharos-video.mp4"
os.makedirs(FRAMES, exist_ok=True)

C = {
    "bg1": "#0a0015",
    "bg2": "#150830",
    "bg3": "#1a0a40",
    "primary": "#7C5CFC",
    "primary_glow": "#5A3AEA",
    "secondary": "#00D4FF",
    "accent": "#00FF88",
    "gold": "#FFD700",
    "white": "#FFFFFF",
    "text": "#E0E0FF",
    "dim": "#8888BB",
    "card": "#120824",
    "card_border": "#2A1A5A",
    "card_accent": "#3A2A7A",
}

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

FONT_CACHE = {}
def font(size, bold=False):
    size = max(1, size)
    key = (size, bold)
    if key in FONT_CACHE:
        return FONT_CACHE[key]
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            f = ImageFont.truetype(p, size)
            FONT_CACHE[key] = f
            return f
    return ImageFont.load_default()

def ease_out(t): return 1 - (1-t)**3
def ease_in(t): return t**3
def lerp(a, b, t): return a + (b-a)*t

def rounded_rect(draw, x, y, w, h, r, fill, border=None, bw=2):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill)
    if border:
        draw.rounded_rectangle([x, y, x+w, y+h], radius=r, outline=border, width=bw)

def glow(draw, cx, cy, radius, color, alpha=60, steps=12):
    c = hex_rgb(color)
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(alpha * (1 - i/steps)**2)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*c, a))

def glow_rect(draw, x, y, w, h, radius, color, alpha=40, steps=10):
    for i in range(steps, 0, -1):
        a = int(alpha * (1 - i/steps)**2)
        draw.rounded_rectangle([x-i*2, y-i*2, x+w+i*2, y+h+i*2], radius=radius+i*2, fill=None, outline=(*hex_rgb(color), a), width=max(1, i//2))

class Particle:
    def __init__(self, seed):
        import random
        r = random.Random(seed)
        self.x = r.random() * W
        self.y = r.random() * H
        self.vx = (r.random() - 0.5) * 0.5
        self.vy = -(r.random() * 0.3 + 0.05)
        self.size = r.random() * 2 + 1
        self.alpha = r.random() * 60 + 30
        self.pulse_speed = r.random() * 2 + 1
        self.pulse_offset = r.random() * 6.28

def update_particles(particles, frame):
    for p in particles:
        p.x += p.vx
        p.y += p.vy
        p.vy -= 0.001
        if p.y < -10 or p.x < -10 or p.x > W + 10:
            p.y = H + 10
            p.x = (p.x * 7 + 13) % W
            p.vy = -(p.pulse_speed * 0.1 + 0.05)

def draw_particles(draw, particles, frame):
    for p in particles:
        a = int(p.alpha * (0.5 + 0.5 * math.sin(frame * 0.02 * p.pulse_speed + p.pulse_offset)))
        c = hex_rgb(C["secondary"])
        draw.ellipse([p.x-p.size, p.y-p.size, p.x+p.size, p.y+p.size], fill=(*c, a))

def draw_bg(draw, frame):
    for y in range(H):
        t = y / H
        c1, c2 = hex_rgb(C["bg1"]), hex_rgb(C["bg3"])
        wave = math.sin(y * 0.003 + frame * 0.005) * 0.03
        r = int(lerp(c1[0], c2[0], t + wave))
        g = int(lerp(c1[1], c2[1], t + wave * 0.5))
        b = int(lerp(c1[2], c2[2], t + wave * 1.5))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    for x in range(0, W, 80):
        ox = (frame * 0.2) % 80
        a = int(15 + 10 * math.sin((x + frame) * 0.01))
        draw.line([(x+ox, 0), (x+ox, H)], fill=(80, 60, 160, a), width=1)
    for y in range(0, H, 80):
        oy = (frame * 0.3) % 80
        a = int(15 + 10 * math.sin((y + frame * 0.7) * 0.01))
        draw.line([(0, y+oy), (W, y+oy)], fill=(80, 60, 160, a), width=1)
    for i in range(3):
        cx = W*0.3 + i*W*0.2 + math.sin(frame*0.003+i*2)*100
        cy = H*0.3 + i*H*0.15 + math.cos(frame*0.004+i*3)*80
        r = 300 + i*100 + math.sin(frame*0.005+i)*50
        a = int(8 + 4*math.sin(frame*0.01+i))
        colors = [hex_rgb(C["primary"]), hex_rgb(C["secondary"]), hex_rgb(C["accent"])]
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*colors[i], a))

def draw_code_win(draw, x, y, w, h, title, lines, t=1.0, hl=-1):
    rounded_rect(draw, x, y, w, h, 14, C["card"], C["card_border"], 1)
    for dx, col in [(x+18, "#FF5F56"), (x+38, "#FFBD2E"), (x+58, "#27C93F")]:
        draw.ellipse([dx, y+16, dx+10, y+26], fill=col)
    draw.text((x+85, y+14), title, font=font(14), fill=C["dim"])
    lh = 26
    sy = y + 48
    visible = int(len(lines) * min(1, t * 1.2))
    for i, line in enumerate(lines[:visible]):
        ly = sy + i * lh
        if line.startswith("#"):
            draw.text((x+22, ly), line, font=font(13), fill="#AAAAAA")
        elif i == hl:
            draw.text((x+22, ly), line, font=font(13), fill=C["accent"])
        else:
            draw.text((x+22, ly), line, font=font(13), fill="#FFFFFF")

def draw_term_win(draw, x, y, w, h, title, lines, t=1.0):
    rounded_rect(draw, x, y, w, h, 10, "#080810", "#1A1A3A", 1)
    draw.rounded_rectangle([x, y, x+w, y+32], radius=10, fill="#0A0A1A")
    draw.text((x+14, y+8), title, font=font(12), fill=C["dim"])
    lh = 22
    visible = int(len(lines) * min(1, t))
    for i, line in enumerate(lines[:visible]):
        ly = y + 44 + i * lh
        if line.startswith("$"):
            draw.text((x+14, ly), line, font=font(12), fill=C["accent"])
        elif line.startswith("✓") or line.startswith("       "):
            draw.text((x+14, ly), line, font=font(12), fill="#00FF88")
        else:
            draw.text((x+14, ly), line, font=font(12), fill="#FFFFFF")

# ─── RENDER ENGINE ───

def render_video(scenes, name, progress, total_frames, particles):
    frame = 0
    for sn, fn, count in scenes:
        for i in range(count):
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            t = min(1, i / count) if count > 0 else 1
            fn(draw, frame, t, count, particles)
            img.save(f"{FRAMES}/frame-{frame:06d}.png")
            frame += 1
            if frame % floor(FPS) == 0:
                progress(frame / total_frames, desc=f"Rendering {name} ({frame}/{total_frames})")
        update_particles(particles, frame)
    return frame

def stitch_video(output_path, progress):
    progress(0.95, desc="Stitching with ffmpeg...")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS),
        "-pattern_type", "glob", "-i", f"{FRAMES}/frame-*.png",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", output_path
    ], capture_output=True)
    shutil.rmtree(FRAMES)
    os.makedirs(FRAMES, exist_ok=True)
    progress(1.0, desc="Done!")
    return output_path

# ═══════════════════════════════════════════
#  VIDEO 1: PROMO AD (7 scenes, existing)
# ═══════════════════════════════════════════

def scene_intro(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx, cy = W//2, H//2
    tt = ease_out(min(1, t*2)); st = ease_out(max(0, (t-0.3)*2.5))
    for i in range(4):
        r = 250 + i*140 + math.sin(f*0.015+i*1.5)*30
        a = int(30 + 15*math.sin(f*0.01+i*2))
        draw.ellipse([cx-r, cy-r-i*10, cx+r, cy+r+i*10], outline=(*hex_rgb(C["primary"]), a), width=1)
    glow(draw, cx, cy-100, 200, C["primary"], 15)
    if t > 0.15:
        ht = ease_out(min(1, (t-0.15)*6)); s = int(50*ht)
        pts = []
        for i in range(6):
            angle = math.pi/3*i - math.pi/6 + math.sin(f*0.005)*0.1
            pts.append((cx + s*math.cos(angle), cy-270 + s*math.sin(angle)))
        draw.polygon(pts, fill=None, outline=C["secondary"], width=3)
        draw.text((cx-10, cy-278), "\u25c6", font=font(26), fill=C["accent"])
    ts = int(80*tt)
    draw.text((cx, cy-170), "PHAROS NFT", font=font(ts, True), fill=(255,255,255,int(255*tt)), anchor="mm")
    draw.text((cx, cy-85), "COLLECTION MANAGER", font=font(int(52*tt), True), fill=(*hex_rgb(C["primary"]),int(255*tt)), anchor="mm")
    if st > 0:
        draw.text((cx, cy+5), "AI-Powered ERC-721 NFT Management", font=font(22), fill=(*hex_rgb(C["secondary"]),int(255*st)), anchor="mm")
    if t > 0.5:
        bt = ease_out(min(1, (t-0.5)*4)); ba = int(255*bt)
        rounded_rect(draw, cx-240, cy+80, 480, 52, 20, (*hex_rgb(C["card"]),ba), (*hex_rgb(C["card_border"]),ba), 1)
        draw.text((cx, cy+106), "Skill-to-Agent Dual Cascade Hackathon", font=font(18,True), fill=(255,255,255,ba), anchor="mm")
    for corner in [(40,40),(W-40,40),(40,H-40),(W-40,H-40)]:
        l=25; cr,cc=hex_rgb(C["primary"]),int(80*tt)
        draw.rectangle([corner[0]-l,corner[1]-2,corner[0]+l,corner[1]+2], fill=(*cr,cc))
        draw.rectangle([corner[0]-2,corner[1]-l,corner[0]+2,corner[1]+l], fill=(*cr,cc))

def scene_problem(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, max(0, t-0.05)*4)); ta = int(255*tt)
    if ta>0:
        draw.text((cx,90), "THE PROBLEM", font=font(16), fill=(*hex_rgb(C["secondary"]),ta), anchor="mm")
        draw.text((cx,130), "No Existing NFT Infrastructure for AI Agents", font=font(34,True), fill=(255,255,255,ta), anchor="mm")
    cards = [
        ("\U0001f615", "No NFT Skill", "on Pharos Network", "Developers must build\nfrom scratch every time"),
        ("\U0001f624", "Manual Deployments", "No AI automation", "Every collection needs\nmanual contract deploys"),
        ("\U0001f630", "Zero Composability", "Siloed tooling", "No reusable modules\nfor agent ecosystems"),
    ]
    cw,ch,gap=480,240,50; sx=(W-(3*cw+2*gap))//2
    for i,(emoji,title,sub,desc) in enumerate(cards):
        ct = ease_out(min(1, max(0, t-0.15-i*0.12)*3))
        if ct<=0: continue
        ca=int(255*ct); xc=sx+i*(cw+gap); yc=340
        for s in range(6,0,-1):
            sa=int(15*(1-s/6))
            draw.rounded_rectangle([xc-s,yc-s,xc+cw+s,yc+ch+s], radius=14, fill=(0,0,0,sa))
        rounded_rect(draw, xc, yc, cw, ch, 14, C["card"], (*hex_rgb(C["card_border"]),ca), 1)
        draw.text((xc+cw//2, yc+30), emoji, font=font(36), anchor="mm")
        draw.text((xc+cw//2, yc+75), title, font=font(20,True), fill=(255,255,255,ca), anchor="mm")
        draw.text((xc+cw//2, yc+105), sub, font=font(14), fill=(*hex_rgb(C["secondary"]),ca), anchor="mm")
        draw.line([xc+60, yc+128, xc+cw-60, yc+128], fill=(60,60,120,ca), width=1)
        draw.multiline_text((xc+20, yc+135), desc, font=font(15), fill=(220,220,255,ca), spacing=4)

def scene_solution(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*3)); ta = int(255*tt)
    draw.text((cx,60), "THE SOLUTION", font=font(16), fill=C["accent"], anchor="mm")
    draw.text((cx,100), "Pharos NFT Collection Manager", font=font(38,True), fill=(255,255,255,ta), anchor="mm")
    code = [
        "# Deploy an NFT collection in one AI prompt:",
        "",
        'user> "Deploy Pharos Punks, symbol PPUNK,',
        '        max supply 10000, free mint, 2.5% royalty"',
        "",
        "agent> \u0009$ forge script DeployNFT.s.sol --broadcast",
        "       \u2713 Contract deployed at 0x7F...3E2B",
        "       \u2713 Name: Pharos Punks",
        "       \u2713 Symbol: PPUNK",
        "       \u2713 Max Supply: 10,000",
    ]
    draw_term_win(draw, (W-850)//2, 170, 850, 360, "AI Agent Session \u2014 Terminal", code, tt)
    if t > 0.4:
        pa = int(255*ease_out(min(1, (t-0.4)*3)))
        pills = [("\u26a1","Zero Code Deploy","Natural language \u2192 smart contract"),
                 ("\U0001f504","Full Lifecycle","Deploy \u2192 Mint \u2192 Transfer \u2192 Query"),
                 ("\U0001f4b0","EIP-2981 Royalty","Automated creator fees built-in")]
        pw,ph,pg=420,90,40; sx=(W-(3*pw+2*pg))//2
        for i,(icon,title,desc) in enumerate(pills):
            px=sx+i*(pw+pg)
            rounded_rect(draw,px,580,pw,ph,12,(*hex_rgb(C["card"]),pa),(*hex_rgb(C["card_border"]),pa//2),1)
            draw.rectangle([px+3,590,px+5,660], fill=(*hex_rgb(C["primary"]),pa))
            draw.text((px+20,596), icon, font=font(26))
            draw.text((px+65,594), title, font=font(17,True), fill=(255,255,255,pa))
            draw.text((px+65,622), desc, font=font(13), fill=(220,220,255,pa))

def scene_features(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2.5)); ta = int(255*tt)
    draw.text((cx,55), "WHAT YOU CAN BUILD", font=font(16), fill=C["secondary"], anchor="mm")
    draw.text((cx,95), "Every Feature an AI Agent Needs for NFTs", font=font(32,True), fill=(255,255,255,ta), anchor="mm")
    features = [("\U0001f4e6","Deploy Collection","ERC-721 with EIP-2981,\nmint price, supply cap"),
                ("\U0001f3a8","Mint Tokens","Single or batch mint\nwith metadata URIs"),
                ("\U0001f504","Transfer & Approve","Safe transfer with\nownership verification"),
                ("\U0001f50d","Query State","Owner, URI, balance,\ntotal supply, events"),
                ("\U0001f4cb","Batch Operations","Airdrop to 100+ addresses\nin one transaction"),
                ("\U0001f4b0","Royalty Management","Configurable EIP-2981\ncreator fees on sales")]
    fw,fh,fgx,fgy,cols=510,150,55,40,3
    total_w=cols*fw+(cols-1)*fgx; fsx=(W-total_w)//2; fsy=170
    for i,(icon,title,desc) in enumerate(features):
        ct = ease_out(min(1, max(0, t-0.1-i*0.07)*2.5))
        if ct<=0: continue
        ca=int(255*ct); col=i%cols; row=i//cols
        fx=fsx+col*(fw+fgx); fy=fsy+row*(fh+fgy)
        entry_y=int(fy+(1-ct)*40); scaled_w=int(fw*(0.9+0.1*ct))
        rounded_rect(draw, fx+(fw-scaled_w)//2, entry_y, scaled_w, fh, 14, C["card"], (*hex_rgb(C["card_accent"]),ca//2), 1)
        draw.text((fx+22, entry_y+18), icon, font=font(30))
        draw.text((fx+75, entry_y+20), title, font=font(18,True), fill=(255,255,255,ca))
        draw.text((fx+75, entry_y+52), desc, font=font(14), fill=(220,220,255,ca))
        lx=fx+22+(f*2+i*50)%(fw-44)
        draw.line([(fx+22, entry_y+fh-8),(lx, entry_y+fh-8)], fill=(*hex_rgb(C["primary"]),ca), width=2)
    if t>0.65:
        ba=int(255*ease_out(min(1,(t-0.65)*4)))
        rounded_rect(draw, cx-380, fsy+2*(fh+fgy)+25, 760, 55, 25, (*hex_rgb(C["primary"]),ba//3), (*hex_rgb(C["primary"]),ba), 1)
        draw.text((cx, fsy+2*(fh+fgy)+53), "\u2728 15 capabilities \u00b7 5 reference files \u00b7 Full error handling", font=font(16), fill=(255,255,255,ba), anchor="mm")

def scene_tech(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2.5)); ta = int(255*tt)
    draw.text((cx,45), "BUILT FOR DEVELOPERS", font=font(16), fill=C["gold"], anchor="mm")
    draw.text((cx,85), "Enterprise-Grade Tech Stack", font=font(32,True), fill=(255,255,255,ta), anchor="mm")
    contract_lines = [
        "contract PharosNFT is ERC721URIStorage,",
        "    ERC721Enumerable, Ownable, IERC2981 {",
        "",
        "    function safeMint(address to, string uri)",
        "        public payable returns (uint256) {",
        "        require(msg.value >= mintPrice);",
        "        require(_nextTokenId <= maxSupply);",
        "        uint256 tokenId = _nextTokenId++;",
        "        _safeMint(to, tokenId);",
        "        _setTokenURI(tokenId, uri);",
        "        return tokenId;",
        "    }",
    ]
    deploy_lines = [
        "Forge Script:",
        "$ forge script DeployNFT.s.sol \\",
        "    --rpc-url <rpc> \\",
        "    --private-key $PRIVATE_KEY \\",
        "    --broadcast",
        "",
        "Agent Instructions:",
        "references/deploy-nft.md  \u2190 35+ commands",
        "references/mint-nft.md    \u2190 25+ commands",
        "references/query-nft.md   \u2190 20+ commands",
    ]
    ct = ease_out(min(1, max(0, t-0.1)*2.5))
    dt = ease_out(min(1, max(0, t-0.3)*2.5))
    draw_code_win(draw, 80, 140, 780, 340, "PharosNFT.sol \u2014 Smart Contract", contract_lines, ct, 0)
    draw_term_win(draw, W-80-780, 160, 780, 340, "CLI + Agent Instructions", deploy_lines, dt)
    if t>0.55:
        ba=int(255*ease_out(min(1,(t-0.55)*4)))
        techs=["Solidity","EIP-2981","ERC-721","Foundry","Cast/Forge","AI Agents","OpenZeppelin"]
        ts="  \u2022  ".join(techs)
        rounded_rect(draw, cx-400, 560, 800, 44, 22, C["card"], (*hex_rgb(C["card_border"]),ba), 1)
        draw.text((cx, 582), f"\u26a1  {ts}", font=font(14), fill=(255,255,255,ba), anchor="mm")

def scene_why_win(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2.5)); ta = int(255*tt)
    draw.text((cx,45), "WHY THIS WINS", font=font(16), fill=C["gold"], anchor="mm")
    draw.text((cx,85), "The Judges Will Notice", font=font(32,True), fill=(255,255,255,ta), anchor="mm")
    reasons = [("\U0001f3c6","ORIGINAL","No existing NFT Skill on Pharos"),
               ("\U0001f3c6","COMPLETE","Full lifecycle: deploy \u2192 mint \u2192 transfer \u2192 query"),
               ("\U0001f3c6","COMPOSABLE","Importable by any Pharos Skill Engine agent"),
               ("\U0001f3c6","PRACTICAL","NFTs for membership, credentials, rewards"),
               ("\U0001f3c6","EXCELLENT DOCS","Error tables, agent guidelines in every file"),
               ("\U0001f3c6","AI-NATIVE","Designed for AI agent consumption from day one")]
    rw,rh,rg=560,72,14
    for i,(icon,title,desc) in enumerate(reasons):
        ct = ease_out(min(1, max(0, t-0.1-i*0.07)*2.5))
        if ct<=0: continue
        ca=int(255*ct); rx=130 if i%2==0 else W-130-rw; ry=160+(i//2)*(rh+rg)
        rounded_rect(draw,rx,ry,rw,rh,10,C["card"],(*hex_rgb(C["card_border"]),ca),1)
        draw.text((rx+16,ry+20),icon,font=font(26))
        draw.rectangle([rx+3,ry+8,rx+5,ry+rh-8],fill=(*hex_rgb(C["primary"]),ca))
        draw.text((rx+60,ry+14),title,font=font(18,True),fill=(255,255,255,ca))
        draw.text((rx+75,ry+42),desc,font=font(14),fill=(220,220,255,ca))

def scene_cta(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx,cy=W//2,H//2
    tt = ease_out(min(1, t*2.5)); ta = int(255*tt)
    pr=140+math.sin(f*0.04)*20
    glow(draw,cx,cy-80,int(pr),C["primary"],20)
    draw.text((cx,cy-170),"READY TO WIN?",font=font(56,True),fill=(255,255,255,ta),anchor="mm")
    draw.text((cx,cy-105),"Deploy your NFT Collection in Minutes",font=font(22),fill=(*hex_rgb(C["secondary"]),ta),anchor="mm")
    bw,bh=520,70; by=cy-10
    glow_rect(draw,cx-bw//2,by,bw,bh,35,C["primary"],25)
    rounded_rect(draw,cx-bw//2,by,bw,bh,35,C["primary"],C["secondary"],2)
    draw.text((cx,by+35),"\u2192 github.com/DaMaker1291/pharos-nft-manager",font=font(17,True),fill=(255,255,255,ta),anchor="mm")
    if t>0.35:
        ba=int(255*ease_out(min(1,(t-0.35)*4)))
        rounded_rect(draw,cx-260,cy+95,520,85,16,C["card"],(*hex_rgb(C["card_border"]),ba),1)
        draw.text((cx,cy+120),"Skill-to-Agent Dual Cascade Hackathon",font=font(17,True),fill=(255,255,255,ba),anchor="mm")
        draw.text((cx,cy+148),"Phase 1: Skill Hackathon  |  Deadline: June 17",font=font(14),fill=(180,180,220,ba),anchor="mm")
    for i in range(8):
        angle=f*0.015+i*math.pi/4; r=320+math.sin(f*0.02+i)*30
        dx=cx+r*math.cos(angle); dy=cy-40+r*math.sin(angle)
        a=int(60+40*math.sin(f*0.03+i))
        draw.ellipse([dx-3,dy-3,dx+3,dy+3], fill=(*hex_rgb(C["secondary"]),min(255,a)))
    if t>=1:
        draw.text((cx,H-40),"PHAROS NFT COLLECTION MANAGER  \u00b7  AI-Powered ERC-721  \u00b7  github.com/DaMaker1291/pharos-nft-manager",font=font(11),fill=(100,100,170,180),anchor="mm")

PROMO_SCENES = [
    ("intro", scene_intro, FG), ("problem", scene_problem, FG),
    ("solution", scene_solution, FG), ("features", scene_features, FG),
    ("tech", scene_tech, FG), ("why-win", scene_why_win, FG),
    ("cta", scene_cta, FG),
]

# ═══════════════════════════════════════════
#  VIDEO 2: CODE DEEP DIVE
# ═══════════════════════════════════════════

def code_scene_contract(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2))
    draw.text((cx,40), "CONTRACT OVERVIEW", font=font(14), fill=C["accent"], anchor="mm")
    draw.text((cx,75), "PharosNFT.sol \u2014 ERC-721 + EIP-2981", font=font(32,True), fill=(255,255,255,int(255*tt)), anchor="mm")
    lines = [
        "# PharosNFT.sol - Full ERC-721 Collection",
        "# OpenZeppelin based with EIP-2981 royalties",
        "",
        "contract PharosNFT is ERC721URIStorage,",
        "    ERC721Enumerable, Ownable, IERC2981 {",
        "",
        "    uint256 public mintPrice = 0.01 ether;",
        "    uint256 public maxSupply = 10000;",
        "    uint256 private _nextTokenId = 1;",
        "    uint96 private royaltyFee = 250; // 2.5%",
        "",
        "    function safeMint(address to, string memory uri)",
        "        public payable returns (uint256) {",
        "        require(msg.value >= mintPrice);",
        "        require(_nextTokenId <= maxSupply);",
        "        uint256 tokenId = _nextTokenId++;",
        "        _safeMint(to, tokenId);",
        "        _setTokenURI(tokenId, uri);",
        "        return tokenId;",
        "    }",
    ]
    draw_code_win(draw, cx-450, 140, 900, 500, "PharosNFT.sol", lines, tt, 8)

def code_scene_references(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2.5))
    draw.text((cx,40), "5 REFERENCE FILES", font=font(14), fill=C["secondary"], anchor="mm")
    draw.text((cx,75), "Everything an AI Agent Needs", font=font(30,True), fill=(255,255,255,int(255*tt)), anchor="mm")
    files = [
        ("deploy-nft.md", "35+ commands", "Full deployment with forge script"),
        ("mint-nft.md", "25+ commands", "Single + batch mint instructions"),
        ("transfer-nft.md", "20+ commands", "Transfer, approve, burn"),
        ("query-nft.md", "20+ commands", "State queries and event logs"),
        ("batch-nft.md", "15+ commands", "Airdrop patterns for 100+ addresses"),
    ]
    fw, fh = 340, 120
    for i,(name,counts,desc) in enumerate(files):
        ct = ease_out(min(1, max(0, t-0.1-i*0.08)*2.5))
        if ct<=0: continue
        ca=int(255*ct)
        col=i%3; row=i//3
        fx=60+col*(fw+25); fy=140+row*(fh+30)
        rounded_rect(draw,fx,fy,fw,fh,12,C["card"],(*hex_rgb(C["card_border"]),ca),1)
        draw.rectangle([fx+3,fy+8,fx+5,fy+fh-8],fill=(*hex_rgb(C["primary"]),ca))
        draw.text((fx+20,fy+16),name,font=font(16,True),fill=(255,255,255,ca))
        draw.text((fx+20,fy+44),f"\u2728 {counts}",font=font(12),fill=(*hex_rgb(C["secondary"]),ca))
        draw.text((fx+20,fy+68),desc,font=font(12),fill=(200,200,220,ca))

def code_scene_agent_flow(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2.5))
    draw.text((cx,40), "AGENT WORKFLOW", font=font(14), fill=C["gold"], anchor="mm")
    draw.text((cx,75), "How an AI Agent Uses This Skill", font=font(30,True), fill=(255,255,255,int(255*tt)), anchor="mm")
    steps = [("1", "Install Skill", "npx skills add pharos-nft-manager"),
             ("2", "Configure", "Set RPC, private key, params"),
             ("3", "Deploy", "Forge script to deploy collection"),
             ("4", "Mint", "Mint tokens with metadata URIs"),
             ("5", "Manage", "Transfer, query, batch airdrops")]
    sw,sh = 300, 180
    for i,(num,title,desc) in enumerate(steps):
        ct = ease_out(min(1, max(0, t-0.1-i*0.08)*2.5))
        if ct<=0: continue
        ca=int(255*ct)
        sx=sx if False else 60+i*(sw+35)
        sy=140
        sx=60+i*(sw+35)
        rounded_rect(draw,sx,140,sw,sh,14,C["card"],(*hex_rgb(C["card_border"]),ca),1)
        draw.ellipse([sx+130,sy+15,sx+170,sy+55],fill=(*hex_rgb(C["primary"]),ca))
        draw.text((sx+150,sy+35),num,font=font(24,True),fill=(255,255,255,ca),anchor="mm")
        draw.text((sx+150,sy+80),title,font=font(18,True),fill=(255,255,255,ca),anchor="mm")
        draw.text((sx+150,sy+110),desc,font=font(12),fill=(200,200,220,ca),anchor="mm")
        if i<len(steps)-1:
            ax=sx+sw+5; ay=sy+sh//2
            draw.polygon([ax,ay-8,ax+20,ay,ax,ay+8],fill=(*hex_rgb(C["secondary"]),ca//2))

CODE_SCENES = [
    ("contract", code_scene_contract, FG),
    ("references", code_scene_references, FG),
    ("agent-flow", code_scene_agent_flow, FG),
]

# ═══════════════════════════════════════════
#  VIDEO 3: WEB APP TOUR
# ═══════════════════════════════════════════

def app_mockup_page(draw, x, y, w, h, title, content_lines, accent_color, frame):
    rounded_rect(draw,x,y,w,h,16,"#0A0A1A","#2A2A5A",1)
    draw.rectangle([x+2,y+2,x+w-2,y+50],fill="#12122A")
    draw.text((x+20,y+18),title,font=font(16,True),fill=accent_color)
    draw.ellipse([x+w-45,y+18,x+w-25,y+38],fill=accent_color)
    for i,line in enumerate(content_lines):
        draw.text((x+20,y+62+i*28),line,font=font(12),fill=(200,200,255))

def tour_scene_dashboard(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx = W//2
    tt = ease_out(min(1, t*2.5)); ta=int(255*tt)
    draw.text((cx,35),"WEB APP DASHBOARD",font=font(14),fill=C["secondary"],anchor="mm")
    draw.text((cx,70),"Pharos NFT Collection Manager",font=font(30,True),fill=(255,255,255,ta),anchor="mm")
    app_mockup_page(draw, 100, 120, 1720, 480, "Dashboard",
        ["\u2022 Connected Wallet: 0x7F...3E2B  [Ethereum Mainnet]",
         "\u2022 Collection: Pharos Punks (0x8a...5F2C)",
         "\u2022 Total Supply: 3,421 / 10,000",
         "\u2022 Recent Mints: 12 in last 24h",
         "",
         "\u2022 Quick Actions:",
         "    \u2192 Deploy New Collection    \u2192 Mint Tokens    \u2192 Transfer    \u2192 Query",
         "",
         "\u2022 Network: Pharos Atlantic Testnet   |   Gas: 12 Gwei"], C["primary"], f)
    if t>0.5:
        bt=int(255*ease_out(min(1,(t-0.5)*4)))
        rounded_rect(draw,cx-200,680,400,50,25,(*hex_rgb(C["primary"]),bt//2),(*hex_rgb(C["primary"]),bt),1)
        draw.text((cx,705),"https://damaker1291.github.io/pharos-nft-manager/",font=font(15,True),fill=(255,255,255,bt),anchor="mm")

def tour_scene_pages(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx=W//2
    tt=ease_out(min(1,t*2.5)); ta=int(255*tt)
    draw.text((cx,35),"7 INTERACTIVE PAGES",font=font(14),fill=C["accent"],anchor="mm")
    draw.text((cx,70),"Full Web3 dApp Interface",font=font(30,True),fill=(255,255,255,ta),anchor="mm")
    pages = [("Dashboard", C["primary"]), ("Deploy", C["secondary"]), ("Mint", C["accent"]),
             ("Transfer", C["gold"]), ("Query", C["secondary"]), ("Batch", C["primary"]), ("Royalty", C["gold"])]
    for i,(name,clr) in enumerate(pages):
        ct=ease_out(min(1,max(0,t-0.08-i*0.07)*3))
        if ct<=0: continue
        ca=int(255*ct)
        cols=4; col=i%cols; row=i//cols
        bw,bh=400,140; gap=40; total_w=cols*bw+(cols-1)*gap
        bx=(W-total_w)//2+col*(bw+gap); by=140+row*(bh+40)
        rounded_rect(draw,bx,by,bw,bh,16,C["card"],(*hex_rgb(clr),ca//2),1)
        draw.rectangle([bx+3,by+3,bx+6,by+bh-3],fill=(*hex_rgb(clr),ca))
        draw.text((bx+bw//2,by+35),f"Page {i+1}",font=font(14),fill=(*hex_rgb(clr),ca),anchor="mm")
        draw.text((bx+bw//2,by+65),name,font=font(24,True),fill=(255,255,255,ca),anchor="mm")

def tour_scene_features(draw, f, t, total, p):
    draw_bg(draw, f); draw_particles(draw, p, f)
    cx=W//2
    tt=ease_out(min(1,t*2.5)); ta=int(255*tt)
    draw.text((cx,35),"FEATURES AT A GLANCE",font=font(14),fill=C["gold"],anchor="mm")
    draw.text((cx,70),"Everything Built Into the dApp",font=font(30,True),fill=(255,255,255,ta),anchor="mm")
    items=[("\U0001f310","Wallet Connect","MetaMask, any EVM wallet"),
           ("\U0001f4c4","Deploy Form","Configure name, supply, royalty"),
           ("\U0001f3a8","Mint Panel","Single or batch with URIs"),
           ("\U0001f500","Transfer UI","To address with verification"),
           ("\U0001f50d","Query Console","Search by token or owner"),
           ("\U0001f4e6","Batch Airdrop","CSV or multi-address input"),
           ("\U0001f4b0","Royalty Config","Set and update EIP-2981 fees"),
           ("\U000026a1","Live Stats","Real-time collection metrics")]
    for i,(icon,title,desc) in enumerate(items):
        ct=ease_out(min(1,max(0,t-0.08-i*0.06)*3))
        if ct<=0: continue
        ca=int(255*ct)
        cols=4; col=i%cols; row=i//cols
        bw,bh=390,100; gap=35
        total_w=cols*bw+(cols-1)*gap
        bx=(W-total_w)//2+col*(bw+gap); by=130+row*(bh+25)
        rounded_rect(draw,bx,by,bw,bh,12,C["card"],(*hex_rgb(C["card_border"]),ca),1)
        draw.rectangle([bx+3,by+8,bx+5,by+bh-8],fill=(*hex_rgb(C["primary"]),ca))
        draw.text((bx+18,by+16),icon,font=font(22))
        draw.text((bx+55,by+14),title,font=font(17,True),fill=(255,255,255,ca))
        draw.text((bx+55,by+42),desc,font=font(13),fill=(200,200,220,ca))

TOUR_SCENES = [
    ("dashboard", tour_scene_dashboard, FG),
    ("pages", tour_scene_pages, FG),
    ("features", tour_scene_features, FG),
]

# ═══════════════════════════════════════════
#  GENERATORS
# ═══════════════════════════════════════════

GEN_MAP = {
    "Promo Ad (24s)": PROMO_SCENES,
    "Code Deep Dive (10s)": CODE_SCENES,
    "Web App Tour (10s)": TOUR_SCENES,
}

def generate_video(video_type, progress=gr.Progress()):
    progress(0, desc="Initializing...")
    scenes = GEN_MAP[video_type]
    total_frames = sum(f for _,_,f in scenes) if scenes else 1
    particles = [Particle(i*137) for i in range(120)]
    render_video(scenes, video_type, progress, total_frames, particles)
    return stitch_video(OUTPUT_VID, progress)

# ═══════════════════════════════════════════
#  VIMEO UPLOAD
# ═══════════════════════════════════════════

def vimeo_upload(video_path, token, title, desc, progress=gr.Progress()):
    if not token:
        return "ERROR: No Vimeo token provided. Generate one at https://developer.vimeo.com/apps"
    progress(0, desc="Creating Vimeo upload ticket...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    ticket_data = {
        "upload": {"approach": "post", "size": str(os.path.getsize(video_path))},
        "privacy": {"view": "anybody"},
        "name": title or "Pharos NFT Collection Manager",
        "description": desc or "Generated by Pharos Video Studio on Hugging Face Spaces",
    }
    r = requests.post("https://api.vimeo.com/me/videos", headers=headers, json=ticket_data)
    if r.status_code not in (200, 201):
        return f"ERROR creating Vimeo ticket: {r.status_code} {r.text[:300]}"
    ticket = r.json()
    upload_url = ticket["upload"]["upload_link"]
    progress(0.3, desc="Uploading video to Vimeo...")
    file_size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        headers["Content-Type"] = "video/mp4"
        headers["Content-Length"] = str(file_size)
        r2 = requests.put(upload_url, headers=headers, data=f)
    if r2.status_code not in (200, 201, 204, 304):
        return f"ERROR uploading to Vimeo: {r2.status_code} {r2.text[:300]}"
    progress(0.9, desc="Verifying upload...")
    verify_url = ticket["uri"]
    for _ in range(10):
        import time
        time.sleep(2)
        r3 = requests.get(f"https://api.vimeo.com{verify_url}", headers=headers)
        if r3.status_code == 200:
            data = r3.json()
            if data.get("status") == "available":
                vimeo_link = data.get("link", f"https://vimeo.com/{data.get('uri','').split('/')[-1]}")
                progress(1.0, desc="Uploaded!")
                return f"SUCCESS: {vimeo_link}"
    progress(1.0, desc="Upload complete (pending processing)")
    vlink = ticket.get("link", f"https://vimeo.com/{verify_url.split('/')[-1]}")
    return f"UPLOADED (processing): {vlink}"

# ═══════════════════════════════════════════
#  GRADIO UI
# ═══════════════════════════════════════════

with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"), title="Pharos NFT — Video Studio") as demo:
    gr.Markdown("""
    # 🎬 Pharos NFT Collection Manager — Video Studio  
    Generate **1920×1080, 30fps** demo videos on Hugging Face's servers. Pick a type, click Generate, then optionally upload to Vimeo.
    """)

    with gr.Tabs():
        with gr.TabItem("🎥 Generate Video"):
            with gr.Row():
                with gr.Column(scale=1):
                    video_type = gr.Radio(
                        choices=["Promo Ad (24s)", "Code Deep Dive (10s)", "Web App Tour (10s)"],
                        value="Promo Ad (24s)", label="Video Type",
                        info="Promo Ad=7 animated scenes, Code=contract+files, Web App=app mockups"
                    )
                    gen_btn = gr.Button("✨ Generate Video", variant="primary", size="lg")
                    vid_output = gr.Video(label="Generated Video", show_download_button=True)
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### What each video shows:
                    - **Promo Ad** — 7 animated scenes with particles, code windows, feature cards, glow effects (~24s)
                    - **Code Deep Dive** — Contract code walkthrough, reference files, agent workflow (~10s)
                    - **Web App Tour** — Dashboard mockup, 7 pages overview, features grid (~10s)
                    """)
            gen_btn.click(fn=generate_video, inputs=video_type, outputs=vid_output)

        with gr.TabItem("☁️ Upload to Vimeo"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### Vimeo Upload
                    Upload the generated video directly to Vimeo.
                    - Get a **Personal Access Token** with `Upload` scope from [developer.vimeo.com/apps](https://developer.vimeo.com/apps)
                    - Paste it below
                    - Click Upload
                    """)
                    vimeo_token = gr.Textbox(label="Vimeo Access Token", type="password", placeholder="Paste your Vimeo Personal Access Token here...")
                    vimeo_title = gr.Textbox(label="Video Title", value="Pharos NFT Collection Manager", placeholder="Title for Vimeo")
                    vimeo_desc = gr.Textbox(label="Description", lines=3, value="AI Agent Skill for ERC-721 NFT collection management on Pharos Network. Built for the Skill-to-Agent Dual Cascade Hackathon.", placeholder="Video description")
                    vimeo_btn = gr.Button("☁️ Upload to Vimeo", variant="primary")
                    vimeo_result = gr.Textbox(label="Result", lines=2)
                    with gr.Accordion("Vimeo API Setup", open=False):
                        gr.Markdown("""
                        **To generate a token:**
                        1. Go to https://developer.vimeo.com/apps
                        2. Select your app (you already created one)
                        3. Go to **Authentication** → **Personal Access Tokens**
                        4. Click **Generate** → select **Upload** scope
                        5. Copy the token and paste it above
                        """)

            vimeo_btn.click(
                fn=vimeo_upload,
                inputs=[vid_output, vimeo_token, vimeo_title, vimeo_desc],
                outputs=vimeo_result
            )

if __name__ == "__main__":
    demo.launch()
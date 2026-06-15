import gradio as gr
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, subprocess, shutil
from math import floor

# ─── PATHS ───
FRAMES = "/tmp/pharos-ad-frames"
OUTPUT = "/tmp/pharos-ad.mp4"
os.makedirs(FRAMES, exist_ok=True)

W, H = 1920, 1080
FPS = 30
SEC_PER_SCENE = 3.5
FG = int(FPS * SEC_PER_SCENE)

# ─── COLOR PALETTE ───
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

# ─── FONTS ───
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

# ─── EASING ───
def ease_out(t): return 1 - (1-t)**3
def ease_in(t): return t**3
def ease_in_out(t): return t**2 * (3 - 2*t) if t < 0.5 else 1 - (1-t)**2 * (3 - 2*(1-t))
def lerp(a, b, t): return a + (b-a)*t
def lerp_c(c1, c2, t): return tuple(int(lerp(a,b,t)) for a,b in zip(c1, c2))

# ─── DRAWING UTILITIES ───
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
        draw.rounded_rectangle(
            [x - i*2, y - i*2, x+w + i*2, y+h + i*2],
            radius=radius + i*2,
            fill=None,
            outline=(*hex_rgb(color), a),
            width=max(1, i//2)
        )

# ─── PARTICLES ───
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
            p.x = (p.x * 7 + 13) % W  # pseudo-random reset using golden ratio
            p.vy = -(p.pulse_speed * 0.1 + 0.05)

def draw_particles(draw, particles, frame):
    for p in particles:
        a = int(p.alpha * (0.5 + 0.5 * math.sin(frame * 0.02 * p.pulse_speed + p.pulse_offset)))
        c = hex_rgb(C["secondary"])
        draw.ellipse([p.x-p.size, p.y-p.size, p.x+p.size, p.y+p.size], fill=(*c, a))

# ─── BACKGROUND LAYER ───
def draw_bg(draw, frame, tint=None):
    # Deep gradient with animated warp
    for y in range(H):
        t = y / H
        c1, c2 = hex_rgb(C["bg1"]), hex_rgb(C["bg3"])
        wave = math.sin(y * 0.003 + frame * 0.005) * 0.03
        r = int(lerp(c1[0], c2[0], t + wave))
        g = int(lerp(c1[1], c2[1], t + wave * 0.5))
        b = int(lerp(c1[2], c2[2], t + wave * 1.5))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Grid
    grid_spacing = 80
    for x in range(0, W, grid_spacing):
        ox = (frame * 0.2) % grid_spacing
        a = int(15 + 10 * math.sin((x + frame) * 0.01))
        draw.line([(x + ox, 0), (x + ox, H)], fill=(80, 60, 160, a), width=1)
    for y in range(0, H, grid_spacing):
        oy = (frame * 0.3) % grid_spacing
        a = int(15 + 10 * math.sin((y + frame * 0.7) * 0.01))
        draw.line([(0, y + oy), (W, y + oy)], fill=(80, 60, 160, a), width=1)

    # Nebula blobs
    for i in range(3):
        cx = W * 0.3 + i * W * 0.2 + math.sin(frame * 0.003 + i * 2) * 100
        cy = H * 0.3 + i * H * 0.15 + math.cos(frame * 0.004 + i * 3) * 80
        r = 300 + i * 100 + math.sin(frame * 0.005 + i) * 50
        a = int(8 + 4 * math.sin(frame * 0.01 + i))
        colors = [hex_rgb(C["primary"]), hex_rgb(C["secondary"]), hex_rgb(C["accent"])]
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*colors[i], a))

# ─── CODE WINDOW ───
def draw_code_win(draw, x, y, w, h, title, lines, t=1.0, hl=-1):
    rounded_rect(draw, x, y, w, h, 14, C["card"], C["card_border"], 1)
    # Title bar dots
    for dx, col in [(x+18, "#FF5F56"), (x+38, "#FFBD2E"), (x+58, "#27C93F")]:
        draw.ellipse([dx, y+16, dx+10, y+26], fill=col)
    draw.text((x+85, y+14), title, font=font(14), fill=C["dim"])
    # Code lines with typewriter
    lh = 26
    sy = y + 48
    visible = int(len(lines) * min(1, t * 1.2))
    for i, line in enumerate(lines[:visible]):
        ly = sy + i * lh
        if line.startswith("#"):
            draw.text((x+22, ly), line, font=font(13), fill=C["dim"])
        elif i == hl:
            draw.text((x+22, ly), line, font=font(13), fill=C["accent"])
        else:
            draw.text((x+22, ly), line, font=font(13), fill=C["text"])

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
        elif line.startswith("✓"):
            draw.text((x+14, ly), line, font=font(12), fill="#00FF88")
        else:
            draw.text((x+14, ly), line, font=font(12), fill=C["text"])

# ─── SCENES ───

def scene_intro(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)

    cx, cy = W//2, H//2
    tt = ease_out(min(1, t * 2))
    st = ease_out(max(0, (t - 0.3) * 2.5))

    # Animated rings
    for i in range(4):
        r = 250 + i * 140 + math.sin(f * 0.015 + i * 1.5) * 30
        a = int(30 + 15 * math.sin(f * 0.01 + i * 2))
        draw.ellipse([cx-r, cy-r-i*10, cx+r, cy+r+i*10], outline=(*hex_rgb(C["primary"]), a), width=1)

    # Large glow behind title
    glow(draw, cx, cy - 100, 200, C["primary"], 15)

    # Hexagon icon
    if t > 0.15:
        ht = ease_out(min(1, (t - 0.15) * 6))
        s = int(50 * ht)
        hs = int(255 * ht)
        pts = []
        for i in range(6):
            angle = math.pi/3 * i - math.pi/6 + math.sin(f * 0.005) * 0.1
            pts.append((cx + s * math.cos(angle), cy - 270 + s * math.sin(angle)))
        draw.polygon(pts, fill=None, outline=C["secondary"], width=3)
        draw.text((cx-10, cy-278), "◆", font=font(26), fill=C["accent"])

    # Title
    ts = int(80 * tt)
    draw.text((cx, cy - 170), "PHAROS NFT", font=font(ts, True), fill=(255, 255, 255, int(255*tt)), anchor="mm")
    draw.text((cx, cy - 85), "COLLECTION MANAGER", font=font(int(52 * tt), True), fill=(*hex_rgb(C["primary"]), int(255*tt)), anchor="mm")

    # Tagline
    if st > 0:
        draw.text((cx, cy + 5), "AI-Powered ERC-721 NFT Management", font=font(22), fill=(*hex_rgb(C["secondary"]), int(255*st)), anchor="mm")

    # Bottom card
    if t > 0.5:
        bt = ease_out(min(1, (t - 0.5) * 4))
        ba = int(255 * bt)
        rounded_rect(draw, cx-240, cy+80, 480, 52, 20, (*hex_rgb(C["card"]), ba), (*hex_rgb(C["card_border"]), ba), 1)
        draw.text((cx, cy+106), "Skill-to-Agent Dual Cascade Hackathon", font=font(18, True), fill=(255, 255, 255, ba), anchor="mm")

    # Corner brackets
    for corner in [(40,40), (W-40,40), (40,H-40), (W-40,H-40)]:
        l = 25
        cr, cc = hex_rgb(C["primary"]), int(80 * tt)
        draw.rectangle([corner[0]-l, corner[1]-2, corner[0]+l, corner[1]+2], fill=(*cr, cc))
        draw.rectangle([corner[0]-2, corner[1]-l, corner[0]+2, corner[1]+l], fill=(*cr, cc))


def scene_problem(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)
    cx = W//2

    tt = ease_out(min(1, max(0, t - 0.05) * 4))
    ta = int(255 * tt)
    if ta > 0:
        draw.text((cx, 90), "THE PROBLEM", font=font(16), fill=(*hex_rgb(C["secondary"]), ta), anchor="mm")
        draw.text((cx, 130), "No Existing NFT Infrastructure for AI Agents", font=font(34, True), fill=(255, 255, 255, ta), anchor="mm")

    cards = [
        ("😕", "No NFT Skill", "on Pharos Network", "Developers must build\nfrom scratch every time"),
        ("😤", "Manual Deployments", "No AI automation", "Every collection needs\nmanual contract deploys"),
        ("😰", "Zero Composability", "Siloed tooling", "No reusable modules\nfor agent ecosystems"),
    ]

    cw, ch = 480, 240
    gap = 50
    sx = (W - (3*cw + 2*gap)) // 2

    for i, (emoji, title, sub, desc) in enumerate(cards):
        ct = ease_out(min(1, max(0, t - 0.15 - i*0.12) * 3))
        if ct <= 0: continue
        ca = int(255 * ct)
        xc = sx + i * (cw + gap)
        yc = 340

        # Card shadow
        for s in range(6, 0, -1):
            sa = int(15 * (1 - s/6))
            draw.rounded_rectangle([xc-s, yc-s, xc+cw+s, yc+ch+s], radius=14, fill=(0, 0, 0, sa))

        rounded_rect(draw, xc, yc, cw, ch, 14, C["card"], (*hex_rgb(C["card_border"]), ca), 1)
        draw.text((xc+cw//2, yc+30), emoji, font=font(36), anchor="mm")
        draw.text((xc+cw//2, yc+75), title, font=font(20, True), fill=(255, 255, 255, ca), anchor="mm")
        draw.text((xc+cw//2, yc+105), sub, font=font(14), fill=(*hex_rgb(C["secondary"]), ca), anchor="mm")
        draw.line([xc+60, yc+128, xc+cw-60, yc+128], fill=(60, 60, 120, ca), width=1)
        draw.text((xc+cw//2, yc+145), desc, font=font(15), fill=(180, 180, 220, ca), anchor="mm", align="center")


def scene_solution(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)
    cx = W//2

    tt = ease_out(min(1, t * 3))
    ta = int(255 * tt)

    draw.text((cx, 60), "THE SOLUTION", font=font(16), fill=C["accent"], anchor="mm")
    draw.text((cx, 100), "Pharos NFT Collection Manager", font=font(38, True), fill=(255, 255, 255, ta), anchor="mm")

    # Terminal
    code = [
        "# Deploy an NFT collection in one AI prompt:",
        "",
        'user> "Deploy Pharos Punks, symbol PPUNK,',
        '        max supply 10000, free mint, 2.5% royalty"',
        "",
        "agent> $ forge script DeployNFT.s.sol --broadcast",
        "       ✓ Contract deployed at 0x7F...3E2B",
        "       ✓ Name: Pharos Punks",
        "       ✓ Symbol: PPUNK",
        "       ✓ Max Supply: 10,000",
    ]
    cw, ch = 850, 360
    draw_term_win(draw, (W-cw)//2, 170, cw, ch, "AI Agent Session — Terminal", code, tt)

    # Pill cards
    if t > 0.4:
        pt = ease_out(min(1, (t - 0.4) * 3))
        pa = int(255 * pt)
        pills = [
            ("⚡", "Zero Code Deploy", "Natural language → smart contract"),
            ("🔄", "Full Lifecycle", "Deploy → Mint → Transfer → Query"),
            ("💰", "EIP-2981 Royalty", "Automated creator fees built-in"),
        ]
        pw, ph = 420, 90
        pg = 40
        sx = (W - (3*pw + 2*pg)) // 2
        for i, (icon, title, desc) in enumerate(pills):
            px = sx + i * (pw + pg)
            rounded_rect(draw, px, 580, pw, ph, 12, (*hex_rgb(C["card"]), pa), (*hex_rgb(C["card_border"]), pa//2), 1)
            # Glow line left
            draw.rectangle([px+3, 590, px+5, 660], fill=(*hex_rgb(C["primary"]), pa))

            draw.text((px+24, 600), icon, font=font(26))
            draw.text((px+65, 596), title, font=font(17, True), fill=(255, 255, 255, pa))
            draw.text((px+65, 622), desc, font=font(13), fill=(180, 180, 220, pa))


def scene_features(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)
    cx = W//2

    tt = ease_out(min(1, t * 2.5))
    ta = int(255 * tt)

    draw.text((cx, 55), "WHAT YOU CAN BUILD", font=font(16), fill=C["secondary"], anchor="mm")
    draw.text((cx, 95), "Every Feature an AI Agent Needs for NFTs", font=font(32, True), fill=(255, 255, 255, ta), anchor="mm")

    features = [
        ("📦", "Deploy Collection", "ERC-721 with EIP-2981,\nmint price, supply cap"),
        ("🎨", "Mint Tokens", "Single or batch mint\nwith metadata URIs"),
        ("🔄", "Transfer & Approve", "Safe transfer with\nownership verification"),
        ("🔍", "Query State", "Owner, URI, balance,\ntotal supply, events"),
        ("📋", "Batch Operations", "Airdrop to 100+ addresses\nin one transaction"),
        ("💰", "Royalty Management", "Configurable EIP-2981\ncreator fees on sales"),
    ]

    fw, fh = 510, 150
    fgx, fgy = 55, 40
    cols = 3
    total_w = cols * fw + (cols-1) * fgx
    fsx = (W - total_w) // 2
    fsy = 170

    for i, (icon, title, desc) in enumerate(features):
        ct = ease_out(min(1, max(0, t - 0.1 - i*0.07) * 2.5))
        if ct <= 0: continue
        ca = int(255 * ct)
        col = i % cols
        row = i // cols
        fx = fsx + col * (fw + fgx)
        fy = fsy + row * (fh + fgy)

        # Entry animation (slide from below)
        entry_y = int(fy + (1 - ct) * 40)
        scaled_w = int(fw * (0.9 + 0.1 * ct))

        rounded_rect(draw, fx + (fw - scaled_w)//2, entry_y, scaled_w, fh, 14,
                     C["card"], (*hex_rgb(C["card_accent"]), ca//2), 1)

        draw.text((fx + 22, entry_y + 18), icon, font=font(30))
        draw.text((fx + 75, entry_y + 20), title, font=font(18, True), fill=(255, 255, 255, ca))
        draw.text((fx + 75, entry_y + 52), desc, font=font(14), fill=(180, 180, 220, ca))

        # Animated line
        lx = fx + 22 + (f * 2 + i * 50) % (fw - 44)
        draw.line([(fx+22, entry_y+fh-8), (lx, entry_y+fh-8)], fill=(*hex_rgb(C["primary"]), ca), width=2)

    # Bottom badge
    if t > 0.65:
        bt = ease_out(min(1, (t - 0.65) * 4))
        ba = int(255 * bt)
        rounded_rect(draw, cx-380, fsy + 2*(fh+fgy) + 25, 760, 55, 25,
                     (*hex_rgb(C["primary"]), ba//3), (*hex_rgb(C["primary"]), ba), 1)
        draw.text((cx, fsy + 2*(fh+fgy) + 53),
                  "✨ 15 capabilities · 5 reference files · Full error handling",
                  font=font(16), fill=(255, 255, 255, ba), anchor="mm")


def scene_tech(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)
    cx = W//2

    tt = ease_out(min(1, t * 2.5))
    ta = int(255 * tt)

    draw.text((cx, 45), "BUILT FOR DEVELOPERS", font=font(16), fill=C["gold"], anchor="mm")
    draw.text((cx, 85), "Enterprise-Grade Tech Stack", font=font(32, True), fill=(255, 255, 255, ta), anchor="mm")

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
        "references/deploy-nft.md  ← 35+ commands",
        "references/mint-nft.md    ← 25+ commands",
        "references/query-nft.md   ← 20+ commands",
    ]

    cw_w, cw_h = 780, 340
    dw_w, dw_h = 780, 340
    ct = ease_out(min(1, max(0, t - 0.1) * 2.5))
    dt = ease_out(min(1, max(0, t - 0.3) * 2.5))

    draw_code_win(draw, 80, 140, cw_w, cw_h, "PharosNFT.sol — Smart Contract", contract_lines, ct, 0)
    draw_term_win(draw, W-80-dw_w, 160, dw_w, dw_h, "CLI + Agent Instructions", deploy_lines, dt)

    # Tech stack bar
    if t > 0.55:
        bt = ease_out(min(1, (t - 0.55) * 4))
        ba = int(255 * bt)
        techs = ["Solidity", "EIP-2981", "ERC-721", "Foundry", "Cast/Forge", "AI Agents", "OpenZeppelin"]
        ts = "  •  ".join(techs)

        bx, by, bw, bh = cx-400, 560, 800, 44
        rounded_rect(draw, bx, by, bw, bh, 22, C["card"], (*hex_rgb(C["card_border"]), ba), 1)
        draw.text((cx, by+22), f"⚡  {ts}", font=font(14), fill=(200, 200, 255, ba), anchor="mm")


def scene_why_win(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)
    cx = W//2

    tt = ease_out(min(1, t * 2.5))
    ta = int(255 * tt)

    draw.text((cx, 45), "WHY THIS WINS", font=font(16), fill=C["gold"], anchor="mm")
    draw.text((cx, 85), "The Judges Will Notice", font=font(32, True), fill=(255, 255, 255, ta), anchor="mm")

    reasons = [
        ("🏆", "ORIGINAL", "No existing NFT Skill on Pharos"),
        ("🏆", "COMPLETE", "Full lifecycle: deploy → mint → transfer → query"),
        ("🏆", "COMPOSABLE", "Importable by any Pharos Skill Engine agent"),
        ("🏆", "PRACTICAL", "NFTs for membership, credentials, rewards"),
        ("🏆", "EXCELLENT DOCS", "Error tables, agent guidelines in every file"),
        ("🏆", "AI-NATIVE", "Designed for AI agent consumption from day one"),
    ]

    rw, rh = 560, 72
    rg = 14
    for i, (icon, title, desc) in enumerate(reasons):
        ct = ease_out(min(1, max(0, t - 0.1 - i*0.07) * 2.5))
        if ct <= 0: continue
        ca = int(255 * ct)
        rx = 130 if i % 2 == 0 else W - 130 - rw
        ry = 160 + (i//2) * (rh + rg)

        rounded_rect(draw, rx, ry, rw, rh, 10, C["card"], (*hex_rgb(C["card_border"]), ca), 1)
        draw.text((rx+16, ry+20), icon, font=font(26))
        draw.rectangle([rx+3, ry+8, rx+5, ry+rh-8], fill=(*hex_rgb(C["primary"]), ca))
        draw.text((rx+60, ry+16), title, font=font(18, True), fill=(255, 255, 255, ca))
        draw.text((rx+60, ry+42), desc, font=font(14), fill=(180, 180, 220, ca), anchor="mm")


def scene_cta(draw, f, t, total, particles):
    draw_bg(draw, f)
    draw_particles(draw, particles, f)
    cx, cy = W//2, H//2

    tt = ease_out(min(1, t * 2.5))
    ta = int(255 * tt)

    # Pulsing glow
    pr = 140 + math.sin(f * 0.04) * 20
    glow(draw, cx, cy - 80, int(pr), C["primary"], 20)

    # Main title
    draw.text((cx, cy - 170), "READY TO WIN?", font=font(56, True), fill=(255, 255, 255, ta), anchor="mm")
    draw.text((cx, cy - 105), "Deploy your NFT Collection in Minutes", font=font(22), fill=(*hex_rgb(C["secondary"]), ta), anchor="mm")

    # CTA Button
    bw, bh = 520, 70
    by = cy - 10
    # Button glow
    glow_rect(draw, cx-bw//2, by, bw, bh, 35, C["primary"], 25)
    rounded_rect(draw, cx-bw//2, by, bw, bh, 35, C["primary"], C["secondary"], 2)
    draw.text((cx, by+35), "→ github.com/DaMaker1291/pharos-nft-manager", font=font(17, True), fill=(255, 255, 255, ta), anchor="mm")

    # Hackathon info
    if t > 0.35:
        bt = ease_out(min(1, (t - 0.35) * 4))
        ba = int(255 * bt)
        rounded_rect(draw, cx-260, cy+95, 520, 85, 16, C["card"], (*hex_rgb(C["card_border"]), ba), 1)
        draw.text((cx, cy+120), "Skill-to-Agent Dual Cascade Hackathon", font=font(17, True), fill=(255, 255, 255, ba), anchor="mm")
        draw.text((cx, cy+148), "Phase 1: Skill Hackathon  |  Deadline: June 17", font=font(14), fill=(180, 180, 220, ba), anchor="mm")

    # Orbiting particles
    for i in range(8):
        angle = f * 0.015 + i * math.pi/4
        r = 320 + math.sin(f * 0.02 + i) * 30
        dx = cx + r * math.cos(angle)
        dy = cy - 40 + r * math.sin(angle)
        a = int(60 + 40 * math.sin(f * 0.03 + i))
        draw.ellipse([dx-3, dy-3, dx+3, dy+3], fill=(*hex_rgb(C["secondary"]), min(255, a)))

    # Final hold — after t=1, keep all elements visible
    if t >= 1:
        draw.text((cx, H-40), "PHAROS NFT COLLECTION MANAGER  ·  AI-Powered ERC-721  ·  github.com/DaMaker1291/pharos-nft-manager",
                  font=font(11), fill=(100, 100, 170, 180), anchor="mm")


# ─── RENDER ───

def generate_ad(progress=gr.Progress()):
    progress(0, desc="Initializing...")
    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES, exist_ok=True)

    # Initialize particles
    particles = [Particle(i * 137) for i in range(120)]

    scenes = [
        ("intro",    scene_intro,    FG),
        ("problem",  scene_problem,  FG),
        ("solution", scene_solution, FG),
        ("features", scene_features, FG),
        ("tech",     scene_tech,     FG),
        ("why-win",  scene_why_win,  FG),
        ("cta",      scene_cta,      FG),
    ]

    total_frames = sum(f for _, _, f in scenes)
    frame = 0

    for name, fn, count in scenes:
        for i in range(count):
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            t = min(1, i / count) if count > 0 else 1
            fn(draw, frame, t, count, particles)
            path = f"{FRAMES}/frame-{frame:06d}.png"
            img.save(path)
            frame += 1
            if frame % floor(FPS) == 0:
                progress(frame / total_frames, desc=f"Rendering {name} ({frame}/{total_frames})")
        update_particles(particles, frame)
        print(f"  ✓ Scene '{name}' done ({count} frames)")

    progress(0.95, desc="Stitching video with ffmpeg...")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-pattern_type", "glob",
        "-i", f"{FRAMES}/frame-*.png",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        OUTPUT
    ]
    subprocess.run(cmd, capture_output=True)

    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)

    progress(1.0, desc="Done!")
    return OUTPUT


# ─── GRADIO UI ───

with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"), title="Pharos NFT — Ad Generator") as demo:
    gr.Markdown("""
    # 🎬 Pharos NFT Collection Manager — Professional Ad Generator
    Generate a **1920×1080, 30fps** motion-graphics promotional video on Hugging Face's servers.
    Zero local computation. Click **Generate Ad** to start.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            ### Features:
            - **7 animated scenes** with particle effects
            - Cinematic parallax backgrounds
            - Animated grid lines and nebula blobs
            - Professional easing curves
            - Code windows, terminal UIs, feature cards
            - Glow effects and smooth transitions
            - **~24 seconds**, 1920×1080, 30fps
            """)
            btn = gr.Button("✨ Generate Ad", variant="primary", size="lg")
        with gr.Column(scale=2):
            video = gr.Video(label="Your Ad Video", show_download_button=True)

    btn.click(fn=generate_ad, outputs=video)
    gr.Markdown("---\n*Powered by Pillow + ffmpeg on Hugging Face Spaces — free CPU tier*")

if __name__ == "__main__":
    demo.launch()

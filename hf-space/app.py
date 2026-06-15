import gradio as gr
from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess, tempfile, shutil, json, glob, textwrap, time
from math import floor

# ---------- PATHS ----------
FRAMES = "/tmp/pharos-ad-frames"
OUTPUT = "/tmp/pharos-ad.mp4"
os.makedirs(FRAMES, exist_ok=True)

W, H = 1920, 1080
FPS = 30
SEC_PER_SCENE = 3.0
FG = int(FPS * SEC_PER_SCENE)

C_BG1 = "#1a1040"
C_BG2 = "#301860"
C_PRIMARY = "#8B7CF7"
C_SECOND = "#00D2FF"
C_ACCENT = "#00FF88"
C_GOLD = "#FFD700"
C_WHITE = "#FFFFFF"
C_TEXT = "#E8E8FF"
C_DIM = "#9999CC"
C_CARD = "#282050"
C_BORDER = "#5A4A9A"


def fnt(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def lerp(a, b, t): return a + (b - a) * t

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def gradient_bg(draw, y_offset=0):
    for y in range(H):
        t = y / H
        r1, g1, b1 = hex_to_rgb(C_BG1)
        r2, g2, b2 = hex_to_rgb(C_BG2)
        r = int(lerp(r1, r2, t))
        g = int(lerp(g1, g2, t))
        b = int(lerp(b1, b2, t))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    dot_spacing = 60
    for x in range(0, W, dot_spacing):
        for y in range(0, H, dot_spacing):
            dx = x + (y_offset * 0.3) % dot_spacing
            dy = y + (y_offset * 0.5) % dot_spacing
            alpha = int(40 + 30 * math.sin((x + y + y_offset) * 0.01))
            draw.ellipse([dx-1, dy-1, dx+1, dy+1], fill=(150, 120, 255, alpha))


def draw_rounded_box(draw, x, y, w, h, color, radius=12, border=None, bw=2):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=color)
    if border:
        draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, outline=border, width=bw)


def draw_glow(draw, cx, cy, radius, color, alpha=80):
    for r in range(radius, 0, -4):
        a = int(alpha * (1 - r / radius))
        c = hex_to_rgb(color)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*c, a))


def draw_code_window(draw, x, y, w, h, title, lines, t=1.0, highlight=-1):
    draw_rounded_box(draw, x, y, w, h, C_CARD, 14, C_BORDER, 1)
    dot_r = 8
    for i, (dx, col) in enumerate([(x+20, "#FF5F56"), (x+44, "#FFBD2E"), (x+68, "#27C93F")]):
        a = int(255 * min(1, t * 3))
        draw.ellipse([dx, y+18, dx+dot_r, y+18+dot_r], fill=col)
    draw.text((x+100, y+14), title, font=fnt(16), fill=C_DIM)
    line_h = 26
    start_y = y + 50
    visible = int(len(lines) * t)
    for i, line in enumerate(lines[:visible]):
        ly = start_y + i * line_h
        fg = C_ACCENT if i == highlight else C_TEXT
        kw = {"fill": C_DIM} if line.startswith("#") else {"fill": fg}
        draw.text((x+24, ly), line, font=fnt(15), **kw)


def draw_terminal(draw, x, y, w, h, title, lines, t=1.0, typing=False):
    draw_rounded_box(draw, x, y, w, h, "#0A0A15", 10, "#1A1A3A", 1)
    draw.rounded_rectangle([x, y, x+w, y+36], radius=10, fill="#12122A")
    draw.text((x+16, y+10), title, font=fnt(14), fill=C_DIM)
    line_h = 24
    visible = int(len(lines) * t) if not typing else len(lines)
    for i, line in enumerate(lines[:visible]):
        ly = y + 48 + i * line_h
        if typing and i == visible - 1:
            chars = int((t % 1) * len(line))
            line = line[:chars] + "█"
        draw.text((x+16, ly), line, font=fnt(14), fill=C_ACCENT if i == 0 else C_TEXT)


def make_scene(scene_name, frame_num, total_frames, draw_fn):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    t = min(1, frame_num / total_frames) if total_frames > 0 else 1
    draw_fn(draw, frame_num, t, total_frames)
    return img


# ---------- SCENES ----------

def scene_intro(draw, f, t, total):
    gradient_bg(draw, f)
    cx, cy = W//2, H//2
    for i in range(3):
        r = 200 + i * 120 + math.sin(f * 0.02 + i) * 40
        a = int(60 + math.sin(f * 0.01 + i * 2) * 30)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(108, 92, 231, a), width=2)
    draw_glow(draw, cx, cy - 80, 150, C_PRIMARY, 40)
    title_alpha = min(255, int(255 * max(0, t * 3 - 0.5)))
    subtitle_alpha = min(255, int(255 * max(0, t * 3 - 1.5)))
    if t > 0.3:
        s = min(60, int(60 * (t - 0.3) * 5))
        pts = []
        for i in range(6):
            angle = math.pi/3 * i - math.pi/6 + f * 0.005
            pts.append((cx + s * math.cos(angle), cy - 280 + s * math.sin(angle)))
        draw.polygon(pts, fill=None, outline=C_SECOND, width=3)
        draw.text((cx-12, cy-290), "◆", font=fnt(30), fill=C_ACCENT)
    draw.text((cx, cy - 160), "PHAROS NFT", font=fnt(64), fill=(255, 255, 255, title_alpha), anchor="mm")
    draw.text((cx, cy - 90), "COLLECTION MANAGER", font=fnt(52, True), fill=(108, 92, 231, title_alpha), anchor="mm")
    draw.text((cx, cy), "AI-Powered ERC-721 NFT Management", font=fnt(24), fill=(0, 210, 255, subtitle_alpha), anchor="mm")
    if t > 0.6:
        ba = min(255, int(255 * (t - 0.6) * 5))
        draw_rounded_box(draw, cx-220, cy+80, 440, 50, C_CARD, 16, C_BORDER)
        draw.text((cx, cy+105), "Skill-to-Agent Dual Cascade Hackathon", font=fnt(18), fill=(255, 255, 255, ba), anchor="mm")
    for corner in [(30, 30), (W-30, 30), (30, H-30), (W-30, H-30)]:
        draw.rectangle([corner[0]-20, corner[1]-2, corner[0]+20, corner[1]+2], fill=(108, 92, 231, max(30, title_alpha//3)))
        draw.rectangle([corner[0]-2, corner[1]-20, corner[0]+2, corner[1]+20], fill=(108, 92, 231, max(30, title_alpha//3)))


def scene_problem(draw, f, t, total):
    gradient_bg(draw, f)
    cx = W // 2
    if t > 0.1:
        a = min(255, int(255 * (t - 0.1) * 5))
        draw.text((cx, 100), "THE PROBLEM", font=fnt(18), fill=(0, 210, 255, a), anchor="mm")
        draw.text((cx, 145), "No Existing NFT Infrastructure for AI Agents", font=fnt(38, True), fill=(255, 255, 255, a), anchor="mm")
    cards = [
        ("😕", "No NFT Skill", "on Pharos Network", "Developers must build\nfrom scratch every time"),
        ("😤", "Manual Deployments", "No AI automation", "Every collection needs\nmanual contract deploys"),
        ("😰", "Zero Composability", "Siloed tooling", "No reusable modules\nfor agent ecosystems"),
    ]
    card_w, card_h = 500, 260
    gap = 60
    start_x = (W - (3 * card_w + 2 * gap)) // 2
    card_t = max(0, (t - 0.2) * 2)
    for i, (emoji, title, sub, desc) in enumerate(cards):
        ct = min(1, max(0, card_t - i * 0.15) * 3)
        if ct <= 0: continue
        cx_c = start_x + i * (card_w + gap)
        cy_c = 380
        a = int(255 * ct)
        draw_rounded_box(draw, cx_c, cy_c, card_w, card_h, C_CARD, 20, (42, 42, 90, a), 1)
        draw.text((cx_c + card_w//2, cy_c + 35), emoji, font=fnt(40), anchor="mm")
        draw.text((cx_c + card_w//2, cy_c + 80), title, font=fnt(22, True), fill=(255, 255, 255, a), anchor="mm")
        draw.text((cx_c + card_w//2, cy_c + 110), sub, font=fnt(16), fill=(0, 210, 255, a), anchor="mm")
        draw.line([cx_c + 80, cy_c + 135, cx_c + card_w - 80, cy_c + 135], fill=(66, 66, 120, a), width=1)
        draw.text((cx_c + card_w//2, cy_c + 155), desc, font=fnt(16), fill=(180, 180, 220, a), anchor="mm", align="center")


def scene_solution(draw, f, t, total):
    gradient_bg(draw, f)
    cx = W // 2
    a = min(255, int(255 * t * 4))
    draw.text((cx, 70), "THE SOLUTION", font=fnt(18), fill=C_ACCENT, anchor="mm")
    draw.text((cx, 115), "Pharos NFT Collection Manager", font=fnt(40, True), fill=(255, 255, 255, a), anchor="mm")
    code_lines = [
        "# Deploy an NFT collection in one AI prompt:",
        "",
        'user> "Deploy \'Pharos Punks\' with symbol PPUNK,',
        '        max supply 10000, free mint, 2.5% royalty"',
        "",
        "agent> $ forge script DeployNFT.s.sol --broadcast",
        "       ✓ Contract deployed at 0x7F...3E2B",
        "       ✓ Name: Pharos Punks",
        "       ✓ Symbol: PPUNK",
        "       ✓ Max Supply: 10,000",
        "       ✓ Royalty: 2.5% → 0xDeployer...",
    ]
    cw_w, cw_h = 800, 380
    cw_x, cw_y = (W - cw_w) // 2, 190
    draw_code_window(draw, cw_x, cw_y, cw_w, cw_h, "terminal — AI Agent Session", code_lines, t, 0)
    if t > 0.5:
        ba = min(255, int(255 * (t - 0.5) * 5))
        pills = [
            ("⚡", "Zero Code Deploy", "Natural language → smart contract"),
            ("🔄", "Full Lifecycle", "Deploy → Mint → Transfer → Query"),
            ("💰", "EIP-2981 Royalty", "Automated creator fees built-in"),
        ]
        pill_w, pill_h = 400, 100
        pgap = 50
        sx = (W - (3 * pill_w + 2 * pgap)) // 2
        for i, (icon, title, desc) in enumerate(pills):
            px = sx + i * (pill_w + pgap)
            draw_rounded_box(draw, px, 620, pill_w, pill_h, C_CARD, 14, C_BORDER)
            draw.text((px + 30, 645), icon, font=fnt(28))
            draw.text((px + 75, 638), title, font=fnt(18, True), fill=(255, 255, 255, ba))
            draw.text((px + 75, 662), desc, font=fnt(14), fill=(180, 180, 220, ba))


def scene_features(draw, f, t, total):
    gradient_bg(draw, f)
    cx = W // 2
    a = min(255, int(255 * t * 3))
    draw.text((cx, 60), "WHAT YOU CAN BUILD", font=fnt(18), fill=C_SECOND, anchor="mm")
    draw.text((cx, 105), "Every Feature an AI Agent Needs for NFTs", font=fnt(34, True), fill=(255, 255, 255, a), anchor="mm")
    features = [
        ("📦", "Deploy Collection", "ERC-721 with EIP-2981,\nmint price, supply cap"),
        ("🎨", "Mint Tokens", "Single or batch mint\nwith metadata URIs"),
        ("🔄", "Transfer & Approve", "Safe transfer with\nownership verification"),
        ("🔍", "Query State", "Owner, URI, balance,\ntotal supply, events"),
        ("📋", "Batch Operations", "Airdrop to 100+ addresses\nin one transaction"),
        ("💰", "Royalty Management", "Configurable EIP-2981\ncreator fees on sales"),
    ]
    cols, rows = 3, 2
    fw, fh = 500, 160
    fgap_x, fgap_y = 60, 50
    total_w = cols * fw + (cols - 1) * fgap_x
    total_h = rows * fh + (rows - 1) * fgap_y
    fsx = (W - total_w) // 2
    fsy = 180
    ft = max(0, (t - 0.1) * 1.5)
    for i, (icon, title, desc) in enumerate(features):
        col = i % cols
        row = i // cols
        ci = min(1, max(0, ft - i * 0.08) * 3)
        if ci <= 0: continue
        fa = int(255 * ci)
        fx = fsx + col * (fw + fgap_x)
        fy = fsy + row * (fh + fgap_y)
        draw_rounded_box(draw, fx, fy, fw, fh, C_CARD, 14, (42, 42, 90, fa), 1)
        draw.text((fx + 24, fy + 20), icon, font=fnt(32))
        draw.text((fx + 80, fy + 22), title, font=fnt(20, True), fill=(255, 255, 255, fa))
        draw.text((fx + 80, fy + 55), desc, font=fnt(15), fill=(180, 180, 220, fa))
        lx = fx + 24 + (f * 3) % (fw - 48)
        draw.line([(fx+24, fy+fh-6), (lx, fy+fh-6)], fill=(0, 210, 255, fa), width=2)
    if t > 0.7:
        ba = min(255, int(255 * (t - 0.7) * 5))
        draw_rounded_box(draw, cx-350, fsy+total_h+30, 700, 60, (108, 92, 231, ba//2), 30, C_PRIMARY, 2)
        draw.text((cx, fsy+total_h+60), "✨ 15 capabilities · 5 reference files · Full error handling", font=fnt(18), fill=(255, 255, 255, ba), anchor="mm")


def scene_tech(draw, f, t, total):
    gradient_bg(draw, f)
    cx = W // 2
    a = min(255, int(255 * t * 3))
    draw.text((cx, 50), "BUILT FOR DEVELOPERS", font=fnt(18), fill=C_GOLD, anchor="mm")
    draw.text((cx, 95), "Enterprise-Grade Tech Stack", font=fnt(36, True), fill=(255, 255, 255, a), anchor="mm")
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
    ct = min(1, max(0, t - 0.1) * 2)
    dt = min(1, max(0, t - 0.3) * 2)
    cw_w, cw_h = 780, 380
    cw_x = 100
    cw_y = 160
    draw_code_window(draw, cw_x, cw_y, cw_w, cw_h, "PharosNFT.sol — Smart Contract", contract_lines, ct, 0)
    dw_w, dw_h = 780, 380
    dw_x = W - 100 - dw_w
    dw_y = 160
    draw_terminal(draw, dw_x, dw_y, dw_w, dw_h, "CLI + Agent Instructions", deploy_lines, dt)
    if t > 0.6:
        ba = min(255, int(255 * (t - 0.6) * 5))
        techs = ["Solidity", "EIP-2981", "ERC-721", "Foundry", "Cast/Forge", "AI Agents", "OpenZeppelin"]
        tech_str = "  •  ".join(techs)
        draw_rounded_box(draw, cx-380, 600, 760, 50, C_CARD, 25, C_BORDER)
        draw.text((cx, 625), f"⚡  {tech_str}", font=fnt(16), fill=(200, 200, 255, ba), anchor="mm")


def scene_why_win(draw, f, t, total):
    gradient_bg(draw, f)
    cx = W // 2
    a = min(255, int(255 * t * 3))
    draw.text((cx, 50), "WHY THIS WINS", font=fnt(18), fill=C_GOLD, anchor="mm")
    draw.text((cx, 95), "The Judges Will Notice", font=fnt(36, True), fill=(255, 255, 255, a), anchor="mm")
    reasons = [
        ("🏆", "ORIGINAL", "No existing NFT Skill on Pharos"),
        ("🏆", "COMPLETE", "Full lifecycle: deploy → mint → transfer → query"),
        ("🏆", "COMPOSABLE", "Importable by any Pharos Skill Engine agent"),
        ("🏆", "PRACTICAL", "NFTs for membership, credentials, rewards"),
        ("🏆", "EXCELLENT DOCS", "Error tables, agent guidelines in every file"),
        ("🏆", "AI-NATIVE", "Designed for AI agent consumption from day one"),
    ]
    rw, rh = 580, 80
    rgap = 16
    start_y = 180
    rt = max(0, (t - 0.1) * 1.5)
    for i, (icon, title, desc) in enumerate(reasons):
        ci = min(1, max(0, rt - i * 0.08) * 3)
        if ci <= 0: continue
        ra = int(255 * ci)
        rx = 120 if i % 2 == 0 else W - 120 - rw
        ry = start_y + (i // 2) * (rh + rgap)
        draw_rounded_box(draw, rx, ry, rw, rh, C_CARD, 12, (42, 42, 90, ra), 1)
        draw.text((rx + 18, ry + 22), icon, font=fnt(30))
        draw.rectangle([rx+3, ry+10, rx+5, ry+rh-10], fill=(108, 92, 231, ra))
        draw.text((rx + 68, ry + 18), title, font=fnt(20, True), fill=(255, 255, 255, ra))
        draw.text((rx + 68, ry + 46), desc, font=fnt(15), fill=(180, 180, 220, ra))


def scene_cta(draw, f, t, total):
    gradient_bg(draw, f)
    cx, cy = W//2, H//2
    a = min(255, int(255 * t * 3))
    pulse_r = 120 + math.sin(f * 0.05) * 20
    draw_glow(draw, cx, cy - 100, int(pulse_r), C_PRIMARY, 15)
    draw.text((cx, cy - 180), "READY TO WIN?", font=fnt(60, True), fill=(255, 255, 255, a), anchor="mm")
    draw.text((cx, cy - 110), "Deploy your NFT Collection in Minutes", font=fnt(24), fill=C_SECOND, anchor="mm")
    btn_w, btn_h = 500, 70
    btn_y = cy - 10
    draw_rounded_box(draw, cx - btn_w//2, btn_y, btn_w, btn_h, C_PRIMARY, 35, C_SECOND, 2)
    draw.text((cx, btn_y + 35), "→ github.com/DaMaker1291/pharos-nft-manager", font=fnt(18, True), fill=(255, 255, 255, a), anchor="mm")
    if t > 0.4:
        ba = min(255, int(255 * (t - 0.4) * 5))
        draw_rounded_box(draw, cx-250, cy+90, 500, 80, C_CARD, 16, C_BORDER)
        draw.text((cx, cy+115), "Skill-to-Agent Dual Cascade Hackathon", font=fnt(18, True), fill=(255, 255, 255, ba), anchor="mm")
        draw.text((cx, cy+145), "Phase 1: Skill Hackathon  |  Deadline: June 17", font=fnt(16), fill=(180, 180, 220, ba), anchor="mm")
    for i in range(6):
        angle = f * 0.02 + i * math.pi/3
        r = 350 + math.sin(f * 0.03 + i) * 30
        dx = cx + r * math.cos(angle)
        dy = cy - 50 + r * math.sin(angle)
        draw.ellipse([dx-2, dy-2, dx+2, dy+2], fill=(0, 210, 255, max(30, int(a*0.3))))


# ---------- GENERATE ----------

def generate_ad(progress=gr.Progress()):
    progress(0, desc="Cleaning up...")
    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES, exist_ok=True)

    scenes = [
        ("intro", scene_intro, FG),
        ("problem", scene_problem, FG),
        ("solution", scene_solution, FG),
        ("features", scene_features, FG),
        ("tech", scene_tech, FG),
        ("why-win", scene_why_win, FG),
        ("cta", scene_cta, FG),
    ]

    total_frames = sum(f for _, _, f in scenes)
    frame = 0
    bg = Image.new("RGBA", (W, H), (26, 16, 64, 255))
    rendered = 0

    for name, fn, count in scenes:
        for i in range(count):
            img_rgba = make_scene(name, i, count, fn)
            img = Image.alpha_composite(bg, img_rgba).convert("RGB")
            path = f"{FRAMES}/frame-{frame:06d}.png"
            img.save(path)
            frame += 1
            rendered += 1
            if rendered % floor(FPS) == 0:
                progress(rendered / total_frames, desc=f"Rendering {name} ({rendered}/{total_frames})")
        print(f"  ✓ Scene '{name}' done ({count} frames)")

    progress(0.95, desc="Stitching video with ffmpeg...")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-pattern_type", "glob",
        "-i", f"{FRAMES}/frame-*.png",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        OUTPUT
    ]
    subprocess.run(cmd, capture_output=True)

    if os.path.exists(FRAMES):
        shutil.rmtree(FRAMES)

    progress(1.0, desc="Done!")
    return OUTPUT

# ---------- GRADIO UI ----------

with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple", secondary_hue="cyan"), title="Pharos NFT — Ad Generator") as demo:
    gr.Markdown("""
    # 🎬 Pharos NFT Collection Manager — Ad Generator
    Click **Generate Ad** to create a full 1920×1080 promotional video on Hugging Face's servers.
    Zero local computation — everything runs here.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            ### What you get:
            - **7 animated scenes** (intro, problem, solution, features, tech, why-win, CTA)
            - **1920×1080**, 30fps, ~21 seconds
            - Dark purple/cyan cyberpunk aesthetic
            - Code windows, terminal mockups, animated cards
            - Direct download link
            """)
            generate_btn = gr.Button("✨ Generate Ad", variant="primary", size="lg")
        with gr.Column(scale=2):
            video = gr.Video(label="Your Ad Video", show_download_button=True)

    generate_btn.click(
        fn=generate_ad,
        outputs=video,
    )

    gr.Markdown("---\n*Powered by Pillow + ffmpeg on Hugging Face Spaces*")

if __name__ == "__main__":
    demo.launch()

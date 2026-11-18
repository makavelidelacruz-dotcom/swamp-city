# Sign art atlas: one painted/neon/engraved face per sign label, packed into 2048px atlases.
# Writes tex/signs-N.jpg (color), tex/signs-N-em.jpg (glow) and signs.json (atlas + uv rect per sign, in DFS order).
import json, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

snap = json.load(open('/home/claude/bake/snap.json'))
signs = []
def walk(n):
    a = n['a']
    if a.get('data-bake') and n['tag'] == 'm-label' and a.get('data-mount'): signs.append(a)
    for c in n['c']: walk(c)
walk(snap)

PX = 92
PAINTED = {'LIVE BAIT', 'GUMBO HUT', 'BAIT & TACKLE', 'GATOR FARM', 'SWAMP PAWN', 'GATOR JUNK', 'BAYOU CANNERY CO.'}          # pixels per meter
AT = 2048
F_NEON = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
F_SERIF = '/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrebonum-bold.otf'
F_PAINT = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
lime = Image.open('/home/claude/bake/tex/limestone.jpg').convert('RGB')
plank = Image.open('/home/claude/bake/tex/planks.jpg').convert('RGB')

def hexrgb(h, d=(255, 255, 255)):
    h = (h or '').lstrip('#')
    if len(h) == 3: h = ''.join(c * 2 for c in h)
    try: return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception: return d

def fit_font(path, text, W, H, frac=0.62, maxw=0.88):
    size = max(8, int(H * frac))
    while size > 8:
        f = ImageFont.truetype(path, size)
        if path == F_PAINT:
            try: f.set_variation_by_name('Bold')
            except Exception: pass
        b = f.getbbox(text)
        if b[2] - b[0] <= W * maxw: return f
        size -= 2
    return ImageFont.truetype(path, 8)

def tiled(src, W, H):
    out = Image.new('RGB', (W, H))
    for y in range(0, H, src.height):
        for x in range(0, W, src.width): out.paste(src, (x, y))
    return out

FT = '/home/claude/fonts/ttf/'
FONTS = {k: FT + k + '.ttf' for k in ['anton', 'bungee', 'bebas-neue', 'pacifico', 'monoton', 'black-ops-one', 'alfa-slab-one', 'racing-sans-one', 'lobster', 'permanent-marker', 'oswald']}
# GTA-style brand looks for Swamp City: (style, font, background, letters, tagline)
STYLE = {
    'BAYOU SAVINGS & TRUST': ('bank', None, '#13233f', '#f2c94c', 'EST. 1899  -  MEMBER FDIC'),
    'CHAOS TRIALS  |  SWAMP CITY': ('marquee', 'bungee', '#120d10', '#ff4fa3', None),
    'LUCKY GATOR CASINO': ('marquee', 'bungee', '#160a1a', '#ff4fa3', 'SLOTS  -  LUCKY WHEEL  -  GATOR DICE  -  OPEN 24/7'),
    'GATOR GRAND HOTEL': ('billboard', 'bebas-neue', '#2a1238', '#f2c94c', 'SUITES  -  ROOFTOP POOL  -  CASINO NEXT DOOR'),
    'PELICAN MOTEL': ('script', 'lobster', '#0e1c24', '#3ff2e0', 'VACANCY'),
    'GATOR PIT': ('billboard', 'bungee', '#0b0f0b', '#7dff8a', 'FRIDAY NIGHT FIGHTS  -  LIVE'),
    'GATOR FARM': ('painted', 'alfa-slab-one', None, '#f2e6c8', 'TOURS  -  FRESH EGGS'),
    'LIVE BAIT': ('painted', 'permanent-marker', None, '#ffe14d', 'WORMS  -  CRICKETS  -  ICE'),
    'BAYOU HEIGHTS': ('billboard', 'bebas-neue', '#132a4a', '#ffffff', 'LUXURY CONDOS  -  NOW LEASING'),
    'BAYOU PD': ('police', 'oswald', '#1a3d8f', '#ffffff', 'TO PROTECT AND SERVE THE SWAMP'),
    'MARSH TOWER': ('billboard', 'oswald', '#1c2228', '#d8dee6', 'OFFICES  -  FLOORS 1-12'),
    'THE RUSTY CRAWDAD': ('script', 'pacifico', '#1a0c08', '#ff8a3d', 'COLD BEER  -  LIVE BLUES'),
    'GUMBO HUT': ('billboard', 'alfa-slab-one', '#f2e6c8', '#c0241e', 'HOT GUMBO  -  OPEN 24 HRS'),
    'VOODOO INK': ('script', 'permanent-marker', '#120a18', '#c48bff', 'TATTOOS  -  PIERCING  -  WALK-INS'),
    'BAIT & TACKLE': ('billboard', 'bungee', '#ffd21f', '#141414', 'LURES  -  LINE  -  LICENSES'),
    'SWAMP PAWN': ('billboard', 'anton', '#111111', '#ffd21f', 'WE BUY GOLD  -  CASH NOW'),
    'SWAMP RECORDS': ('script', 'lobster', '#140a1e', '#c48bff', 'VINYL  -  TAPES  -  CDS'),
    'BAYOU BOWL': ('script', 'lobster', '#081a20', '#2ff3e0', 'COSMIC BOWLING  -  OPEN LATE'),
    'ST. GATOR CHAPEL': ('script', 'lobster', '#fff6f0', '#e0457a', 'WEDDINGS 24 HRS  -  ELVIS ON CALL'),
    'CRAWFISH KING': ('billboard', 'bungee', '#ffcf1f', '#c8161d', 'ALL YOU CAN EAT'),
    'SWAMP FAIR': ('billboard', 'bungee', '#2a1238', '#ff6ec7', 'RIDES  -  GAMES  -  FUNNEL CAKES'),
    'BAYOU CANNERY CO.': ('painted', 'alfa-slab-one', None, '#f2e6c8', 'EST. 1921'),
    'GATOR JUNK': ('stencil', 'black-ops-one', '#2b2a26', '#ffb020', 'SCRAP  -  PARTS  -  NO QUESTIONS'),
    'KGTR 97.3': ('billboard', 'racing-sans-one', '#c8161d', '#ffffff', 'SWAMP ROCK RADIO'),
    'SWAMP CITY MARINA': ('billboard', 'bungee', '#0e3a52', '#ffffff', 'BOAT SLIPS  -  BAIT  -  FUEL'),
    'BAYOU EYE': ('script', 'lobster', '#123a3a', '#7dfff0', None),
    'GATOR-GO-ROUND': ('script', 'lobster', '#4a0f22', '#ffd27a', None),
    'GATOR DROP': ('billboard', 'bungee', '#2a1238', '#ff6ec7', None),
    'ICE HOUSE': ('script', 'racing-sans-one', '#08141c', '#9ae6ff', None), 'VOODOO': ('script', 'permanent-marker', '#120a18', '#c48bff', None),
    "PO' BOYS": ('script', 'pacifico', '#140c08', '#ffb347', None), 'OYSTER BAR': ('script', 'lobster', '#081418', '#7dfff0', None),
    'ZYDECO': ('script', 'pacifico', '#140812', '#ff6ec7', None), 'BEIGNETS': ('script', 'lobster', '#160c08', '#ffe08a', None),
    'FISH MARKET': ('billboard', 'bungee', '#0e3a52', '#ffffff', None), 'BOAT WORKS': ('stencil', 'black-ops-one', '#2b2a26', '#ffffff', None),
    'ROPE & NET': ('painted', 'alfa-slab-one', None, '#f2e6c8', None), 'PRALINES': ('script', 'pacifico', '#1a0c10', '#ff9ad5', None),
    'JAZZ': ('script', 'monoton', '#0a0a18', '#5fb6ff', None), 'HOODOO': ('script', 'permanent-marker', '#120a18', '#9be15d', None),
    'CAJUN GRILL': ('billboard', 'alfa-slab-one', '#c0241e', '#ffe08a', None), 'DRY DOCK': ('stencil', 'black-ops-one', '#2b2a26', '#ffd21f', None),
    'SHRIMP CO.': ('billboard', 'bungee', '#ff7a5c', '#ffffff', None),
    'WELCOME TO SWAMP CITY': ('billboard', 'bungee', '#0e3a52', '#ffffff', 'DOWNTOWN  -  BANK  -  CASINO  -  SWAMP FAIR'),
    'VISITOR CENTER': ('billboard', 'oswald', '#0e3a52', '#ffffff', None),
    'SWAMP CITY VISITOR CENTER': ('billboard', 'bungee', '#0e3a52', '#ffffff', 'TEAM CHECK-IN  -  PICK YOUR CREW HERE'),
    'TEAM CHECK-IN': ('highway', 'oswald', '#12613a', '#ffffff', 'VISITOR CENTER  -  EAST EDGE'),
}
DISTRICT = {'UPTOWN', 'BAYOU VILLAGE', 'VOODOO QUARTER', 'OLD TOWN', 'CANNERY ROW', 'GATOR FLATS'}

def font_at(path, size): return ImageFont.truetype(path, max(8, int(size)))
def fit(path, text, maxw, maxh):
    size = int(maxh)
    while size > 8:
        f = font_at(path, size); b = f.getbbox(text)
        if b[2] - b[0] <= maxw and b[3] - b[1] <= maxh * 1.05: return f
        size -= 2
    return font_at(path, 8)
def glow(img, draw_fn, blur, k=0.9):
    """draw shapes on a black layer, blur it, add it to img; returns (img, layer)"""
    lay = Image.new('RGB', img.size, (0, 0, 0)); draw_fn(ImageDraw.Draw(lay))
    halo = lay.filter(ImageFilter.GaussianBlur(blur))
    out = np.clip(np.asarray(img).astype(np.float32) + np.asarray(halo).astype(np.float32) * k, 0, 255)
    return Image.fromarray(out.astype(np.uint8)), lay, halo
def lines_layout(W, H, has_tag):
    return (H * 0.40, H * 0.62, H * 0.80) if has_tag else (H / 2, H * 0.74, None)
def tag_font(H): return FONTS['oswald']

def render(a):
    text = a.get('content', '').strip()
    mount = a['data-mount']
    W = max(64, int(float(a.get('width', 1)) * PX)); H = max(32, int(float(a.get('height', 1)) * PX))
    fc = hexrgb(a.get('font-color'), (255, 255, 255)); bg = hexrgb(a.get('color'), (18, 13, 16))
    st = STYLE.get(text)
    if text in DISTRICT: st = ('highway', 'oswald', '#12613a', '#ffffff', None)
    if text.endswith(' HIDEOUT'): st = ('stencil', 'black-ops-one', '#24221f', None, 'MEMBERS ONLY  -  NO COPS')
    if st is None:
        st = {'engraved': ('engraved', None, None, None, None), 'hang': ('painted', 'alfa-slab-one', None, None, None), 'marquee': ('marquee', 'bungee', None, None, None)}.get(mount, ('billboard', 'bungee', None, None, None))
    style, fname, sbg, sfc, tag = st
    if sbg: bg = hexrgb(sbg)
    if sfc: fc = hexrgb(sfc)
    fpath = FONTS.get(fname, F_NEON)
    em = Image.new('RGB', (W, H), (0, 0, 0))
    small = H < 70
    if small: tag = None
    if style == 'bank':   # modern bank branding on the old frieze: navy band, gold serif letters, fine gold rules
        y = np.linspace(0, 1, H)[:, None, None]
        arr = np.array(bg, np.float32)[None, None, :] * (1.15 - 0.35 * y) * np.ones((H, W, 1))
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        gold = fc; bw = max(2, H // 30)
        d.rectangle([bw, bw, W - 1 - bw, H - 1 - bw], outline=gold, width=bw)
        d.rectangle([bw * 4, bw * 4, W - 1 - bw * 4, H - 1 - bw * 4], outline=tuple(int(v * 0.6) for v in gold), width=max(1, bw // 2))
        f = fit_font(F_SERIF, text, W, H * (0.8 if tag else 1), 0.66)
        cy = H * 0.43 if tag else H / 2
        d.text((W / 2 + 2, cy + 3), text, font=f, fill=(8, 12, 22), anchor='mm')
        d.text((W / 2, cy), text, font=f, fill=gold, anchor='mm')
        if tag: d.text((W / 2, H * 0.82), tag, font=fit(FONTS['oswald'], tag, W * 0.4, H * 0.15), fill=tuple(int(v * 0.85) for v in gold), anchor='mm')
        ImageDraw.Draw(em).text((W / 2, cy), text, font=f, fill=tuple(int(v * 0.5) for v in gold), anchor='mm')
        return img, em
    if style == 'engraved':
        img = tiled(lime.resize((PX * 3, PX * 3)), W, H)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W - 1, H - 1], outline=(150, 140, 120), width=max(3, H // 16))
        f = fit_font(F_SERIF, text, W, H * (0.78 if tag else 1), 0.62)
        cy = H * 0.42 if tag else H / 2
        c = (W / 2, cy)
        d.text((c[0] + 3, c[1] + 4), text, font=f, fill=(70, 60, 45), anchor='mm')
        d.text((c[0] - 1, c[1] - 1), text, font=f, fill=(255, 238, 190), anchor='mm')
        d.text(c, text, font=f, fill=(205, 160, 70), anchor='mm')
        if tag: d.text((W / 2, H * 0.83), tag, font=fit(F_SERIF, tag, W * 0.6, H * 0.17), fill=(120, 96, 50), anchor='mm')
        ImageDraw.Draw(em).text(c, text, font=f, fill=(60, 45, 15), anchor='mm')
        return img, em
    if style == 'painted':
        img = tiled(plank.resize((PX * 2, PX * 2)), W, H)
        img = Image.blend(img, Image.new('RGB', (W, H), (30, 22, 16)), 0.35)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W - 1, H - 1], outline=(25, 18, 12), width=max(3, H // 10))
        y1, y2, _ = (H * 0.42, H * 0.8, None) if tag else (H / 2, None, None)
        f = fit(fpath, text, W * 0.86, H * (0.5 if tag else 0.64))
        d.text((W / 2 + 3, y1 + 3), text, font=f, fill=(15, 10, 8), anchor='mm')
        d.text((W / 2, y1), text, font=f, fill=fc, anchor='mm', stroke_width=max(1, H // 40), stroke_fill=(20, 14, 10))
        if tag: d.text((W / 2, y2), tag, font=fit(FONTS['oswald'], tag, W * 0.8, H * 0.2), fill=(240, 228, 200), anchor='mm')
        ImageDraw.Draw(em).text((W / 2, y1), text, font=f, fill=tuple(int(v * 0.35) for v in fc), anchor='mm')
        return img, em
    if style == 'highway':   # green freeway guide sign: white border, white letters, exit tab and arrow
        img = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(img)
        r = H // 8; bw = max(4, H // 22)
        d.rounded_rectangle([bw * 2, bw * 2, W - 1 - bw * 2, H - 1 - bw * 2], radius=r, outline=(255, 255, 255), width=bw)
        f = fit(fpath, text, W * 0.7, H * 0.44)
        d.text((W * 0.44, H * 0.4), text, font=f, fill=(255, 255, 255), anchor='mm')
        sub = tag or 'NEXT EXIT'
        sf = fit(FONTS['oswald'], sub, W * (0.62 if tag else 0.16), H * 0.16)
        d.text((W * 0.44, H * 0.8), sub, font=sf, fill=(255, 255, 255), anchor='mm')
        ax, ay, s = W * 0.86, H * 0.5, H * 0.24
        if tag:   # arrow pointing right
            d.polygon([(ax + s, ay), (ax + s * 0.1, ay - s * 0.8), (ax + s * 0.1, ay - s * 0.3), (ax - s, ay - s * 0.3), (ax - s, ay + s * 0.3), (ax + s * 0.1, ay + s * 0.3), (ax + s * 0.1, ay + s * 0.8)], fill=(255, 255, 255))
        else:     # arrow pointing up (straight ahead)
            d.polygon([(ax, ay - s), (ax - s * 0.8, ay - s * 0.1), (ax - s * 0.3, ay - s * 0.1), (ax - s * 0.3, ay + s), (ax + s * 0.3, ay + s), (ax + s * 0.3, ay - s * 0.1), (ax + s * 0.8, ay - s * 0.1)], fill=(255, 255, 255))
        em = Image.fromarray((np.asarray(img).astype(np.float32) * 0.35).astype(np.uint8))   # reflective at night
        return img, em
    if style == 'police':
        img = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(img)
        d.rectangle([0, int(H * 0.72), W, H], fill=(255, 255, 255))
        d.rectangle([0, 0, W - 1, H - 1], outline=(240, 200, 60), width=max(3, H // 20))
        cx, cy, s = H * 0.55, H * 0.36, H * 0.26        # gold star badge
        pts = [(cx + math.cos(math.radians(-90 + k * 36)) * (s if k % 2 == 0 else s * 0.45), cy + math.sin(math.radians(-90 + k * 36)) * (s if k % 2 == 0 else s * 0.45)) for k in range(10)]
        d.polygon(pts, fill=(240, 200, 60))
        f = fit(fpath, text, W * 0.7, H * 0.5)
        d.text((W * 0.56, H * 0.36), text, font=f, fill=(255, 255, 255), anchor='mm')
        if tag: d.text((W / 2, H * 0.86), tag, font=fit(FONTS['oswald'], tag, W * 0.86, H * 0.18), fill=bg, anchor='mm')
        em = Image.fromarray((np.asarray(img).astype(np.float32) * 0.45).astype(np.uint8))
        return img, em
    if style == 'stencil':
        base = np.asarray(Image.open('/home/claude/bake/tex/metal.jpg').convert('L').resize((W, H))).astype(np.float32) / 255
        arr = (np.array(bg, np.float32)[None, None, :] * (0.7 + 0.5 * base[..., None]))
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        sw = max(6, H // 9)   # hazard stripes top and bottom
        for x in range(-H, W + H, sw * 2):
            for y0 in (0, H - sw):
                d.polygon([(x, y0 + sw), (x + sw, y0), (x + 2 * sw, y0), (x + sw, y0 + sw)], fill=(230, 180, 30))
        y1 = H * 0.45 if tag else H / 2
        f = fit(fpath, text, W * 0.88, H * (0.42 if tag else 0.55))
        d.text((W / 2, y1), text, font=f, fill=fc, anchor='mm')
        if tag: d.text((W / 2, H * 0.74), tag, font=fit(FONTS['oswald'], tag, W * 0.7, H * 0.13), fill=(235, 230, 220), anchor='mm')
        ImageDraw.Draw(em).text((W / 2, y1), text, font=f, fill=tuple(int(v * 0.4) for v in fc), anchor='mm')
        return img, em
    if style == 'billboard':
        img = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(img)
        dark = sum(bg) < 300
        acc = tuple(min(255, int(v * 0.85)) for v in fc)
        d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 34) if not dark else acc, width=max(4, H // 18))
        if tag:
            band = int(H * 0.27)
            d.rectangle([max(4, H // 18), H - band - max(4, H // 18), W - 1 - max(4, H // 18), H - 1 - max(4, H // 18)], fill=fc if not dark else (20, 20, 24))
        y1 = H * (0.38 if tag else 0.5)
        f = fit(fpath, text, W * 0.88, H * (0.48 if tag else 0.62))
        sh = max(2, H // 30)
        d.text((W / 2 + sh, y1 + sh), text, font=f, fill=(0, 0, 0) if not dark else (0, 0, 0), anchor='mm')
        d.text((W / 2, y1), text, font=f, fill=fc, anchor='mm', stroke_width=max(1, H // 60), stroke_fill=(0, 0, 0) if not dark else tuple(int(v * 0.4) for v in fc))
        if tag:
            tf = fit(FONTS['oswald'], tag, W * 0.84, H * 0.17)
            d.text((W / 2, H - band / 2 - max(4, H // 18)), tag, font=tf, fill=bg if not dark else fc, anchor='mm')
        k = 0.55 if dark else 0.4   # backlit box
        em = Image.fromarray((np.asarray(img).astype(np.float32) * k).astype(np.uint8))
        return img, em
    if style == 'script':   # neon tubes on a dark backer (or on white for the chapel)
        light_bg = sum(bg) > 500
        base = np.asarray(Image.open('/home/claude/bake/tex/metal.jpg').convert('L').resize((W, H))).astype(np.float32) / 255
        arr = np.array(bg, np.float32)[None, None, :] * (0.85 + 0.2 * base[..., None])
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
        d.rounded_rectangle([2, 2, W - 3, H - 3], radius=H // 6, outline=tuple(int(v * 0.6) for v in fc), width=max(3, H // 22))
        y1 = H * (0.42 if tag else 0.5)
        f = fit(fpath, text, W * 0.84, H * (0.56 if tag else 0.7))
        tagc = (255, 60, 60) if tag == 'VACANCY' else (tuple(int(v * 0.75) for v in fc) if light_bg else (255, 238, 200))
        def tubes(gd):
            gd.text((W / 2, y1), text, font=f, fill=fc, anchor='mm')
            if tag: gd.text((W / 2, H * 0.83), tag, font=fit(FONTS['oswald'], tag, W * 0.8, H * 0.17), fill=tagc, anchor='mm')
        img, lay, halo = glow(img, tubes, max(3, H // 12), 0.0 if light_bg else 0.95)
        core = Image.new('RGB', (W, H), (0, 0, 0)); cd = ImageDraw.Draw(core)
        cd.text((W / 2, y1), text, font=f, fill=tuple(min(255, int(v * 0.55 + 120)) for v in fc) if not light_bg else fc, anchor='mm')
        if tag: cd.text((W / 2, H * 0.83), tag, font=fit(FONTS['oswald'], tag, W * 0.8, H * 0.17), fill=tagc if light_bg else tuple(min(255, int(v * 0.6 + 100)) for v in tagc), anchor='mm')
        out = np.asarray(img).astype(np.float32); c = np.asarray(core).astype(np.float32)
        out = np.where(c.sum(-1, keepdims=True) > 0, c if light_bg else np.maximum(out, c), out)
        img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        em = Image.fromarray(np.clip(np.asarray(halo).astype(np.float32) * 0.7 + np.asarray(lay).astype(np.float32) * (0.4 if light_bg else 1.0), 0, 255).astype(np.uint8))
        return img, em
    # marquee (and anything else): dark brushed backing, inset frame, bulbs, glowing letters
    base = np.asarray(Image.open('/home/claude/bake/tex/metal.jpg').convert('L').resize((W, H))).astype(np.float32) / 255
    bgc = np.array(bg, dtype=np.float32) / 255 * 0.9 + 0.03
    arr = (bgc[None, None, :] * (0.75 + 0.35 * base[..., None])) * 255
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    bw = max(3, H // 14)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 38, 42), width=bw)
    d.rectangle([bw * 2, bw * 2, W - 1 - bw * 2, H - 1 - bw * 2], outline=tuple(int(v * 0.55) for v in fc), width=max(2, bw // 2))
    glow_layer = Image.new('RGB', (W, H), (0, 0, 0)); gd = ImageDraw.Draw(glow_layer)
    r = max(4, H // 16); step = r * 4
    for x in range(step // 2, W, step):
        for y in (bw * 3, H - 1 - bw * 3): gd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 214, 120))
    for y in range(step // 2 + bw * 3, H - bw * 3, step):
        for x in (bw * 3, W - 1 - bw * 3): gd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 214, 120))
    y1 = H * (0.42 if tag else 0.5)
    f = fit(fpath, text, W * 0.82, H * (0.46 if tag else 0.56))
    gd.text((W / 2, y1), text, font=f, fill=fc, anchor='mm')
    if tag: gd.text((W / 2, H * 0.76), tag, font=fit(FONTS['oswald'], tag, W * 0.7, H * 0.15), fill=(255, 230, 150), anchor='mm')
    halo = glow_layer.filter(ImageFilter.GaussianBlur(max(3, H // 14)))
    tube = Image.new('RGB', (W, H), (0, 0, 0))
    ImageDraw.Draw(tube).text((W / 2, y1), text, font=f, fill=tuple(min(255, int(v * 0.6 + 110)) for v in fc), anchor='mm')
    out = np.asarray(img).astype(np.float32) + np.asarray(halo).astype(np.float32) * 0.9 + np.asarray(glow_layer).astype(np.float32) * 0.8
    core = np.asarray(tube).astype(np.float32)
    out = np.where(core.sum(-1, keepdims=True) > 0, np.maximum(out, core + np.asarray(glow_layer).astype(np.float32) * 0.4), out)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    emv = np.asarray(halo).astype(np.float32) * 0.7 + np.asarray(glow_layer).astype(np.float32)
    em = Image.fromarray(np.clip(emv, 0, 255).astype(np.uint8))
    return img, em
# shelf-pack into atlases
items = []
for i, a in enumerate(signs):
    img, em = render(a)
    if img.width > AT - 8:   # very long signs: scale down to fit the atlas width
        s = (AT - 8) / img.width
        img = img.resize((AT - 8, max(8, int(img.height * s)))); em = em.resize(img.size)
    items.append((i, img, em))
order = sorted(items, key=lambda t: -t[1].height)
atlases = []; placed = {}
cur = None
for i, img, em in order:
    w, h = img.size
    while True:
        if cur is None:
            cur = {'c': Image.new('RGB', (AT, AT), (20, 20, 20)), 'e': Image.new('RGB', (AT, AT), (0, 0, 0)), 'x': 4, 'y': 4, 'row': 0}
            atlases.append(cur)
        if cur['x'] + w + 4 > AT: cur['x'] = 4; cur['y'] += cur['row'] + 4; cur['row'] = 0
        if cur['y'] + h + 4 > AT: cur = None; continue
        break
    cur['c'].paste(img, (cur['x'], cur['y'])); cur['e'].paste(em, (cur['x'], cur['y']))
    k = len(atlases) - 1
    placed[i] = {'atlas': k, 'u0': cur['x'] / AT, 'v0': cur['y'] / AT, 'u1': (cur['x'] + w) / AT, 'v1': (cur['y'] + h) / AT}
    cur['x'] += w + 4; cur['row'] = max(cur['row'], h)
for k, a in enumerate(atlases):
    # crop unused bottom so the atlas stays small
    used = max(p['v1'] for p in placed.values() if p['atlas'] == k)
    hh = 1 << int(np.ceil(np.log2(max(64, used * AT + 4))))
    a['c'].crop((0, 0, AT, hh)).save(f'/home/claude/bake/tex/signs-{k}.jpg', quality=88)
    a['e'].crop((0, 0, AT, hh)).save(f'/home/claude/bake/tex/signs-{k}-em.jpg', quality=85)
    for p in placed.values():
        if p['atlas'] == k: p['v0'] *= AT / hh; p['v1'] *= AT / hh
json.dump([placed[i] | {'content': signs[i].get('content'), 'mount': signs[i]['data-mount']} for i in range(len(signs))], open('/home/claude/bake/signs.json', 'w'), indent=0)
print(len(signs), 'signs in', len(atlases), 'atlases')

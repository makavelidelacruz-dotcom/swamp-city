# Swamp Fair artwork: awning stripes, food stand boards, Whack-a-Gator backboard, high striker scale, carousel fascia
import sys; sys.argv = ['x']
exec(open('/home/claude/boats/ctex.py').read().split('SYMBOL_COL')[0])   # icon drawer + fonts
import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
GOLD = (232, 182, 62); CREAM = (250, 240, 214); INK = (24, 12, 26)

def stripes(name, col, n=8):
    im = Image.new('RGB', (512, 512), CREAM); d = ImageDraw.Draw(im)
    w = 512 // n
    for k in range(0, n, 2): d.rectangle([k * w, 0, (k + 1) * w - 1, 511], fill=col)
    arr = np.asarray(im).astype(float); arr *= (0.94 + 0.06 * np.random.default_rng(3).random((512, 512, 1)))   # canvas grain
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT + name + '.jpg', quality=90)
stripes('stripe-red', (196, 40, 52)); stripes('stripe-teal', (22, 140, 138)); stripes('stripe-purple', (118, 52, 160)); stripes('stripe-gold', (222, 160, 30))

def bulbs(d, W, H, step=48, inset=22, r=8):
    for x in range(inset + step // 2, W - inset, step):
        for y in (inset, H - inset): d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 238, 170))
    for y in range(inset + step, H - inset - step // 2, step):
        for x in (inset, W - inset): d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 238, 170))

def glowtext(img, xy, txt, size, col, stroke=(30, 10, 30)):
    g = Image.new('RGB', img.size, (0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.text(xy, txt, font=font(FB, size), fill=col, anchor='mm')
    g = g.filter(ImageFilter.GaussianBlur(size // 9))
    out = Image.fromarray(np.clip(np.asarray(img).astype(int) + (np.asarray(g) * 0.8).astype(int), 0, 255).astype(np.uint8))
    ImageDraw.Draw(out).text(xy, txt, font=font(FB, size), fill=tuple(min(255, int(v * 0.4 + 150)) for v in col), anchor='mm', stroke_width=max(3, size // 22), stroke_fill=stroke)
    return out

# food stand header boards (1024 x 256)
for key, title, sub, col, bg in [('funnel', 'FUNNEL CAKES', 'POWDERED SUGAR  |  SWAMP BERRY', (255, 120, 190), (60, 14, 40)),
                                  ('boudin', 'BOUDIN BALLS', 'CAJUN SPICE  |  CRISPY HOT', (255, 170, 60), (60, 26, 10)),
                                  ('snowball', 'SNOWBALLS', 'BLUE BAYOU  |  SATSUMA  |  ICE', (90, 220, 255), (10, 30, 60)),
                                  ('gatorstick', 'GATOR ON A STICK', 'FRIED  |  GRILLED  |  BRAVE', (120, 240, 120), (12, 40, 20))]:
    im = Image.new('RGB', (1024, 256), bg); d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, 1017, 249], radius=28, outline=GOLD, width=10); bulbs(d, 1024, 256, 52, 24, 7)
    im = glowtext(im, (512, 112), title, 96, col)
    ImageDraw.Draw(im).text((512, 200), sub, font=font(FB, 34), fill=(255, 232, 150), anchor='mm')
    im.save(OUT + 'stand-' + key + '.jpg', quality=90)

# Whack-a-Gator backboard (1024 x 512)
im = Image.new('RGB', (1024, 512), (20, 60, 34)); d = ImageDraw.Draw(im)
for k in range(24):     # sunburst
    a0, a1 = math.radians(k * 15), math.radians(k * 15 + 7)
    d.polygon([(512, 330), (512 + math.cos(a0) * 900, 330 + math.sin(a0) * 900), (512 + math.cos(a1) * 900, 330 + math.sin(a1) * 900)], fill=(30, 84, 46))
d.rounded_rectangle([8, 8, 1015, 503], radius=36, outline=GOLD, width=14); bulbs(d, 1024, 512, 56, 28, 9)
for x in (128, 896): sym(d, 'GATOR', x, 340, 130)
im = glowtext(im, (512, 140), 'WHACK-A-GATOR', 92, (130, 255, 140))
d = ImageDraw.Draw(im); d.text((512, 300), 'CLICK START', font=font(FB, 54), fill=(255, 230, 120), anchor='mm')
d.text((512, 368), 'BOP EVERY GATOR THAT POPS UP', font=font(FB, 32), fill=CREAM, anchor='mm')
d.text((512, 428), '20 SECONDS  |  BEAT THE HIGH SCORE', font=font(FB, 30), fill=(255, 210, 120), anchor='mm')
im.save(OUT + 'whack-board.jpg', quality=90)

# High striker scale (256 x 2048), bottom = 0, top = bell
im = Image.new('RGB', (256, 2048), (250, 236, 200)); d = ImageDraw.Draw(im)
bands = [('GATOR!', (200, 30, 40)), ('BULLFROG', (230, 120, 30)), ('CATFISH', (220, 190, 40)), ('TADPOLE', (60, 150, 80)), ('SKEETER', (40, 110, 180))]
h = 2048 // len(bands)
for i, (lab, c) in enumerate(bands):
    y0 = i * h; d.rectangle([0, y0, 255, y0 + h], fill=c)
    for t in range(1, 5): d.line([(0, y0 + t * h // 5), (60, y0 + t * h // 5)], fill=CREAM, width=6)
    tl = Image.new('RGBA', (h, 256), (0, 0, 0, 0)); td = ImageDraw.Draw(tl)
    td.text((h // 2, 140), lab, font=font(FB, 96), fill=CREAM, anchor='mm', stroke_width=5, stroke_fill=INK)
    im.paste(tl.rotate(90, expand=True), (0, y0), tl.rotate(90, expand=True))
d.rectangle([0, 0, 255, 2047], outline=GOLD, width=14)
im.save(OUT + 'striker-scale.jpg', quality=90)

# carousel rounding-board fascia (1024 x 256), tiles around the canopy
im = Image.new('RGB', (1024, 256), (120, 20, 50)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, 1023, 24], fill=GOLD); d.rectangle([0, 232, 1023, 255], fill=GOLD)
for k in range(4):
    cx = 128 + k * 256
    d.ellipse([cx - 80, 50, cx + 80, 206], fill=(250, 236, 200), outline=GOLD, width=10)
    sym(d, ['GATOR', 'FROG', 'CROWN', 'FROG'][k], cx, 128, 120)
    for s in (-1, 1): d.arc([cx + s * 128 - 40, 60, cx + s * 128 + 40, 196], 0, 360, fill=GOLD, width=6)
for x in range(16, 1024, 32): d.ellipse([x - 6, 6, x + 6, 18], fill=(255, 240, 180)); d.ellipse([x - 6, 238, x + 6, 250], fill=(255, 240, 180))
im.save(OUT + 'carousel-fascia.jpg', quality=90)

# gator scales for the carousel figures and the drop tower head (512, seamless-ish)
rng = np.random.default_rng(5); im = Image.new('RGB', (512, 512), (52, 120, 60)); d = ImageDraw.Draw(im)
for y in range(0, 512, 32):
    for x in range(-16 if (y // 32) % 2 else 0, 512, 32):
        c = 40 + int(rng.random() * 30); d.rounded_rectangle([x + 2, y + 2, x + 30, y + 30], radius=8, fill=(c, 110 + c, 50 + c // 2), outline=(28, 70, 34), width=2)
im.save(OUT + 'gatorpaint.jpg', quality=90)
print('ok')

# Bet board faces: one per wheel symbol, same icon art and colours as the wheel
import sys; sys.argv = ['x']
exec(open('/home/claude/boats/ctex.py').read().split('# ---------------- wheel face')[0])   # icons, colours, fonts only
import numpy as np, math
from PIL import Image, ImageDraw, ImageFilter
W, H = 1024, 704
for s in ['CROWN', 'GATOR', 'FROG', 'SKULL']:
    c0, c1 = np.array(SEG_BG[s][0]), np.array(SEG_BG[s][1])
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.clip(np.hypot((xx - W / 2) / (W / 2), (yy - H * 0.42) / (H / 2)), 0, 1)[..., None]
    img = Image.fromarray((c1 * (1 - r) + c0 * r).astype(np.uint8)); d = ImageDraw.Draw(img)
    # sunburst rays behind the icon
    ray = Image.new('L', (W, H), 0); rd = ImageDraw.Draw(ray)
    for k in range(18):
        a0 = math.radians(k * 20); a1 = math.radians(k * 20 + 9)
        rd.polygon([(W / 2, 250), (W / 2 + math.cos(a0) * 900, 250 + math.sin(a0) * 900), (W / 2 + math.cos(a1) * 900, 250 + math.sin(a1) * 900)], fill=38)
    img = Image.composite(Image.new('RGB', (W, H), (255, 230, 150)), img, ray); d = ImageDraw.Draw(img)
    # gold double frame with marquee bulbs
    d.rounded_rectangle([10, 10, W - 10, H - 10], radius=40, outline=(232, 182, 62), width=16)
    d.rounded_rectangle([46, 46, W - 46, H - 46], radius=28, outline=(150, 100, 30), width=5)
    for x in range(70, W - 60, 56):
        for y in (28, H - 28): d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 238, 170))
    for y in range(84, H - 60, 56):
        for x in (28, W - 28): d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 238, 170))
    # icon with a soft glow disc
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse([W / 2 - 170, 80, W / 2 + 170, 420], fill=120)
    img = Image.composite(Image.new('RGB', (W, H), (255, 245, 210)), img, glow.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(img)
    sym(d, s, W / 2, 250, 300)
    # BET <SYMBOL> banner and payout
    d.rounded_rectangle([110, 440, W - 110, 560], radius=24, fill=(24, 10, 28), outline=(232, 182, 62), width=6)
    d.text((W / 2, 500), 'BET ' + s, font=font(FB, 92), fill=SYMBOL_COL[s], anchor='mm', stroke_width=3, stroke_fill=(10, 4, 12))
    d.text((W / 2, 612), 'PAYS ' + PAY[s] + '   CLICK TO BET', font=font(FB, 54), fill=(255, 232, 140), anchor='mm', stroke_width=3, stroke_fill=(30, 10, 20))
    img.save(OUT + 'bet-' + s.lower() + '.jpg', quality=90)
print('ok')

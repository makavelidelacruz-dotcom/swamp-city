# Bank artwork: rusticated stone, granite, marble floor, fluted column, burlap money sack, ATM screen, teller plaques
import sys; sys.argv = ['x']
exec(open('/home/claude/boats/ctex.py').read().split('SYMBOL_COL')[0])   # fonts, OUT
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
rng = np.random.default_rng(11)
def noise(n, scale, seed):
    r = np.random.default_rng(seed); small = r.random((n // scale + 2, n // scale + 2))
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)).astype(float) / 255

# rusticated ashlar: 1 tile = 2.4 m wide x 1.2 m tall (two courses of 1.2 x 0.6 blocks, offset)
W = 1024; H = 512
base = np.array([226, 212, 182], float)
n1 = noise(W, 8, 1)[:H, :W]; n2 = noise(W, 64, 2)[:H, :W]
img = base[None, None, :] * (0.86 + 0.1 * n1[..., None] + 0.08 * n2[..., None])
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
for row in range(2):
    y0 = row * 256; off = 0 if row == 0 else 256
    d.line([(0, y0), (W, y0)], fill=(120, 108, 88), width=10); d.line([(0, y0 + 6), (W, y0 + 6)], fill=(250, 240, 214), width=3)
    for x in range(-off, W, 512):
        xx = x + off
        d.line([(xx % W, y0), (xx % W, y0 + 256)], fill=(120, 108, 88), width=10)
        d.line([((xx + 6) % W, y0), ((xx + 6) % W, y0 + 256)], fill=(250, 240, 214), width=3)
im = im.filter(ImageFilter.GaussianBlur(0.8)); im.save(OUT + 'bankstone.jpg', quality=90)

# dark granite for the plinth and steps
g = np.array([88, 84, 86], float); n3 = rng.random((512, 512))
arr = g[None, None, :] * (0.8 + 0.4 * (n3[..., None] > 0.82)) * (0.9 + 0.1 * noise(512, 16, 4)[..., None])
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(OUT + 'granite.jpg', quality=90)

# checkerboard marble floor: 1 tile = 2 m (4 squares of 1 m)
m = np.zeros((512, 512, 3)); v = noise(512, 32, 5); v2 = noise(512, 8, 6)
vein = np.abs(np.sin((v * 9 + v2 * 2) * 3.14)) ** 12
for i in range(2):
    for j in range(2):
        c = np.array([236, 232, 222]) if (i + j) % 2 == 0 else np.array([34, 36, 40])
        m[i * 256:(i + 1) * 256, j * 256:(j + 1) * 256] = c
m = m * (0.93 + 0.07 * v2[..., None]) + vein[..., None] * np.where(m.sum(-1, keepdims=True) > 300, -70, 90)
mi = Image.fromarray(np.clip(m, 0, 255).astype(np.uint8)); dm = ImageDraw.Draw(mi)
for k in (0, 256): dm.line([(k, 0), (k, 511)], fill=(200, 170, 90), width=3); dm.line([(0, k), (511, k)], fill=(200, 170, 90), width=3)
mi.save(OUT + 'marblefloor.jpg', quality=90)

# fluted column: 1 tile wraps once round the shaft, 16 flutes
c = np.zeros((256, 512, 3)); x = np.arange(512) / 512 * 16 * 2 * np.pi
shade = 0.78 + 0.22 * np.abs(np.cos(x / 2)) ** 0.6
c[:] = np.array([238, 230, 210])[None, None, :] * shade[None, :, None]
c *= (0.94 + 0.06 * noise(512, 16, 7)[:256, :, None])
Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).save(OUT + 'flutes.jpg', quality=90)

# burlap money sack with a big green $ stamp (front and back halves of the u range)
b = np.array([176, 140, 92], float); wv = noise(512, 2, 8)
xx, yy = np.meshgrid(np.arange(512), np.arange(512))
weave = 0.85 + 0.15 * ((np.sin(xx * 1.6) * np.sin(yy * 1.6)) > 0)
arr = b[None, None, :] * weave[..., None] * (0.9 + 0.12 * wv[..., None]) * (0.9 + 0.1 * noise(512, 32, 9)[..., None])
sack = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
stamp = Image.new('L', (512, 512), 0); sd = ImageDraw.Draw(stamp)
for cx in (128, 384):
    sd.ellipse([cx - 92, 170, cx + 92, 354], outline=255, width=12)
    sd.text((cx, 262), '$', font=font(FB, 150), fill=255, anchor='mm')
stamp = stamp.filter(ImageFilter.GaussianBlur(1.2))
ink = Image.new('RGB', (512, 512), (30, 92, 48))
Image.composite(ink, sack, stamp.point(lambda p: int(p * 0.85))).save(OUT + 'moneybag.jpg', quality=90)

# ATM screen + teller plaque
a = Image.new('RGB', (512, 384), (10, 40, 70)); ad = ImageDraw.Draw(a)
ad.rectangle([0, 0, 511, 70], fill=(220, 170, 40)); ad.text((256, 36), 'SWAMP CITY ATM', font=font(FB, 40), fill=(20, 20, 30), anchor='mm')
ad.text((256, 150), 'INSERT CARD', font=font(FB, 46), fill=(140, 230, 255), anchor='mm')
ad.text((256, 230), 'FAST CASH  $20  $60  $100', font=font(FB, 28), fill=(230, 240, 255), anchor='mm')
ad.text((256, 320), 'NO FEES FOR GATORS', font=font(FB, 26), fill=(255, 220, 120), anchor='mm')
a.save(OUT + 'atm.jpg', quality=90)
t = Image.new('RGB', (512, 128), (24, 32, 44)); td = ImageDraw.Draw(t)
td.rectangle([4, 4, 507, 123], outline=(214, 170, 70), width=6)
td.text((256, 64), 'TELLER  1  2  3  4', font=font(FB, 54), fill=(240, 205, 120), anchor='mm')
t.save(OUT + 'teller.jpg', quality=90)
print('ok')

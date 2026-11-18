# Gator Pit artwork (CC0, procedural): arena sand, wet mud with puddles, palisade logs, mossy stone,
# bleacher planks, crew banners (team color with a gator-tooth hem), gold trim, bone.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = '/home/claude/boats/tex/'
def noise(n, scale, seed, m=None):
    m = m or n
    r = np.random.default_rng(seed); small = r.random((m // scale + 2, n // scale + 2))
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((n, m), Image.BICUBIC)).astype(float)[:m, :n] / 255
def fbm(n, seed): return 0.5 * noise(n, 64, seed) + 0.3 * noise(n, 16, seed + 1) + 0.2 * noise(n, 4, seed + 2)
def save(arr, name, blur=0.6): Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur)).save(OUT + name, quality=88)
N = 512
# raked arena sand
f = fbm(N, 1); rake = (0.94 + 0.06 * np.sin(np.arange(N) / 3.0))[:, None, None]
save(np.array([196, 168, 118], float) * (0.82 + 0.25 * f[..., None]) * rake, 'pit-sand.jpg')
# wet swamp mud with glossy puddles
f = fbm(N, 5); pud = np.clip((noise(N, 48, 9) - 0.62) * 6, 0, 1)[..., None]
mud = np.array([74, 58, 38], float) * (0.75 + 0.4 * f[..., None])
save(mud * (1 - pud) + np.array([46, 52, 40], float) * pud, 'pit-mud.jpg')
# palisade logs (vertical, 8 logs per tile) with bark streaks
x = np.arange(N); log = (0.6 + 0.4 * np.abs(np.sin(x / N * np.pi * 8)))[None, :, None]
bark = noise(N, 3, 13)[..., None] * 0.35 + noise(N, 32, 14)[..., None] * 0.2
save(np.array([98, 70, 44], float) * log * (0.75 + bark), 'pit-logs.jpg')
# mossy stone blocks
f = fbm(N, 21); moss = np.clip((noise(N, 24, 22) - 0.55) * 4, 0, 1)[..., None]
st = np.array([118, 112, 100], float) * (0.75 + 0.35 * f[..., None])
im = Image.fromarray(np.clip(st * (1 - moss) + np.array([70, 96, 52], float) * moss, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
for r in range(4):
    y = r * 128; d.line([(0, y), (N, y)], fill=(60, 56, 50), width=6); off = 0 if r % 2 else 128
    for c in range(-1, 3): d.line([(c * 256 + off, y), (c * 256 + off, y + 128)], fill=(60, 56, 50), width=6)
im.filter(ImageFilter.GaussianBlur(0.8)).save(OUT + 'pit-stone.jpg', quality=88)
# bleacher planks (horizontal boards, weathered paint)
y = np.arange(N); gap = ((y % 64) < 4)[:, None, None]
wood = np.array([150, 112, 72], float) * (0.75 + 0.3 * noise(N, 2, 31)[..., None] * noise(N, 40, 32)[..., None] + 0.1)
save(np.where(gap, np.array([50, 38, 28], float), wood), 'pit-planks.jpg')
# crew banners: team color cloth with a darker stripe and a gator-tooth hem at the bottom
for name, col in [('gator', (79, 224, 143)), ('heron', (63, 208, 255)), ('frog', (255, 194, 61)), ('snake', (196, 139, 255))]:
    W, H = 256, 512
    c = np.array(col, float) * 0.8
    arr = np.ones((H, W, 3)) * c * (0.85 + 0.2 * noise(W, 8, 41, H)[..., None])
    im = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(im)
    d.rectangle([0, 60, W, 90], fill=tuple(int(v * 0.55) for v in col)); d.rectangle([0, 0, W, 14], fill=(30, 26, 22))
    for k in range(8): d.polygon([(k * 32, H - 60), (k * 32 + 32, H - 60), (k * 32 + 16, H - 4)], fill=(240, 236, 220))   # teeth
    d.ellipse([W / 2 - 70, 170, W / 2 + 70, 310], outline=(240, 236, 220), width=10)   # a ring emblem
    d.polygon([(W / 2 - 40, 270), (W / 2, 190), (W / 2 + 40, 270)], fill=(240, 236, 220))
    im.save(OUT + f'pit-banner-{name}.jpg', quality=90)
# hammered gold trim
f = fbm(256, 51); save(np.array([214, 168, 64], float) * (0.8 + 0.35 * f[..., None]), 'pit-gold.jpg')
print('pit textures done')

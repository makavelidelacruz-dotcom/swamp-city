# Gator Junk artwork (CC0, procedural): rusty car paint in six colors, bare rust, yard dirt with oil stains,
# chipped crusher yellow, rusty corrugated trailer siding, crushed-car bale, cracked dark glass, tire tread rubber.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = '/home/claude/boats/tex/'
def noise(n, scale, seed):
    r = np.random.default_rng(seed); small = r.random((n // scale + 2, n // scale + 2))
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)).astype(float)[:n, :n] / 255
def fbm(n, seed): return 0.5 * noise(n, 64, seed) + 0.3 * noise(n, 16, seed + 1) + 0.2 * noise(n, 4, seed + 2)
N = 512
RUST = np.array([122, 62, 30], float); RUST_D = np.array([70, 36, 20], float)
def rusty(paint, seed, amount=0.42):
    f = 0.4 * noise(N, 64, seed) + 0.35 * noise(N, 12, seed + 1) + 0.25 * noise(N, 3, seed + 2); m = np.clip((f - (1 - amount)) * 6, 0, 1)[..., None]          # rust patches
    streak = np.clip(noise(N, 2, seed + 9)[..., None] * 0.25, 0, 1)
    p = np.array(paint, float) * (0.82 + 0.25 * noise(N, 8, seed + 3)[..., None])   # faded, uneven paint
    r = RUST * (0.7 + 0.5 * noise(N, 4, seed + 5)[..., None]) * (1 - streak) + RUST_D * streak
    img = p * (1 - m) + r * m
    # dents and scratches
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); rg = np.random.default_rng(seed)
    for _ in range(40):
        x, y = rg.integers(0, N, 2); L = rg.integers(10, 60); a = rg.random() * 6.28
        d.line([(x, y), (x + L * np.cos(a), y + L * np.sin(a))], fill=(170, 150, 130), width=1)
    return im.filter(ImageFilter.GaussianBlur(0.6))
for name, col in [('red', (150, 36, 30)), ('blue', (40, 70, 130)), ('green', (52, 98, 60)), ('cream', (210, 196, 160)), ('teal', (40, 120, 120)), ('black', (40, 40, 42))]:
    rusty(col, sum(map(ord, name)), 0.38).save(OUT + f'junk-{name}.jpg', quality=88)
rusty((112, 70, 46), 77, 0.9).save(OUT + 'junk-rust.jpg', quality=88)

# yard dirt with gravel and oil stains (1 tile = 8 m)
f = fbm(1024, 31)
dirt = np.array([112, 96, 74], float) * (0.75 + 0.4 * f[..., None])
grav = (np.random.default_rng(3).random((1024, 1024)) > 0.93)[..., None]
dirt = dirt * (1 - grav * 0.35) + grav * np.array([150, 140, 125]) * 0.35
im = Image.fromarray(np.clip(dirt, 0, 255).astype(np.uint8)).convert('RGBA')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rg = np.random.default_rng(8)
for _ in range(7):
    x, y = rg.integers(120, 904, 2); r = rg.integers(20, 55)
    d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(18, 16, 14, 150))
ov = ov.filter(ImageFilter.GaussianBlur(10)); im = Image.alpha_composite(im, ov).convert('RGB')
im.filter(ImageFilter.GaussianBlur(0.8)).save(OUT + 'junk-dirt.jpg', quality=86)

# crusher: chipped safety yellow with black-and-yellow hazard band at the bottom
f = fbm(N, 41); m = np.clip((f - 0.62) * 7, 0, 1)[..., None]
y = np.array([214, 168, 30], float) * (0.85 + 0.2 * noise(N, 8, 42)[..., None])
img = y * (1 - m) + (RUST * 0.8) * m
im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
for k in range(-2, 12): d.polygon([(k * 64, N), (k * 64 + 32, N), (k * 64 + 96, N - 64), (k * 64 + 64, N - 64)], fill=(24, 22, 20))
im.filter(ImageFilter.GaussianBlur(0.5)).save(OUT + 'junk-crusher.jpg', quality=88)

# rusty corrugated siding for the office trailer
x = np.arange(N); rib = (0.75 + 0.25 * np.cos(x / N * 2 * np.pi * 16))[None, :, None]
f = fbm(N, 51); m = np.clip((f - 0.45) * 4, 0, 1)[..., None]
img = (np.array([168, 172, 168], float) * (1 - m) + RUST * m) * rib
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(OUT + 'junk-siding.jpg', quality=88)

# crushed-car bale: squashed layers of mixed paint, rust and chrome
rg = np.random.default_rng(61); im = Image.new('RGB', (N, N)); d = ImageDraw.Draw(im); y0 = 0
cols = [(150, 36, 30), (40, 70, 130), (52, 98, 60), (210, 196, 160), (122, 62, 30), (90, 90, 92), (180, 180, 184), (40, 120, 120)]
while y0 < N:
    h = int(rg.integers(10, 34)); pts = [(0, y0)]
    for xx in range(0, N + 32, 32): pts.append((xx, y0 + int(rg.integers(-6, 6))))
    pts += [(N, y0 + h), (0, y0 + h)]
    d.polygon(pts, fill=tuple(int(c * (0.7 + 0.4 * rg.random())) for c in cols[int(rg.integers(0, len(cols)))])); y0 += h
arr = np.asarray(im).astype(float) * (0.8 + 0.3 * noise(N, 4, 62)[..., None])
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)).save(OUT + 'junk-bale.jpg', quality=88)

# cracked dark glass
im = Image.new('RGB', (256, 256), (28, 34, 38)); d = ImageDraw.Draw(im); rg = np.random.default_rng(71)
cx, cy = 150, 110
for _ in range(14):
    a = rg.random() * 6.28; L = rg.integers(40, 160)
    d.line([(cx, cy), (cx + L * np.cos(a), cy + L * np.sin(a))], fill=(150, 160, 165), width=1)
for r in (18, 40, 70): d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(110, 120, 125))
im.save(OUT + 'junk-glass.jpg', quality=88)
print('junk textures done')

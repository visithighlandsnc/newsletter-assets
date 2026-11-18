"""Download one tall Canva PNG export and cut it into the email images.

Manifest (incoming/<issue>.json):
  {"url": "...", "out": "2026-11-19", "page_width": 800,
   "pages": [["header.png", 525], ["title-01.png", 56], ...]}
Page heights are in Canva units; the export is scaled to page_width.
"""
import json, sys, urllib.request, io, os
from PIL import Image

m = json.load(open(sys.argv[1]))

# Crop mode: {"crops": [{"url": ..., "out": "2026-11-19/photo-x.jpg",
#   "ratio": 1.25, "anchor": 0.5}]}  ratio = max height / width,
#   anchor = share of the extra height cut from the top (0 top, 0.5 center).
if "crops" in m:
    for c in m["crops"]:
        req = urllib.request.Request(c["url"], headers={"User-Agent": "Mozilla/5.0"})
        im = Image.open(io.BytesIO(urllib.request.urlopen(req).read())).convert("RGB")
        W, H = im.size
        keep_h = min(H, round(W * c.get("ratio", 1.25)))
        top = round((H - keep_h) * c.get("anchor", 0.5))
        os.makedirs(os.path.dirname(c["out"]), exist_ok=True)
        im.crop((0, top, W, top + keep_h)).save(c["out"], quality=88, optimize=True)
        print("cropped", c["out"], W, keep_h)
    sys.exit(0)
data = urllib.request.urlopen(m["url"]).read()
im = Image.open(io.BytesIO(data)).convert("RGB")
W, H = im.size
scale = W / m["page_width"]
total = sum(h for _, h in m["pages"]) * scale
print(f"export {W}x{H}, expected height {total:.0f}")
if abs(total - H) > len(m["pages"]) * 2:
    sys.exit(f"height mismatch: got {H}, expected {total:.0f}")
os.makedirs(m["out"], exist_ok=True)
y = 0.0
for name, h in m["pages"]:
    top, bottom = round(y), round(y + h * scale)
    im.crop((0, top, W, bottom)).save(os.path.join(m["out"], name), optimize=True)
    y += h * scale
print("saved", len(m["pages"]), "images to", m["out"])

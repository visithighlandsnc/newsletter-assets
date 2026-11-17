"""Download one tall Canva PNG export and cut it into the email images.

Manifest (incoming/<issue>.json):
  {"url": "...", "out": "2026-11-19", "page_width": 800,
   "pages": [["header.png", 525], ["title-01.png", 56], ...]}
Page heights are in Canva units; the export is scaled to page_width.
"""
import json, sys, urllib.request, io, os
from PIL import Image

m = json.load(open(sys.argv[1]))
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

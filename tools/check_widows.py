"""Report any paragraph whose last rendered line holds a single word."""
import sys, re
from playwright.sync_api import sync_playwright
src = sys.argv[1]
h = open(src, encoding="utf-8").read()
h = re.sub(r'src="https?://[^"]*"', 'src=""', h)  # layout only
open("/tmp/w.html", "w", encoding="utf-8").write(h)
JS = r"""() => {
 const out=[];
 for (const el of document.querySelectorAll('p, td > a, strong')) {
   const txt = el.innerText.trim(); if (!txt || txt.split(/\s+/).length < 2) continue;
   if (el.tagName==='STRONG') continue;
   // walk text nodes, measure each word's line
   const words=[]; const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
   let n; while ((n=w.nextNode())) { const re=/\S+/g; let m; while ((m=re.exec(n.data))) {
     const r=document.createRange(); r.setStart(n,m.index); r.setEnd(n,m.index+m[0].length);
     const rects=[...r.getClientRects()]; if (rects.length) words.push({w:m[0], top:Math.round(rects[rects.length-1].top)}); } }
   if (words.length<2) continue;
   const lines={}; for (const x of words) (lines[x.top] ||= []).push(x.w);
   const tops=Object.keys(lines).map(Number).sort((a,b)=>a-b);
   if (tops.length>1) { const last=lines[tops[tops.length-1]]; if (last.length===1) out.push(txt.slice(0,70)+' ... ['+last[0]+']'); }
 }
 return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for width in (640, 414, 375, 320):
        pg = b.new_page(viewport={"width": width, "height": 1000})
        pg.goto("file:///tmp/w.html"); pg.wait_for_timeout(300)
        bad = pg.evaluate(JS)
        print(f"width {width}: {len(bad)} single-word lines")
        for x in bad: print("   ", x)
    b.close()

#!/usr/bin/env python3
"""Builds the website into ./dist

  python build.py            build the site
  python build.py --serve    build, then preview at http://localhost:8000

Where things live:
  content.json     all text, links and product data
  images/          original photos (resized automatically)
  templates/       HTML (index.html + partials/)
  static/          style.css and script.js (inlined into the page)
  data/icons.json  social icon drawings
"""
import json, shutil, sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "images", ROOT / "dist"
OUTIMG = OUT / "img"
WIDTHS = (480, 800, 1280)              # sizes generated for every photo


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def process_images():
    """Resize each photo to several widths in WebP + JPG. Returns {name: info}."""
    if OUT.exists():
        shutil.rmtree(OUT)
    OUTIMG.mkdir(parents=True)
    info = {}
    for f in sorted(SRC.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        if f.stem == "logo":           # keep transparency, cap the size
            logo = Image.open(f).convert("RGBA")
            if logo.width > 640:
                logo = logo.resize((640, round(logo.height * 640 / logo.width)), Image.LANCZOS)
            logo.save(OUTIMG / "logo.png", optimize=True)
            info["logo"] = dict(w=logo.width, h=logo.height)
            continue
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        ow, oh = im.size
        widths = sorted({min(w, ow) for w in WIDTHS})   # never enlarge
        for w in widths:
            resized = im if w == ow else im.resize((w, round(oh * w / ow)), Image.LANCZOS)
            resized.save(OUTIMG / f"{f.stem}-{w}.webp", "WEBP", quality=80, method=6)
            resized.save(OUTIMG / f"{f.stem}-{w}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        info[f.stem] = dict(w=widths[-1], h=round(oh * widths[-1] / ow), ws=widths)
    return info


def check_images(content, images):
    """Stop with a clear message if content.json names a photo that doesn't exist."""
    names = [content["hero"]["image"]]
    for cat in content["categories"]:
        for p in cat["products"]:
            names += p.get("img", []) + [n for n, _ in p.get("gal", [])]
    missing = sorted({n for n in names if n not in images})
    if missing:
        sys.exit("ERROR: content.json uses photos that are not in images/: " + ", ".join(missing))


def build():
    content, icons = read_json("content.json"), read_json("data/icons.json")
    images = process_images()
    check_images(content, images)

    socials = [{"name": k, "url": v} for k, v in content["social"].items() if v and k in icons]
    base = content["site"].get("url", "").rstrip("/")
    company = content["company"]
    ld = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": company["name"],
          "telephone": company["phone"], "email": company["email"],
          "address": company["address"], "slogan": company["motto"]}
    if base:
        ld.update(url=base + "/", logo=base + "/img/logo.png")

    hero_img = images[content["hero"]["image"]]
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    page = env.get_template("index.html").render(
        **content, icons=icons, images=images, socials=socials,
        social_map={s["name"]: s["url"] for s in socials}, base=base,
        og_image=f'{base}/img/{content["hero"]["image"]}-{hero_img["ws"][-1]}.jpg', ld=ld,
        css=(ROOT / "static/style.css").read_text(encoding="utf-8"),
        js=(ROOT / "static/script.js").read_text(encoding="utf-8"))

    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    mb = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file()) / 1e6
    print(f"Built {len(images) - 1} photos + logo -> dist/ ({mb:.1f} MB total)")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        print("Preview: http://localhost:8000   (Ctrl+C to stop)")
        handler = partial(SimpleHTTPRequestHandler, directory=str(OUT))
        ThreadingHTTPServer(("", 8000), handler).serve_forever()

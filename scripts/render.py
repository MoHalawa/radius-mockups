"""Render .dc.html artboards (or plain HTML snippets) side by side into one PNG.

usage: python3 scripts/render.py OUT.png TITLE FILE[:LABEL] [FILE[:LABEL] ...]
Each FILE is a .dc.html artboard (content inside <x-dc> is used, <helmet>/scripts dropped)
or a plain .html file (its <body> is used). Each artboard keeps its own fixed size.
"""
import re, sys, html
from playwright.sync_api import sync_playwright

def body_of(src):
    m = re.search(r'<x-dc>(.*)</x-dc>', src, re.S)
    inner = m.group(1) if m else re.search(r'<body[^>]*>(.*)</body>', src, re.S).group(1)
    styles = ''.join(re.findall(r'<style>(.*?)</style>', inner, re.S))
    inner = re.sub(r'<helmet>.*?</helmet>', '', inner, flags=re.S)
    inner = re.sub(r'<script.*?</script>', '', inner, flags=re.S)
    return styles, inner

out, title, items = sys.argv[1], sys.argv[2], sys.argv[3:]
boards, css = [], ''
for it in items:
    path, _, label = it.partition(':')
    s, b = body_of(open(path).read())
    css += s.replace('body{margin:0}', '')
    boards.append(f'<figure><figcaption>{html.escape(label)}</figcaption><div class="ab">{b}</div></figure>')
page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#E9ECEB;font-family:Inter,"Helvetica Neue",Arial,sans-serif}}
.wrap{{display:inline-flex;flex-direction:column;gap:24px;padding:40px}}
h1{{margin:0;font:700 34px/1.2 "Helvetica Neue",Arial,sans-serif;color:#10201D}}
.row{{display:flex;gap:48px;align-items:flex-start}}
figure{{margin:0;display:flex;flex-direction:column;gap:12px}}
figcaption{{font:600 18px Arial,sans-serif;color:#33463F}}
.ab{{box-shadow:0 2px 12px rgba(0,0,0,.12);border-radius:28px;overflow:hidden}}
{css}</style></head><body><div class="wrap"><h1>{html.escape(title)}</h1><div class="row">{''.join(boards)}</div></div></body></html>'''
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(device_scale_factor=1)
    pg.set_content(page, wait_until='load')
    pg.locator('.wrap').screenshot(path=out)
    b.close()
print(out)

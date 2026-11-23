import html
from playwright.sync_api import sync_playwright
from common import *
def render(fields):
    t = (ROOT / "template" / "template.html").read_text()
    for k, val in fields.items():
        t = t.replace("{{%s}}" % k, html.escape(str(val)).replace("\n", "<br>"))
    page = ROOT / "template" / "_rendered.html"; page.write_text(t)
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(page.as_uri()); pg.wait_for_function("window.__ready===true", timeout=30000); pg.wait_for_timeout(500)
        for i in range(1, 6):
            pg.locator(f"#c{i}").screenshot(path=str(OUT / f"slide{i}.jpg"), type="jpeg", quality=95)
        b.close()
if __name__ == "__main__":
    import json; render(json.loads((OUT / "post.json").read_text())["fields"])

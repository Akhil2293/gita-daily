"""Pick the next verse, ask an AI (OpenRouter) for Telugu content, render slides + video."""
import argparse, json, os, re, sys, time, requests
from indic_transliteration import sanscript
from common import *

RAW = "https://raw.githubusercontent.com/gita/gita/main/data/"

def fetch(name):
    BUILD.mkdir(exist_ok=True)
    p = BUILD / name
    if not p.exists():
        r = requests.get(RAW + name, timeout=60); r.raise_for_status(); p.write_bytes(r.content)
    return json.loads(p.read_text())

def sanskrit_te(text):
    t = re.sub(r"[।॥|]+\s*[\d०-९]+\.[\d०-९]+\s*[।॥|]+", " ", text)   # drop "।।2.71।।"
    t = t.replace("॥", " || ").replace("।", " | ")
    t = " ".join(t.split())
    t = sanscript.transliterate(t, sanscript.DEVANAGARI, sanscript.TELUGU)
    return re.sub(r"\s*\|\s*$", "", t).replace(" | ", " | ").strip() + " ||"

PROMPT = """You write daily Bhagavad Gita posts in simple, warm, conversational Telugu for Instagram/YouTube.
Verse {ch}.{v} (Chapter: {chname}).
Sanskrit: {sa}
Reliable English translations (stay faithful to these; do not invent meanings):
- {en1}
- {en2}

Return ONLY JSON with these keys (all values Telugu, no markdown):
"hook": <=110 characters. A curious question for the viewer plus a teaser, ending with "కృష్ణుడు చెప్పిన ఈ మాట జీవితానికి ఒక గొప్ప పాఠం!" style. Example: "అన్నీ ఉన్నా సంతోషంగా ఉండలేకపోతున్నారా? కోరికలను వదిలితేనే నిజమైన శాంతి దొరుకుతుందా? కృష్ణుడు చెప్పిన ఈ మాట జీవితానికి ఒక గొప్ప పాఠం!"
"intro": <=40 words. One sentence of context from the previous verse, then what this verse explains.
"meaning": <=35 words. Clear meaning (భావం) of this verse.
"life_truth": <=60 words. Everyday-life reflection on the problem the verse addresses.
"life_lesson": <=60 words. Practical lessons as short sentences.
"caption": Instagram caption: 3-4 short Telugu lines, a call to follow, then 8-12 hashtags.
"yt_title": <=60 characters Telugu title mentioning the verse number.
Keep it respectful, non-sectarian, no medical/financial claims."""

KEYS = ("hook", "intro", "meaning", "life_truth", "life_lesson", "caption", "yt_title")
def parse(text):
    """Pull the JSON object out of a model reply and make sure it is complete and in Telugu."""
    text = re.sub(r"```(?:json)?", "", text)
    m = re.search(r"\{.*\}", text, re.S)
    d = json.loads(m.group(0))
    if not all(isinstance(d.get(k), str) and d[k].strip() for k in KEYS): raise ValueError("missing keys")
    te = lambda t: sum("\u0c00" <= ch <= "\u0c7f" for ch in t) / max(len(t), 1)
    if te(d["hook"]) < 0.4 or te(d["meaning"]) < 0.4: raise ValueError("not Telugu")
    return d

def ask_openrouter(prompt):
    key = os.environ["OPENROUTER_API_KEY"]
    models = [m.strip() for m in (os.environ.get("OPENROUTER_MODEL") or "openrouter/free").split(",") if m.strip()]
    for i in range(8):
        model = models[i % len(models)]
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", timeout=180,
                              headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                              json={"model": model, "temperature": 0.8, "messages": [{"role": "user", "content": prompt}]})
            if r.status_code == 200:
                print("model used:", r.json().get("model"))
                return parse(r.json()["choices"][0]["message"]["content"])
            print("OpenRouter", model, r.status_code, r.text[:200])
        except Exception as e: print("retry:", model, e)
        time.sleep(10 * (i + 1))
    sys.exit("OpenRouter failed")

def llm(prompt):
    return ask_openrouter(prompt)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--day", type=int); ap.add_argument("--sample", action="store_true")
    a = ap.parse_args()
    day = a.day or load_state()["next_day"]
    verses = fetch("verse.json")
    vo = day + 1                      # Day 117 == verse_order 118 == 2.71
    verse = next((x for x in verses if x["verse_order"] == vo), None)
    if not verse: sys.exit(f"No verse for day {day} (series complete?)")
    ch, v = verse["chapter_number"], verse["verse_number"]
    sa = sanskrit_te(verse["text"])
    if a.sample:
        c = json.loads((ROOT / "data" / "sample_content.json").read_text())
    else:
        tr = [t for t in fetch("translation.json") if t["verse_id"] == verse["id"] and t["lang"] == "english"]
        en = [t["description"] for t in tr[:2]] + ["", ""]
        c = llm(PROMPT.format(ch=ch, v=v, chname=CHAPTERS_TE[ch], sa=verse["text"].strip(), en1=en[0], en2=en[1]))
    fields = dict(day=day, chapter=ch, verse=v, chapter_name=CHAPTERS_TE[ch], sanskrit=sa, hook=c["hook"], intro=c["intro"],
                  meaning=c["meaning"], truth=c["life_truth"], lesson=c["life_lesson"])
    OUT.mkdir(exist_ok=True)
    (OUT / "post.json").write_text(json.dumps(dict(day=day, ref=f"{ch}.{v}", caption=c["caption"], yt_title=c["yt_title"], fields=fields), ensure_ascii=False, indent=2))
    import render, video
    render.render(fields); video.make()
    print(f"Done: day {day}, verse {ch}.{v}")
if __name__ == "__main__": main()

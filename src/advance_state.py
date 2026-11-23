import json
from common import *
post = json.loads((OUT / "post.json").read_text()); day = post["day"]
sp = ROOT / "published" / f"day-{day}" / "status.json"
st = json.loads(sp.read_text()) if sp.exists() else {}
if st.get("instagram") or st.get("youtube"):
    s = load_state()
    if s["next_day"] == day: s["next_day"] = day + 1; save_state(s); print("advanced to day", day + 1)

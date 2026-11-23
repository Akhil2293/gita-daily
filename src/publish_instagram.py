"""Post the 5 slides as an Instagram carousel (Graph API). Needs IG_USER_ID, IG_ACCESS_TOKEN, IMAGE_BASE_URL."""
import json, os, sys, time, requests
from common import *
G = "https://graph.facebook.com" + ("/" + os.environ["GRAPH_VERSION"] if os.environ.get("GRAPH_VERSION") else "")
def call(method, path, **kw):
    for i in range(6):
        r = requests.request(method, f"{G}/{path}", timeout=60, **kw); d = r.json()
        if r.ok: return d
        print("IG error:", d, "- retry"); time.sleep(10)
    sys.exit(f"Instagram failed: {d}")
def main():
    post = json.loads((OUT / "post.json").read_text()); day = post["day"]
    sp = ROOT / "published" / f"day-{day}" / "status.json"; st = json.loads(sp.read_text()) if sp.exists() else {}
    if st.get("instagram"): print("already posted"); return
    uid, tok, base = os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"], os.environ["IMAGE_BASE_URL"].rstrip("/")
    kids = [call("POST", f"{uid}/media", data=dict(image_url=f"{base}/slide{i}.jpg", is_carousel_item="true", access_token=tok))["id"] for i in range(1, 6)]
    for k in kids:
        for _ in range(30):
            if call("GET", k, params=dict(fields="status_code", access_token=tok)).get("status_code") == "FINISHED": break
            time.sleep(4)
    car = call("POST", f"{uid}/media", data=dict(media_type="CAROUSEL", children=",".join(kids), caption=post["caption"], access_token=tok))["id"]
    for _ in range(30):
        if call("GET", car, params=dict(fields="status_code", access_token=tok)).get("status_code") == "FINISHED": break
        time.sleep(4)
    mid = call("POST", f"{uid}/media_publish", data=dict(creation_id=car, access_token=tok))["id"]
    st["instagram"] = mid; sp.write_text(json.dumps(st)); print("Instagram posted", mid)
if __name__ == "__main__": main()

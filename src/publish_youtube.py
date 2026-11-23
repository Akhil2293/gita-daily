"""Upload reel.mp4 as a YouTube Short. Needs YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from common import *
def main():
    post = json.loads((OUT / "post.json").read_text()); day = post["day"]
    sp = ROOT / "published" / f"day-{day}" / "status.json"; st = json.loads(sp.read_text()) if sp.exists() else {}
    if st.get("youtube"): print("already uploaded"); return
    cred = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                       client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"])
    yt = build("youtube", "v3", credentials=cred)
    title = (f"{post['yt_title']} #Shorts")[:100]
    body = dict(snippet=dict(title=title, description=post["caption"] + "\n\n#Shorts #BhagavadGita #Telugu", categoryId="27",
                             tags=["Bhagavad Gita", "Telugu", "Gita", "Shorts", f"Gita {post['ref']}"], defaultLanguage="te"),
                status=dict(privacyStatus=os.environ.get("YT_PRIVACY", "public"), selfDeclaredMadeForKids=False))
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(str(OUT / "reel.mp4"), mimetype="video/mp4", resumable=True))
    r = None
    while r is None: _, r = req.next_chunk()
    st["youtube"] = r["id"]; sp.write_text(json.dumps(st)); print("YouTube uploaded", r["id"])
if __name__ == "__main__": main()

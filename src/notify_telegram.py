"""Optional: send the slides to your Telegram so you can review before approving. Needs TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID."""
import json, os, requests
from common import *
t, c = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
if t and c:
    post = json.loads((OUT / "post.json").read_text())
    files = {f"p{i}": open(OUT / f"slide{i}.jpg", "rb") for i in range(1, 6)}
    media = [dict(type="photo", media=f"attach://p{i}", **({"caption": f"Day {post['day']} ({post['ref']}) - approve the run in GitHub Actions to publish"} if i == 1 else {})) for i in range(1, 6)]
    requests.post(f"https://api.telegram.org/bot{t}/sendMediaGroup", data=dict(chat_id=c, media=json.dumps(media)), files=files, timeout=120)

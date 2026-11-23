# Daily Bhagavad Gita auto-poster (free, GitHub Actions)

Every day at 06:00 IST: next verse → Gemini writes Telugu text → 5 slides (JPG) + 25 s vertical video →
**you approve with one click** → Instagram carousel + YouTube Short are posted → counter moves to the next day.

Verse text (Sanskrit → Telugu script) and English translations come from the free `gita/gita` dataset, so the AI never invents the shloka.
Day N = verse order N+1 (Day 117 = 2.71). `state.json` holds the next day (starts at 118).

## One-time setup
1. **Create a PUBLIC GitHub repo** and upload everything in this folder (including the hidden `.github` folder).
   Public is needed because Instagram downloads the slide images from `raw.githubusercontent.com`, and free approval gates need a public repo.
2. **Settings → Actions → General → Workflow permissions → Read and write.**
3. **Settings → Environments → New environment `production` → Required reviewers → add yourself.** (This is the approval step.)
4. **Settings → Secrets and variables → Actions → add secrets:**

| Secret | Where to get it |
|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey (free tier) |
| `IG_USER_ID`, `IG_ACCESS_TOKEN` | Instagram **Business/Creator** account linked to a Facebook Page. Create an app at developers.facebook.com, add *Instagram Graph API*, permissions `instagram_basic`, `instagram_content_publish`, `pages_show_list`. Generate a long-lived **Page** access token (Page tokens made from a long-lived user token don't expire). `IG_USER_ID` = the Instagram business account id. |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | console.cloud.google.com → new project → enable **YouTube Data API v3** → OAuth consent screen → create **Desktop** OAuth client, download JSON → run `python tools/get_youtube_token.py client_secret.json` once. Set the consent screen to **In production** (in "Testing" the refresh token dies after 7 days). |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | *Optional.* Sends the 5 slides to your phone for review before you approve. |

Skip a platform by simply not adding its secrets.

5. **Actions → Daily Gita post → Run workflow** to test. Approve the `publish` job when it asks. Slides/video are also downloadable from the run's *Artifacts*.

## Good to know
- **YouTube:** new API projects that haven't passed Google's audit upload as **private**. Request the audit, or set repo variable `YT_PRIVACY=private` and publish manually meanwhile.
- **Optional variables** (Settings → Variables): `GEMINI_MODEL` (default `gemini-2.5-flash`; change if Google retires it), `GRAPH_VERSION` (blank = your app's default), `SLIDE_SECONDS` via workflow env (default `4,5,6,6,4`).
- **Music:** put a royalty-free `music.mp3` in `template/assets/` and it's added to the video automatically.
- **Edit the look:** `template/template.html` + `template/assets/` (backgrounds, fonts). Text boxes auto-shrink if the AI writes too much.
- **Test locally:** `pip install -r requirements.txt && playwright install chromium && python src/generate.py --day 117 --sample` → files appear in `out/`.
- **Skip/redo a day:** edit `state.json`, or run the workflow with a specific day number.
- AI text is only a draft. You are the approver — read the slides before you click approve.

"""Run ONCE on your own computer to get YT_REFRESH_TOKEN.
pip install google-auth-oauthlib ; python tools/get_youtube_token.py client_secret.json"""
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
f = InstalledAppFlow.from_client_secrets_file(sys.argv[1], ["https://www.googleapis.com/auth/youtube.upload"])
c = f.run_local_server(port=0, access_type="offline", prompt="consent")
print("\nYT_CLIENT_ID     =", c.client_id, "\nYT_CLIENT_SECRET =", c.client_secret, "\nYT_REFRESH_TOKEN =", c.refresh_token)

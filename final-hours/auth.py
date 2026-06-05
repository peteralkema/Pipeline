"""
auth.py — One-time OAuth handshake for the Final Hours channel.

Run this ONCE. It opens a browser, asks you to log in to peteralkema2@gmail.com,
and then asks which channel to authorise. Pick "Final Hours" from the chooser.
It writes token.json to disk, which the upload script reads from now on.

If you ever revoke access or the token expires beyond refresh, delete the token
file and run this again.

Run:
    python3 auth.py
"""

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Zscaler cert handling — same pattern as the rest of the pipeline.
CERT_BUNDLE = os.path.expanduser("~/combined_cacert.pem")
if os.path.exists(CERT_BUNDLE):
    os.environ.setdefault("SSL_CERT_FILE", CERT_BUNDLE)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", CERT_BUNDLE)

# Scopes must MATCH upload.py exactly, or token refresh fails with
# invalid_scope. upload = publish the video; force-ssl = attach captions (SRT)
# and set the thumbnail via the API.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

CLIENT_SECRET = "client_secret.json"
TOKEN_FILE    = "token.json"


def main():
    if not os.path.exists(CLIENT_SECRET):
        raise SystemExit(
            f"Missing {CLIENT_SECRET}.\n"
            "Download the OAuth client JSON from Google Cloud Console and "
            "drop it in this folder, named exactly client_secret.json"
        )

    credentials = None

    # If a token already exists, try to use it (refresh if needed)
    if os.path.exists(TOKEN_FILE):
        print(f"Found existing {TOKEN_FILE} — checking if it's still valid...")
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if credentials and credentials.valid:
            print("OK Token is valid. Nothing to do.")
            return
        if credentials and credentials.expired and credentials.refresh_token:
            print("Token expired, refreshing...")
            credentials.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(credentials.to_json())
            print("OK Token refreshed.")
            return

    # No valid token — run the full OAuth flow
    print("Starting browser-based OAuth flow...")
    print("A browser window will open. Log in to peteralkema2@gmail.com,")
    print("and IMPORTANTLY: pick the 'Final Hours' channel from the chooser,")
    print("NOT the Success Coach channel.\n")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    credentials = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())

    print(f"\nOK Token saved -> {TOKEN_FILE}")
    print("This token is now bound to the Final Hours channel. The upload script")
    print("will use it automatically. You won't need to re-run this unless you")
    print("revoke access or delete the token file.")


if __name__ == "__main__":
    main()

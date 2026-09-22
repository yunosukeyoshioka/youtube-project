"""Real YouTube Data API v3 publisher using OAuth 2.0 (installed app flow).

Setup:
1. In Google Cloud Console, create an OAuth client ID (type: Desktop app) for
   a project with the YouTube Data API v3 enabled.
2. Download the client secret JSON and point `youtube_client_secrets_file`
   in config.yaml at it.
3. First run opens a browser for consent; the resulting token is cached at
   `youtube_token_file` and reused after that.
"""

from __future__ import annotations

from pathlib import Path

from ...models import MarketingPackage, PublishResult
from .base import YouTubePublisher

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeApiPublisher(YouTubePublisher):
    def __init__(self, client_secrets_file: str, token_file: str) -> None:
        self._client_secrets_file = client_secrets_file
        self._token_file = token_file

    def _get_credentials(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        token_path = Path(self._token_file)
        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path(self._client_secrets_file).exists():
                    raise FileNotFoundError(
                        f"YouTube OAuth client secrets file not found at "
                        f"{self._client_secrets_file!r}. See "
                        "providers/youtube/youtube_api_provider.py for setup steps."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._client_secrets_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def publish(
        self,
        video_path: str,
        thumbnail_path: str,
        marketing: MarketingPackage,
        privacy_status: str = "private",
    ) -> PublishResult:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        youtube = build("youtube", "v3", credentials=self._get_credentials())

        body = {
            "snippet": {
                "title": marketing.chosen_title[:100],
                "description": marketing.description,
                "tags": marketing.tags,
                "categoryId": "22",
            },
            "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False},
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            _, response = request.next_chunk()
        video_id = response["id"]

        if thumbnail_path and Path(thumbnail_path).exists():
            youtube.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(thumbnail_path)
            ).execute()

        return PublishResult(
            published=True,
            video_id=video_id,
            url=f"https://www.youtube.com/watch?v={video_id}",
        )

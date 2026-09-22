"""Premium TTS via the ElevenLabs API. Requires ELEVENLABS_API_KEY. Produces
much more natural narration than the offline providers; recommended once
you're ready to publish real videos."""

from __future__ import annotations

import requests

from .base import TTSProvider, estimate_duration_seconds

ELEVENLABS_ENDPOINT = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # ElevenLabs' public "Rachel" voice


class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self, api_key: str, voice_id: str = DEFAULT_VOICE_ID) -> None:
        self._api_key = api_key
        self._voice_id = voice_id

    def synthesize(self, text: str, output_path: str) -> float:
        response = requests.post(
            ELEVENLABS_ENDPOINT.format(voice_id=self._voice_id),
            headers={"xi-api-key": self._api_key, "Accept": "audio/mpeg"},
            json={"text": text, "model_id": "eleven_multilingual_v2"},
            timeout=60,
        )
        response.raise_for_status()
        with open(output_path, "wb") as fh:
            fh.write(response.content)
        return estimate_duration_seconds(text)

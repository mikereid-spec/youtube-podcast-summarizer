"""Service for extracting YouTube video transcripts."""
import re
import os
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


class YouTubeService:
    """Handles YouTube video transcript extraction."""

    def __init__(self):
        """Initialize YouTube service with optional proxy configuration."""
        # Optional Webshare proxy credentials for bypassing cloud IP blocks
        self.proxy_username = os.getenv("WEBSHARE_PROXY_USERNAME")
        self.proxy_password = os.getenv("WEBSHARE_PROXY_PASSWORD")

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_transcript(self, video_id: str) -> dict:
        """
        Fetch transcript for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            dict with 'text' and 'metadata'
        """
        try:
            # Use Webshare proxy if credentials are provided (for cloud hosting)
            proxies = None
            if self.proxy_username and self.proxy_password:
                from youtube_transcript_api._settings import WebshareProxyConfig
                proxies = WebshareProxyConfig(
                    proxy_username=self.proxy_username,
                    proxy_password=self.proxy_password
                )

            kwargs = {}
            if proxies:
                kwargs['proxies'] = proxies

            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, **kwargs)

            # Combine all transcript segments into full text
            full_text = " ".join([entry['text'] for entry in transcript_list])

            # Calculate duration
            duration = transcript_list[-1]['start'] + transcript_list[-1]['duration'] if transcript_list else 0

            return {
                "text": full_text,
                "metadata": {
                    "video_id": video_id,
                    "duration_seconds": duration,
                    "segment_count": len(transcript_list)
                }
            }
        except TranscriptsDisabled:
            return {"error": "Transcripts are disabled for this video"}
        except NoTranscriptFound:
            return {"error": "No transcript available"}
        except Exception as e:
            return {"error": f"Error fetching transcript: {str(e)}"}

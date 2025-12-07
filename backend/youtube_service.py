"""Service for extracting YouTube video transcripts."""
import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


class YouTubeService:
    """Handles YouTube video transcript extraction."""

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

    @staticmethod
    def get_transcript(video_id: str) -> dict:
        """
        Fetch transcript for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            dict with 'text' and 'metadata'
        """
        try:
            # Use the API - instantiate and fetch
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id)

            # Convert to raw data (list of dicts)
            transcript_list = transcript.to_raw_data()

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

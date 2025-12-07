"""Service for interacting with OpenAI API."""
from openai import OpenAI
from typing import List, Dict
import os


class ClaudeService:
    """Handles interactions with OpenAI's API."""

    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://gw.datawizz.app/47dc517053c5e9dc/openai/v1"
        )
        self.model = "production"

    def summarize_transcript(self, transcript: str, video_metadata: dict) -> str:
        """
        Generate a comprehensive summary of a video transcript.

        Args:
            transcript: Full video transcript text
            video_metadata: Metadata about the video

        Returns:
            Summary text
        """
        duration_minutes = int(video_metadata.get('duration_seconds', 0) // 60)

        prompt = f"""Summarize this {duration_minutes}-minute YouTube video transcript.

Provide:
- **Main Topic** (1-2 sentences)
- **Key Points** (5-7 bullet points, each 1-2 sentences)
- **Notable Quotes** (2-3 direct quotes worth remembering—skip this section if none stand out)
- **Takeaways** (2-3 actionable insights or conclusions)

Keep the total summary under 400 words.

If the transcript is unclear, incomplete, or appears to be auto-generated with errors, note this briefly and summarize what you can confidently extract.

Transcript:
{transcript}"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
            extra_body={
                "metadata": {
                    "task": "summary",
                    "video_id": video_metadata.get('video_id'),
                    "duration_seconds": video_metadata.get('duration_seconds'),
                    "segment_count": video_metadata.get('segment_count')
                }
            }
        )

        return response.choices[0].message.content

    def chat_about_content(
        self,
        transcript: str,
        conversation_history: List[Dict[str, str]],
        user_question: str,
        video_id: str = None
    ) -> str:
        """
        Answer questions about the video content using the transcript.

        Args:
            transcript: Full video transcript
            conversation_history: Previous messages in the conversation
            user_question: Current user question
            video_id: YouTube video ID for logging

        Returns:
            Assistant's response
        """
        system_prompt = f"""You are a helpful assistant that answers questions about a YouTube video.

Here is the full transcript:
{transcript}

Answer questions accurately based on the content. If something isn't covered in the video, say so."""

        # Build conversation history with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_question})

        response = self.client.chat.completions.create(
            model=self.model,
            max_completion_tokens=1024,
            messages=messages,
            extra_body={
                "metadata": {
                    "task": "chat",
                    "video_id": video_id,
                    "message_count": len(conversation_history) + 1
                }
            }
        )

        return response.choices[0].message.content

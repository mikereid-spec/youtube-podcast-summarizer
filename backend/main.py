"""Main FastAPI application for YouTube Podcast Summarizer."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

from youtube_service import YouTubeService
from claude_service import ClaudeService

# Load environment variables from parent directory (override system env vars)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path, override=True)

app = FastAPI(title="YouTube Podcast Summarizer")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend/templates")

# Initialize services
# Use DATAWIZZ_API_KEY for the datawizz gateway, fallback to OPENAI_API_KEY for backward compatibility
api_key = os.getenv("DATAWIZZ_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("DATAWIZZ_API_KEY or OPENAI_API_KEY environment variable is required")

youtube_service = YouTubeService()
claude_service = ClaudeService(api_key)

# In-memory storage for sessions (in production, use a proper database)
sessions: Dict[str, Dict] = {}


class SummarizeRequest(BaseModel):
    youtube_url: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class SummarizeResponse(BaseModel):
    session_id: str
    summary: str
    video_metadata: dict


class ChatResponse(BaseModel):
    response: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_video(request: SummarizeRequest):
    """
    Extract transcript from YouTube video and generate summary.
    """
    try:
        # Extract video ID
        video_id = youtube_service.extract_video_id(request.youtube_url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        # Get transcript
        transcript_data = youtube_service.get_transcript(video_id)

        # Check for errors
        if "error" in transcript_data:
            raise HTTPException(status_code=400, detail=transcript_data["error"])

        # Generate summary
        summary = claude_service.summarize_transcript(
            transcript_data["text"],
            transcript_data["metadata"]
        )

        # Create session
        import uuid
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "transcript": transcript_data["text"],
            "summary": summary,
            "metadata": transcript_data["metadata"],
            "conversation_history": []
        }

        return SummarizeResponse(
            session_id=session_id,
            summary=summary,
            video_metadata=transcript_data["metadata"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat about the video content.
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]

    try:
        # Get response from Claude
        response = claude_service.chat_about_content(
            transcript=session["transcript"],
            conversation_history=session["conversation_history"],
            user_question=request.message,
            video_id=session["metadata"].get("video_id")
        )

        # Update conversation history
        session["conversation_history"].append({"role": "user", "content": request.message})
        session["conversation_history"].append({"role": "assistant", "content": response})

        return ChatResponse(response=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

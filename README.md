# YouTube Podcast Summarizer

A web application that extracts transcripts from YouTube videos, generates AI-powered summaries using Claude, and allows you to have interactive conversations about the content.

## Features

- **Transcript Extraction**: Automatically extracts transcripts from YouTube videos
- **AI Summarization**: Uses Claude to generate comprehensive summaries including:
  - Main topic
  - Key points
  - Notable quotes
  - Conclusions and takeaways
- **Interactive Chat**: Ask questions about the video content and get informed answers
- **Modern UI**: Clean, dark-themed web interface

## Prerequisites

- Python 3.8+
- Anthropic API key (get one at https://console.anthropic.com)

## Installation

1. Clone or navigate to the project directory:
```bash
cd youtube-podcast-summarizer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Then edit `.env` and add your Datawizz API key:
```
DATAWIZZ_API_KEY=your_datawizz_api_key_here
```

**Optional: For cloud hosting (Railway, AWS, etc.)**

YouTube blocks requests from cloud provider IPs. To fix this, you need rotating residential proxies:

1. Sign up at [Webshare](https://www.webshare.io/) and purchase a "Residential" proxy package (~$10-30/month)
2. Add your credentials to `.env`:
```
WEBSHARE_PROXY_USERNAME=your_webshare_username
WEBSHARE_PROXY_PASSWORD=your_webshare_password
```

**Note:** Without proxies, the app will work locally but not when hosted on cloud platforms.

## Usage

1. Start the server:
```bash
cd backend
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Paste a YouTube URL and click "Summarize"

4. Once the summary is generated, you can ask questions about the video content

## API Endpoints

- `GET /` - Web interface
- `POST /api/summarize` - Summarize a YouTube video
- `POST /api/chat` - Chat about video content
- `GET /api/health` - Health check

## Project Structure

```
youtube-podcast-summarizer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── youtube_service.py   # YouTube transcript extraction
│   └── claude_service.py    # Claude API integration
├── frontend/
│   ├── templates/
│   │   └── index.html       # Web interface
│   └── static/
│       ├── app.js           # Frontend JavaScript
│       └── styles.css       # Styling
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Technologies Used

- **Backend**: FastAPI, Python
- **AI**: Anthropic Claude (Sonnet 4)
- **YouTube API**: youtube-transcript-api
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## Notes

- The application stores sessions in memory. For production use, consider using a proper database.
- Some YouTube videos may not have transcripts available.
- API costs apply for Claude API usage.

## License

MIT

<div align="center">

# 🎵 YouTube to MP3

[![CI](https://github.com/tomyanzhiyuan/ytmp3-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/tomyanzhiyuan/ytmp3-scraper/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-72%20passed-brightgreen.svg)](https://github.com/tomyanzhiyuan/ytmp3-scraper/actions)

**Download audio or video from YouTube channels as MP3 or MP4 files. Filter by content type (videos/shorts) and time frame.**

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-endpoints) • [Contributing](#-contributing)

<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
<img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
<img src="https://img.shields.io/badge/yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="yt-dlp" />

</div>

---

> ⚠️ **Disclaimer**: This tool is for **personal and educational use only**. Respect copyright laws and YouTube's Terms of Service. See [DISCLAIMER.md](DISCLAIMER.md) for full legal notice.

---

## ✨ Features

- 🎯 **Content Type Filtering**: Choose between Videos only, Shorts only, or All content
- ⏱️ **Time Frame Filtering**: Last week, month, year, or all time
- 🔍 **Accurate Short Detection**: Verified via YouTube's `/shorts/` URL (no false positives)
- 🚀 **Complete Channel Scraping**: Uses YouTube Data API v3 to fetch ALL videos (no limits!)
- 🎵 **High-Quality Audio**: Downloads and converts to 320kbps MP3
- 🎬 **Video Downloads**: Also supports MP4 video format
- 🖥️ **Clean UI**: Minimalistic React interface with real-time progress
- ✅ **Selective Downloads**: Choose specific videos or download all at once
- 🔄 **Smart Fallback**: Automatically falls back to yt-dlp if no API key
- 🧪 **Well Tested**: 72+ unit tests covering all edge cases

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - Modern async web framework
- **YouTube Data API v3** - Complete channel video listing
- **yt-dlp** - YouTube video download and MP3 conversion
- **FFmpeg** - Audio conversion
- **Pydantic** - Data validation
- **python-dotenv** - Environment variable management

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/tomyanzhiyuan/ytmp3-scraper.git
cd ytmp3-scraper

# Run with Docker Compose
docker compose up --build

# Open http://localhost:8000 in your browser
```

### Using Conda

```bash
# Clone and setup
git clone https://github.com/tomyanzhiyuan/ytmp3-scraper.git
cd ytmp3-scraper
conda env create -f environment.yml
conda activate ytmp3-scraper

# Start backend (Terminal 1)
cd backend && uvicorn main:app --reload --port 8000

# Start frontend (Terminal 2)
cd frontend && npm install && npm run dev
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Conda** (Anaconda or Miniconda)
   - **macOS/Linux**: Download from [conda.io](https://docs.conda.io/en/latest/miniconda.html)
   - **Windows**: Download from [conda.io](https://docs.conda.io/en/latest/miniconda.html)

   Verify installation:
   ```bash
   conda --version
   ```

**Note:** The Conda environment will automatically install Python 3.11, Node.js 18+, and FFmpeg, avoiding dependency conflicts.

## 🚀 Installation

### 1. Clone the Repository
```bash
cd ytmp3-scraper
```

### 2. Create Conda Environment

```bash
# Create and activate the Conda environment
conda env create -f environment.yml
conda activate ytmp3-scraper
```

This single command will install:
- Python 3.11
- FFmpeg (no separate installation needed!)
- Node.js 18+
- All Python dependencies (FastAPI, yt-dlp, etc.)

### 3. YouTube API Setup (Optional but Recommended)

To fetch ALL videos from a channel (not just ~360), you need a YouTube Data API key:

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Create a new project** (or select existing)
3. **Enable YouTube Data API v3**:
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. **Create API Key**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the generated API key
5. **Add to environment**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and paste your API key
   ```

**Benefits:**
- ✅ Fetch ALL videos (no 360 limit)
- ✅ Much faster (5 seconds vs 15 minutes)
- ✅ 10,000 free requests/day

**Without API key:**
- ⚠️ Limited to ~360 videos per channel
- ⚠️ Slower scraping
- ✅ Still works for smaller channels

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## 🎮 Usage

### Starting the Application

You'll need two terminal windows:

#### Terminal 1 - Backend Server
```bash
# Activate Conda environment
conda activate ytmp3-scraper

# Navigate to backend and start server
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

#### Terminal 2 - Frontend Dev Server
```bash
# Activate Conda environment (if not already active)
conda activate ytmp3-scraper

# Navigate to frontend and start dev server
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Using the Application

1. **Open your browser** to `http://localhost:5173`

2. **Enter a YouTube channel URL** in the input field
   - Example: `https://www.youtube.com/@channelname`
   - Or: `https://www.youtube.com/c/channelname`

3. **Click "Scrape Videos"** to fetch all eligible videos from the channel

4. **Review the video list** - Videos are filtered based on your selections:
   - **Video Type**: Videos only, Shorts only, or All content
   - **Time Frame**: Last week, month, year, or all time
   - Livestreams are always excluded

5. **Select videos** to download:
   - Check individual videos
   - Or click "Download All"

6. **Monitor progress** as downloads complete

7. **Find your MP3 files** in the `output/` directory

## 📁 Project Structure

```
ytmp3-scraper/
├── backend/
│   ├── main.py                 # FastAPI application & routes
│   ├── video_scraper.py        # Hybrid scraper (API + yt-dlp fallback)
│   ├── youtube_api_scraper.py  # YouTube Data API v3 implementation
│   ├── downloader.py           # Video download & MP3 conversion
│   ├── models.py               # Pydantic data models
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (API key)
│   └── .env.example            # Environment template
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── main.tsx            # React entry point
│   │   ├── api.ts              # API client (Axios)
│   │   └── components/
│   │       ├── ChannelInput.tsx      # URL input component
│   │       ├── VideoList.tsx         # Video display & selection
│   │       ├── ScrapeProgress.tsx    # Scraping progress indicator
│   │       └── DownloadProgress.tsx  # Download progress tracking
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── output/                     # Downloaded MP3 files (auto-created)
├── .clinerules                 # AI assistant guidelines
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

### `POST /api/scrape`
Scrapes a YouTube channel and returns filtered video metadata.

**Request:**
```json
{
  "channel_url": "https://www.youtube.com/@channelname",
  "video_type": "videos",
  "time_frame": "all"
}
```

**Parameters:**
- `channel_url` (required): YouTube channel URL
- `video_type` (optional): `"all"`, `"shorts"`, or `"videos"` (default: `"videos"`)
- `time_frame` (optional): `"all"`, `"week"`, `"month"`, or `"year"` (default: `"all"`)

**Response:**
```json
{
  "videos": [
    {
      "id": "video_id",
      "title": "Video Title",
      "duration": 180,
      "thumbnail": "https://...",
      "url": "https://youtube.com/watch?v=..."
    }
  ]
}
```

### `POST /api/download`
Downloads selected videos in the specified format (MP3 or MP4).

**Request:**
```json
{
  "video_ids": ["video_id_1", "video_id_2"],
  "format": "mp3"
}
```

**Parameters:**
- `video_ids` (required): Array of YouTube video IDs
- `format` (optional): `"mp3"` for audio or `"mp4"` for video (default: `"mp3"`)

**Response:**
```json
{
  "message": "MP3 download started",
  "total": 2
}
```

### `GET /api/progress`
Returns current download progress.

**Response:**
```json
{
  "current": 1,
  "total": 5,
  "percentage": 20,
  "status": "downloading",
  "current_video": "Video Title"
}
```

### `GET /api/files`
Lists all downloaded MP3 files.

**Response:**
```json
{
  "files": ["video1.mp3", "video2.mp3"]
}
```

## ⚙️ Configuration

### Backend Configuration

Edit `backend/main.py` to customize:
- **CORS origins**: Add additional allowed origins
- **Output directory**: Change MP3 save location
- **Port**: Modify server port

### Frontend Configuration

Edit `frontend/src/api.ts` to customize:
- **API base URL**: Change backend endpoint
- **Request timeout**: Adjust timeout duration

### Download Settings

Edit `backend/downloader.py` to customize:
- **Audio quality**: Change MP3 bitrate (default: 320kbps)
- **File naming**: Modify output template
- **yt-dlp options**: Add additional download options

## 🔧 Conda Environment Management

### Useful Commands

```bash
# List all Conda environments
conda env list

# Activate the environment
conda activate ytmp3-scraper

# Deactivate the current environment
conda deactivate

# Update the environment (after modifying environment.yml)
conda env update -f environment.yml --prune

# Remove the environment completely
conda env remove -n ytmp3-scraper

# Export current environment to a file
conda env export > environment_backup.yml
```

### Updating Dependencies

If you need to update Python packages:

1. Edit `environment.yml` to change package versions
2. Run: `conda env update -f environment.yml --prune`
3. Restart your terminal and reactivate: `conda activate ytmp3-scraper`

## 🐛 Troubleshooting

### "FFmpeg not found"
- If using Conda: FFmpeg should be automatically installed. Try `conda activate ytmp3-scraper` and verify with `ffmpeg -version`
- If FFmpeg is missing, reinstall the environment: `conda env remove -n ytmp3-scraper && conda env create -f environment.yml`
- Restart your terminal after installation

### "CORS Error" in browser
- Ensure backend is running on port 8000
- Check CORS configuration in `backend/main.py`
- Verify frontend is accessing correct API URL

### "No videos found"
- Verify the channel URL is correct
- Some channels may have all videos as Shorts or livestreams
- Check if the channel is public and accessible

### Downloads fail or hang
- Check your internet connection
- Some videos may be region-restricted
- Verify FFmpeg is working: `ffmpeg -version`
- Check backend logs for detailed error messages

### Port already in use
- Backend: Change port in uvicorn command: `--port 8001`
- Frontend: Vite will automatically try the next available port

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Run all tests
cd backend
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test class
python -m pytest tests/test_short_detection.py::TestShortDetection -v
```

**Test Coverage:**
- Short detection (12 tests)
- Channel resolution (10 tests)
- Time frame filtering (5 tests)
- Duration parsing (8 tests)
- Video filtering logic (5 tests)
- URL parsing edge cases (11 tests)
- API error handling (3 tests)
- And more...

## 🔒 Legal & Security

> ⚠️ **Read the full [DISCLAIMER.md](DISCLAIMER.md) before using this tool.**

- **Personal use only** - Do not use for commercial purposes
- **Respect copyright** - Only download content you have rights to
- **Terms of Service** - Usage may violate YouTube's ToS
- **Your responsibility** - You are liable for how you use this tool
- **No secrets in repo** - API keys are gitignored, use `.env` files

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful YouTube downloader
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Tailwind CSS](https://tailwindcss.com/) - Styling framework

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Happy downloading! 🎵**

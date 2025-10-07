# YouTube MP3 Scraper & Downloader

A full-stack web application that scrapes YouTube channels, filters videos, and downloads them as high-quality MP3 files.

## ✨ Features

- 🎯 **Smart Filtering**: Automatically filters out YouTube Shorts and livestreams
- ⏱️ **Duration Filter**: Only downloads videos longer than 1 minute
- 🎵 **High-Quality Audio**: Downloads and converts to 320kbps MP3
- 🖥️ **Modern UI**: Clean, responsive React interface with Tailwind CSS
- 📊 **Progress Tracking**: Real-time download progress updates
- ✅ **Selective Downloads**: Choose specific videos or download all at once
- 🚀 **Fast & Async**: Non-blocking downloads using FastAPI background tasks

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - Modern async web framework
- **yt-dlp** - YouTube video extraction and download
- **FFmpeg** - Audio conversion
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.11 or higher**
   ```bash
   python --version
   ```

2. **Node.js 18 or higher**
   ```bash
   node --version
   ```

3. **FFmpeg** (required for audio conversion)
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

   Verify installation:
   ```bash
   ffmpeg -version
   ```

## 🚀 Installation

### 1. Clone the Repository
```bash
cd ytmp3-scraper
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## 🎮 Usage

### Starting the Application

You'll need two terminal windows:

#### Terminal 1 - Backend Server
```bash
cd backend
source venv/bin/activate  # If using virtual environment
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

#### Terminal 2 - Frontend Dev Server
```bash
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

4. **Review the video list** - Videos are automatically filtered to:
   - Duration > 1 minute
   - Exclude YouTube Shorts
   - Exclude livestreams

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
│   ├── video_scraper.py        # YouTube channel scraping logic
│   ├── downloader.py           # Video download & MP3 conversion
│   ├── models.py               # Pydantic data models
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main application component
│   │   ├── main.tsx            # React entry point
│   │   ├── api.ts              # API client (Axios)
│   │   └── components/
│   │       ├── ChannelInput.tsx      # URL input component
│   │       ├── VideoList.tsx         # Video display & selection
│   │       └── DownloadProgress.tsx  # Progress tracking
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
  "channel_url": "https://www.youtube.com/@channelname"
}
```

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
Downloads selected videos and converts them to MP3.

**Request:**
```json
{
  "video_ids": ["video_id_1", "video_id_2"]
}
```

**Response:**
```json
{
  "message": "Download started",
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

## 🐛 Troubleshooting

### "FFmpeg not found"
- Ensure FFmpeg is installed and in your system PATH
- Restart your terminal after installation
- Verify with `ffmpeg -version`

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

## 🔒 Security Notes

- This tool is for personal use only
- Respect YouTube's Terms of Service
- Only download content you have rights to
- Be mindful of copyright laws in your jurisdiction
- Rate limiting is recommended for production use

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

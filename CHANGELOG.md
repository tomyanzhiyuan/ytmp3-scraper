# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-14

### Added
- Complete channel scraping with YouTube Data API v3 support
- Smart fallback to yt-dlp when no API key is provided
- Advanced filtering: excludes Shorts, livestreams, and videos under 1 minute
- High-quality 320kbps MP3 conversion
- Modern React frontend with real-time progress updates
- Docker support for easy deployment
- Rate limiting protection with exponential backoff
- Channel-based subfolder organization for downloads
- Duplicate detection to skip already downloaded files

### Features
- Scrape entire YouTube channels (no 360 video limit with API key)
- Selective or bulk video downloading
- Real-time scraping and download progress
- Beautiful, responsive UI with Tailwind CSS

[1.0.0]: https://github.com/tomyanzhiyuan/ytmp3-scraper/releases/tag/v1.0.0

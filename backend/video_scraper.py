"""
YouTube channel video scraper using YouTube Data API (with yt-dlp fallback)
"""
import yt_dlp
from typing import List, Dict
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_channel_videos(channel_url: str, progress_callback=None) -> tuple[str, List[Dict]]:
    """
    Scrape all videos from a YouTube channel.
    Tries YouTube Data API first (if API key available), falls back to yt-dlp.
    
    Args:
        channel_url: YouTube channel URL
        progress_callback: Optional callback function(total, processed, filtered, current_title)
        
    Returns:
        Tuple of (channel_name, list of video metadata dictionaries)
    """
    # Try YouTube Data API first if API key is available
    api_key = os.getenv('YOUTUBE_API_KEY')
    if api_key:
        try:
            logger.info("Using YouTube Data API for scraping")
            from youtube_api_scraper import YouTubeAPIScraper
            
            scraper = YouTubeAPIScraper(api_key)
            return scraper.scrape_channel_videos(channel_url, progress_callback)
        except Exception as e:
            logger.warning(f"YouTube API failed: {e}. Falling back to yt-dlp...")
    else:
        logger.info("No YouTube API key found. Using yt-dlp (limited to ~360 videos)")
    
    # Fallback to yt-dlp
    return _scrape_with_ytdlp(channel_url, progress_callback)


def _scrape_with_ytdlp(channel_url: str, progress_callback=None) -> tuple[str, List[Dict]]:
    """
    Scrape all videos from a YouTube channel and filter them.
    
    Args:
        channel_url: YouTube channel URL
        progress_callback: Optional callback function(total, processed, filtered, current_title)
        
    Returns:
        Tuple of (channel_name, list of video metadata dictionaries)
        
    Raises:
        Exception: If scraping fails
    """
    # First pass: Get video list quickly with extract_flat
    ydl_opts_flat = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
        'playlistend': None,  # Get all videos, not just first page
        'lazy_playlist': False,  # Force full playlist extraction
        'playlist_items': '1-10000',  # Fetch up to 10000 videos
    }
    
    try:
        logger.info(f"Scraping channel: {channel_url}")
        
        # Ensure we're fetching from the videos tab, not just featured
        if '/videos' not in channel_url:
            if channel_url.endswith('/'):
                channel_url = channel_url + 'videos'
            else:
                channel_url = channel_url + '/videos'
        
        logger.info(f"Fetching from: {channel_url}")
        
        # Step 1: Get video IDs and basic info quickly
        with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            
            if not result:
                raise Exception("Failed to extract channel information")
            
            channel_name = result.get('uploader') or result.get('channel') or 'unknown_channel'
            entries = result.get('entries', [])
            
            if not entries:
                logger.warning("No videos found in channel")
                return channel_name, []
            
            logger.info(f"Found {len(entries)} total videos from {channel_name}")
            
            # Filter videos and track reasons
            filtered_videos = []
            filter_reasons = {
                'shorts': 0,
                'livestreams': 0,
                'missing_data': 0
            }
            processed_count = 0
            total_count = len(entries)
            
            for idx, entry in enumerate(entries, 1):
                if not entry:
                    continue
                
                # Get video metadata
                video_id = entry.get('id')
                title = entry.get('title', 'Unknown Title')
                duration = entry.get('duration', 0)
                thumbnail = entry.get('thumbnail', '')
                
                # Skip if essential data is missing
                if not video_id or not duration:
                    filter_reasons['missing_data'] += 1
                    logger.debug(f"Skipping video with missing data: {title}")
                    continue
                
                # Filter criteria
                is_short = duration < 60  # Less than 1 minute
                is_live = entry.get('is_live', False)
                was_live = entry.get('was_live', False)
                
                # Apply filters
                if is_short:
                    filter_reasons['shorts'] += 1
                    logger.debug(f"Filtered out Short: {title} ({duration}s)")
                    continue
                
                if is_live or was_live:
                    filter_reasons['livestreams'] += 1
                    logger.debug(f"Filtered out livestream: {title}")
                    continue
                
                # Add to filtered list
                video_data = {
                    'id': video_id,
                    'title': title,
                    'duration': duration,
                    'thumbnail': thumbnail or f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }
                
                filtered_videos.append(video_data)
                
                # Report progress
                processed_count = idx
                if progress_callback:
                    progress_callback(total_count, processed_count, len(filtered_videos), title)
            
            # Log filter breakdown
            total_filtered = filter_reasons['shorts'] + filter_reasons['livestreams'] + filter_reasons['missing_data']
            logger.info(f"Filtered to {len(filtered_videos)} eligible videos")
            logger.info(f"Filter breakdown: {filter_reasons['shorts']} Shorts, {filter_reasons['livestreams']} Livestreams, {filter_reasons['missing_data']} Missing Data")
            logger.info(f"Total: {len(entries)} found, {len(filtered_videos)} eligible, {total_filtered} filtered out")
            
            return channel_name, filtered_videos
            
    except Exception as e:
        logger.error(f"Error scraping channel: {str(e)}")
        raise Exception(f"Failed to scrape channel: {str(e)}")


def get_video_info(video_url: str) -> Dict:
    """
    Get detailed information for a single video.
    
    Args:
        video_url: YouTube video URL
        
    Returns:
        Video metadata dictionary
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            return {
                'id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration'),
                'thumbnail': info.get('thumbnail'),
                'url': video_url,
                'uploader': info.get('uploader'),
                'upload_date': info.get('upload_date'),
            }
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        raise Exception(f"Failed to get video info: {str(e)}")

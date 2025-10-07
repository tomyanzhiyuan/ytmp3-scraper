"""
YouTube channel video scraper using yt-dlp
"""
import yt_dlp
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_channel_videos(channel_url: str) -> List[Dict]:
    """
    Scrape all videos from a YouTube channel and filter them.
    
    Args:
        channel_url: YouTube channel URL
        
    Returns:
        List of video metadata dictionaries
        
    Raises:
        Exception: If scraping fails
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Don't download, just extract metadata
        'ignoreerrors': True,  # Continue on errors
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Scraping channel: {channel_url}")
            
            # Extract channel info and videos
            result = ydl.extract_info(channel_url, download=False)
            
            if not result:
                raise Exception("Failed to extract channel information")
            
            # Get entries (videos)
            entries = result.get('entries', [])
            
            if not entries:
                logger.warning("No videos found in channel")
                return []
            
            logger.info(f"Found {len(entries)} total videos")
            
            # Filter videos
            filtered_videos = []
            
            for entry in entries:
                if not entry:
                    continue
                
                # Get video metadata
                video_id = entry.get('id')
                title = entry.get('title', 'Unknown Title')
                duration = entry.get('duration', 0)
                thumbnail = entry.get('thumbnail', '')
                
                # Skip if essential data is missing
                if not video_id or not duration:
                    logger.debug(f"Skipping video with missing data: {title}")
                    continue
                
                # Filter criteria
                is_short = duration < 60  # Less than 1 minute
                is_live = entry.get('is_live', False)
                was_live = entry.get('was_live', False)
                
                # Apply filters
                if is_short:
                    logger.debug(f"Filtered out Short: {title} ({duration}s)")
                    continue
                
                if is_live or was_live:
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
            
            logger.info(f"Filtered to {len(filtered_videos)} eligible videos")
            return filtered_videos
            
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

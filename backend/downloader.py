"""
Video downloader and MP3 converter using yt-dlp
"""
import yt_dlp
import os
import re
from typing import Dict, Callable, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory for MP3 files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Trim whitespace
    filename = filename.strip()
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def download_video_as_mp3(
    video_url: str,
    progress_callback: Optional[Callable[[Dict], None]] = None,
    channel_name: Optional[str] = None
) -> str:
    """
    Download a YouTube video and convert it to MP3.
    
    Args:
        video_url: YouTube video URL
        progress_callback: Optional callback function for progress updates
        channel_name: Optional channel name for organizing into subfolders
        
    Returns:
        Path to the downloaded MP3 file
        
    Raises:
        Exception: If download fails
    """
    # Determine output directory (with channel subfolder if provided)
    output_dir = OUTPUT_DIR
    if channel_name:
        # Sanitize channel name for filesystem
        safe_channel_name = sanitize_filename(channel_name)
        output_dir = os.path.join(OUTPUT_DIR, safe_channel_name)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    def progress_hook(d):
        """Hook for yt-dlp progress updates"""
        if progress_callback:
            progress_callback(d)
        
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            logger.info(f"Downloading: {percent} at {speed}")
        elif d['status'] == 'finished':
            logger.info("Download finished, converting to MP3...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Starting download: {video_url}")
            
            # Extract info first
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'Unknown')
            
            # Download and convert
            ydl.download([video_url])
            
            # Construct expected output filename
            sanitized_title = sanitize_filename(title)
            output_file = os.path.join(output_dir, f"{sanitized_title}.mp3")
            
            # Check if file exists
            if os.path.exists(output_file):
                logger.info(f"Successfully downloaded: {output_file}")
                return output_file
            else:
                # Try to find the file with similar name
                for file in os.listdir(output_dir):
                    if file.endswith('.mp3') and sanitized_title.lower() in file.lower():
                        output_file = os.path.join(output_dir, file)
                        logger.info(f"Found downloaded file: {output_file}")
                        return output_file
                
                raise Exception(f"Downloaded file not found: {output_file}")
                
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise Exception(f"Failed to download video: {str(e)}")


def download_multiple_videos(
    video_urls: list,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, str]:
    """
    Download multiple videos as MP3.
    
    Args:
        video_urls: List of YouTube video URLs
        progress_callback: Optional callback(current, total, title)
        
    Returns:
        Dictionary mapping video URLs to output file paths
    """
    results = {}
    total = len(video_urls)
    
    for idx, url in enumerate(video_urls, 1):
        try:
            logger.info(f"Processing video {idx}/{total}")
            
            if progress_callback:
                progress_callback(idx, total, url)
            
            output_file = download_video_as_mp3(url)
            results[url] = output_file
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            results[url] = f"ERROR: {str(e)}"
    
    return results


def list_downloaded_files() -> list:
    """
    List all MP3 files in the output directory.
    
    Returns:
        List of MP3 filenames
    """
    if not os.path.exists(OUTPUT_DIR):
        return []
    
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.mp3')]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
    
    return files


def get_output_directory() -> str:
    """
    Get the output directory path.
    
    Returns:
        Absolute path to output directory
    """
    return os.path.abspath(OUTPUT_DIR)

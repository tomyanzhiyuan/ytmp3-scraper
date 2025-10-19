"""
Video downloader and MP3 converter using yt-dlp
"""
import yt_dlp
import os
import re
import time
from typing import Dict, Callable, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory for MP3 files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')

# Path to cookies file (for YouTube authentication)
COOKIES_FILE = os.path.join(os.path.dirname(__file__), 'cookies.txt')


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
    channel_name: Optional[str] = None,
    skip_existing: bool = True
) -> str:
    """
    Download a YouTube video and convert it to MP3.
    
    Args:
        video_url: YouTube video URL
        progress_callback: Optional callback function for progress updates
        channel_name: Optional channel name for organizing into subfolders
        skip_existing: If True, skip download if file already exists (default: True)
        
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
    
    # Check if file already exists (skip download if requested)
    if skip_existing:
        try:
            # Extract video info to get title without downloading
            ydl_opts_info = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            # Add cookies if available
            if os.path.exists(COOKIES_FILE):
                ydl_opts_info['cookiefile'] = COOKIES_FILE
            
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'Unknown')
                sanitized_title = sanitize_filename(title)
                expected_file = os.path.join(output_dir, f"{sanitized_title}.mp3")
                
                # Check if file exists
                if os.path.exists(expected_file):
                    logger.info(f"File already exists, skipping download: {sanitized_title}.mp3")
                    return expected_file
                
                # Also check for similar filenames (in case of slight variations)
                for existing_file in os.listdir(output_dir):
                    if existing_file.endswith('.mp3') and sanitized_title.lower() in existing_file.lower():
                        logger.info(f"Similar file found, skipping download: {existing_file}")
                        return os.path.join(output_dir, existing_file)
        
        except Exception as e:
            logger.debug(f"Could not check for existing file: {e}. Proceeding with download.")
    
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
    
    # Add cookies if file exists (for YouTube authentication)
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
        logger.info("Using cookies for authentication")
    else:
        logger.warning(f"Cookies file not found at {COOKIES_FILE}. Downloads may fail due to bot detection.")
    
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
            
            # Try to find the file with similar name (fuzzy matching)
            # This handles cases where yt-dlp uses different sanitization than our function
            if os.path.exists(output_dir):
                mp3_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
                
                # Sort by modification time (newest first)
                mp3_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
                
                # Check for fuzzy match with the title
                for file in mp3_files:
                    # Remove .mp3 extension and compare
                    file_base = file[:-4]
                    
                    # Try multiple matching strategies
                    # 1. Check if sanitized title is in filename
                    if sanitized_title.lower() in file_base.lower():
                        output_file = os.path.join(output_dir, file)
                        logger.info(f"Found downloaded file (fuzzy match): {output_file}")
                        return output_file
                    
                    # 2. Check if most words from title are in filename
                    title_words = set(sanitized_title.lower().split())
                    file_words = set(file_base.lower().split())
                    if len(title_words) > 0:
                        match_ratio = len(title_words & file_words) / len(title_words)
                        if match_ratio > 0.7:  # 70% word match
                            output_file = os.path.join(output_dir, file)
                            logger.info(f"Found downloaded file (word match {match_ratio:.0%}): {output_file}")
                            return output_file
            
            raise Exception(f"Downloaded file not found. Expected: {output_file}")
                
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        raise Exception(f"Failed to download video: {str(e)}")


def download_multiple_videos(
    video_urls: list,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    delay_between_downloads: float = 2.0
) -> Dict[str, str]:
    """
    Download multiple videos as MP3.
    
    Args:
        video_urls: List of YouTube video URLs
        progress_callback: Optional callback(current, total, title)
        delay_between_downloads: Delay in seconds between downloads (default: 2.0)
        
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
            
            # Add delay between downloads to avoid rate limiting (except for last video)
            if idx < total:
                logger.info(f"Waiting {delay_between_downloads}s before next download...")
                time.sleep(delay_between_downloads)
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            results[url] = f"ERROR: {str(e)}"
            
            # Still add delay after failed downloads to avoid rate limiting
            if idx < total:
                time.sleep(delay_between_downloads)
    
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

"""
Video downloader and converter using yt-dlp
Supports MP3 (audio) and MP4 (video) formats
"""

import logging
import os
import re
import time
from collections.abc import Callable

import yt_dlp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory for downloaded files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

# Path to cookies file (for YouTube authentication)
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")


def is_rate_limited(error_msg: str) -> tuple[bool, int]:
    """
    Detect if error is due to rate limiting and extract suggested timeout.

    Args:
        error_msg: Error message from yt-dlp

    Returns:
        Tuple of (is_rate_limited, suggested_wait_seconds)
    """
    error_lower = error_msg.lower()

    # Check for rate limiting indicators
    rate_limit_indicators = [
        "rate-limited",
        "rate limited",
        "try again later",
        "content isn't available",
        "too many requests",
        "exceeded the rate limit",
    ]

    is_limited = any(indicator in error_lower for indicator in rate_limit_indicators)

    if not is_limited:
        return False, 0

    # Parse timeout duration from error message
    if "hour" in error_lower:
        # Extract number of hours if present
        import re

        hour_match = re.search(r"(\d+)\s*hour", error_lower)
        if hour_match:
            hours = int(hour_match.group(1))
            return True, hours * 3600
        return True, 3600  # Default 1 hour

    if "minute" in error_lower:
        # Extract number of minutes if present
        minute_match = re.search(r"(\d+)\s*minute", error_lower)
        if minute_match:
            minutes = int(minute_match.group(1))
            return True, minutes * 60
        return True, 300  # Default 5 minutes

    # Default wait time for rate limiting
    return True, 300  # 5 minutes default


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Replace multiple spaces with single space
    filename = re.sub(r"\s+", " ", filename)
    # Trim whitespace
    filename = filename.strip()
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def check_file_exists(title: str, channel_name: str | None = None) -> tuple[bool, str | None]:
    """
    Check if a video file already exists without making any API calls.

    Args:
        title: Video title
        channel_name: Optional channel name for subfolder

    Returns:
        Tuple of (exists, filepath) - filepath is None if not found
    """
    # Determine output directory
    output_dir = OUTPUT_DIR
    if channel_name:
        safe_channel_name = sanitize_filename(channel_name)
        output_dir = os.path.join(OUTPUT_DIR, safe_channel_name)

    if not os.path.exists(output_dir):
        return False, None

    # Sanitize title for comparison
    sanitized_title = sanitize_filename(title)
    expected_file = os.path.join(output_dir, f"{sanitized_title}.mp3")

    # Check exact match
    if os.path.exists(expected_file):
        return True, expected_file

    # Check for fuzzy match (handles special characters)
    try:
        for existing_file in os.listdir(output_dir):
            if not existing_file.endswith(".mp3"):
                continue

            file_base = existing_file[:-4]

            # Check if sanitized title is in filename
            if sanitized_title.lower() in file_base.lower():
                return True, os.path.join(output_dir, existing_file)

            # Check word-based match
            title_words = set(sanitized_title.lower().split())
            file_words = set(file_base.lower().split())
            if len(title_words) > 0:
                match_ratio = len(title_words & file_words) / len(title_words)
                if match_ratio > 0.7:  # 70% word match
                    return True, os.path.join(output_dir, existing_file)
    except Exception as e:
        logger.debug(f"Error checking for existing file: {e}")

    return False, None


def download_video(
    video_url: str,
    format: str = "mp3",
    progress_callback: Callable[[dict], None] | None = None,
    channel_name: str | None = None,
    skip_existing: bool = True,
) -> str:
    """
    Download a YouTube video in the specified format.

    Args:
        video_url: YouTube video URL
        format: Output format - "mp3" for audio, "mp4" for video (default: "mp3")
        progress_callback: Optional callback function for progress updates
        channel_name: Optional channel name for organizing into subfolders
        skip_existing: If True, skip download if file already exists (default: True)

    Returns:
        Path to the downloaded file

    Raises:
        Exception: If download fails
    """
    # Validate format
    format = format.lower()
    if format not in ("mp3", "mp4"):
        raise ValueError(f"Unsupported format: {format}. Use 'mp3' or 'mp4'.")

    file_extension = format

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
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
            }

            # Add cookies if available
            if os.path.exists(COOKIES_FILE):
                ydl_opts_info["cookiefile"] = COOKIES_FILE

            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get("title", "Unknown")
                sanitized_title = sanitize_filename(title)
                expected_file = os.path.join(output_dir, f"{sanitized_title}.{file_extension}")

                # Check if file exists
                if os.path.exists(expected_file):
                    logger.info(f"File already exists, skipping download: {sanitized_title}.{file_extension}")
                    return expected_file

                # Also check for similar filenames (in case of slight variations)
                for existing_file in os.listdir(output_dir):
                    if (
                        existing_file.endswith(f".{file_extension}")
                        and sanitized_title.lower() in existing_file.lower()
                    ):
                        logger.info(f"Similar file found, skipping download: {existing_file}")
                        return os.path.join(output_dir, existing_file)

        except Exception as e:
            logger.debug(f"Could not check for existing file: {e}. Proceeding with download.")

    def progress_hook(d):
        """Hook for yt-dlp progress updates"""
        if progress_callback:
            progress_callback(d)

        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%")
            speed = d.get("_speed_str", "N/A")
            logger.info(f"Downloading: {percent} at {speed}")
        elif d["status"] == "finished":
            if format == "mp3":
                logger.info("Download finished, converting to MP3...")
            else:
                logger.info("Download finished!")

    # Configure yt-dlp options based on format
    if format == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": False,
            "no_warnings": False,
        }
    else:  # mp4
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": False,
            "no_warnings": False,
        }

    # Add cookies if file exists (for YouTube authentication)
    if os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE
        logger.info("Using cookies for authentication")
    else:
        logger.warning(f"Cookies file not found at {COOKIES_FILE}. Downloads may fail due to bot detection.")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Starting download ({format.upper()}): {video_url}")

            # Extract info first
            info = ydl.extract_info(video_url, download=False)
            title = info.get("title", "Unknown")

            # Download and convert
            ydl.download([video_url])

            # Construct expected output filename
            sanitized_title = sanitize_filename(title)
            output_file = os.path.join(output_dir, f"{sanitized_title}.{file_extension}")

            # Check if file exists
            if os.path.exists(output_file):
                logger.info(f"Successfully downloaded: {output_file}")
                return output_file

            # Try to find the file with similar name (fuzzy matching)
            # This handles cases where yt-dlp uses different sanitization than our function
            if os.path.exists(output_dir):
                matching_files = [f for f in os.listdir(output_dir) if f.endswith(f".{file_extension}")]

                # Sort by modification time (newest first)
                matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)

                # Check for fuzzy match with the title
                for file in matching_files:
                    # Remove extension and compare
                    file_base = file[: -(len(file_extension) + 1)]

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
        raise Exception(f"Failed to download video: {str(e)}") from e


# Alias for backward compatibility
def download_video_as_mp3(
    video_url: str,
    progress_callback: Callable[[dict], None] | None = None,
    channel_name: str | None = None,
    skip_existing: bool = True,
) -> str:
    """Backward compatible alias for download_video with mp3 format."""
    return download_video(video_url, "mp3", progress_callback, channel_name, skip_existing)


def download_multiple_videos(
    video_urls: list,
    progress_callback: Callable[[int, int, str], None] | None = None,
    delay_between_downloads: float = 2.0,
) -> dict[str, str]:
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
    List all downloaded files (MP3 and MP4) in the output directory.

    Returns:
        List of filenames
    """
    if not os.path.exists(OUTPUT_DIR):
        return []

    # Include both MP3 and MP4 files
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith((".mp3", ".mp4"))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)

    return files


def get_output_directory() -> str:
    """
    Get the output directory path.

    Returns:
        Absolute path to output directory
    """
    return os.path.abspath(OUTPUT_DIR)

"""
YouTube Data API v3 scraper for getting channel videos
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_time_cutoff(time_frame: str) -> Optional[datetime]:
    """Get the cutoff datetime for a time frame filter"""
    now = datetime.utcnow()
    if time_frame == "week":
        return now - timedelta(days=7)
    elif time_frame == "month":
        return now - timedelta(days=30)
    elif time_frame == "year":
        return now - timedelta(days=365)
    return None  # "all" - no cutoff


class YouTubeAPIScraper:
    """Scraper using YouTube Data API v3"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube API client
        
        Args:
            api_key: YouTube Data API key (or set YOUTUBE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key not provided. Set YOUTUBE_API_KEY environment variable or pass api_key parameter.")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def get_channel_id(self, channel_url: str) -> str:
        """
        Extract channel ID from various YouTube URL formats
        
        Args:
            channel_url: YouTube channel URL 
            
        Returns:
            Channel ID
        """
        # Handle /channel/ID format (direct channel ID)
        if '/channel/' in channel_url:
            return channel_url.split('/channel/')[-1].split('/')[0].split('?')[0]
        
        # Handle @username format - use forHandle for exact lookup
        if '@' in channel_url:
            handle = channel_url.split('@')[-1].split('/')[0].split('?')[0]
            try:
                # Use forHandle for exact handle lookup (not search!)
                request = self.youtube.channels().list(
                    part='snippet',
                    forHandle=handle
                )
                response = request.execute()
                if response.get('items'):
                    channel_id = response['items'][0]['id']
                    channel_name = response['items'][0]['snippet']['title']
                    logger.info(f"Resolved @{handle} -> {channel_name} (ID: {channel_id})")
                    return channel_id
                else:
                    raise ValueError(f"Channel with handle @{handle} not found")
            except HttpError as e:
                logger.error(f"Error finding channel by handle @{handle}: {e}")
                raise
        
        # Handle /c/ custom URL format
        if '/c/' in channel_url:
            custom_name = channel_url.split('/c/')[-1].split('/')[0].split('?')[0]
            try:
                # Try to find by custom URL - unfortunately API doesn't have direct lookup
                # So we search but verify the customUrl matches exactly
                request = self.youtube.search().list(
                    part='snippet',
                    q=custom_name,
                    type='channel',
                    maxResults=5
                )
                response = request.execute()
                
                # Verify we found an exact match
                for item in response.get('items', []):
                    channel_id = item['snippet']['channelId']
                    # Fetch full channel info to check customUrl
                    channel_request = self.youtube.channels().list(
                        part='snippet',
                        id=channel_id
                    )
                    channel_response = channel_request.execute()
                    if channel_response.get('items'):
                        channel_info = channel_response['items'][0]['snippet']
                        custom_url = channel_info.get('customUrl', '').lower()
                        if custom_url == f'@{custom_name.lower()}' or custom_name.lower() in custom_url:
                            logger.info(f"Resolved /c/{custom_name} -> {channel_info['title']} (ID: {channel_id})")
                            return channel_id
                
                raise ValueError(f"Channel with custom URL /c/{custom_name} not found")
            except HttpError as e:
                logger.error(f"Error finding channel by custom URL /c/{custom_name}: {e}")
                raise
        
        # Handle /user/ format - use forUsername for exact lookup
        if '/user/' in channel_url:
            username = channel_url.split('/user/')[-1].split('/')[0].split('?')[0]
            try:
                request = self.youtube.channels().list(
                    part='snippet',
                    forUsername=username
                )
                response = request.execute()
                if response.get('items'):
                    channel_id = response['items'][0]['id']
                    channel_name = response['items'][0]['snippet']['title']
                    logger.info(f"Resolved /user/{username} -> {channel_name} (ID: {channel_id})")
                    return channel_id
                else:
                    raise ValueError(f"Channel with username {username} not found")
            except HttpError as e:
                logger.error(f"Error finding channel by username {username}: {e}")
                raise
        
        raise ValueError(f"Could not extract channel ID from URL: {channel_url}. Supported formats: @handle, /channel/ID, /c/customUrl, /user/username")
    
    def scrape_channel_videos(
        self, 
        channel_url: str, 
        progress_callback=None,
        video_type: str = "videos",
        time_frame: str = "all"
    ) -> tuple[str, List[Dict]]:
        """
        Scrape all videos from a YouTube channel
        
        Args:
            channel_url: YouTube channel URL
            progress_callback: Optional callback function(total, processed, filtered, current_title)
            video_type: "all", "shorts", or "videos"
            time_frame: "all", "week", "month", or "year"
            
        Returns:
            Tuple of (channel_name, list of video metadata dictionaries)
        """
        try:
            # Get channel ID
            channel_id = self.get_channel_id(channel_url)
            logger.info(f"Found channel ID: {channel_id}")
            
            # Get channel info including contentDetails for uploads playlist
            channel_request = self.youtube.channels().list(
                part='snippet,contentDetails',
                id=channel_id
            )
            channel_response = channel_request.execute()
            channel_name = channel_response['items'][0]['snippet']['title']
            
            logger.info(f"Scraping channel: {channel_name}")
            logger.info(f"Filters: video_type={video_type}, time_frame={time_frame}")
            
            # Get the channel's uploads playlist ID
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            logger.info(f"Uploads playlist ID: {uploads_playlist_id}")
            
            # Get time cutoff
            time_cutoff = get_time_cutoff(time_frame)
            if time_cutoff:
                logger.info(f"Time cutoff: {time_cutoff.isoformat()}")
            
            # Get all videos from the uploads playlist
            all_video_ids = []
            next_page_token = None
            stop_fetching = False
            
            while not stop_fetching:
                # Get videos from uploads playlist (50 per page, max allowed by API)
                request = self.youtube.playlistItems().list(
                    part='contentDetails,snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Collect video IDs, checking publish date if time filter is set
                for item in response['items']:
                    publish_date_str = item['snippet'].get('publishedAt', '')
                    if publish_date_str and time_cutoff:
                        publish_date = datetime.fromisoformat(publish_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
                        if publish_date < time_cutoff:
                            stop_fetching = True
                            break
                    all_video_ids.append(item['contentDetails']['videoId'])
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                if progress_callback:
                    progress_callback(len(all_video_ids), 0, 0, f"Found {len(all_video_ids)} videos...")
                logger.info(f"Fetched {len(all_video_ids)} videos so far...")
            
            logger.info(f"Found {len(all_video_ids)} videos from {channel_name} (within time frame)")
            
            # Get detailed info for all videos (in batches of 50)
            filtered_videos = []
            shorts_videos = []
            long_videos = []
            filter_reasons = {
                'shorts': 0,
                'long_videos': 0,
                'livestreams': 0,
                'time_filtered': 0
            }
            
            total_to_process = len(all_video_ids)
            processed_count = 0
            
            for i in range(0, len(all_video_ids), 50):
                batch = all_video_ids[i:i+50]
                
                # Get video details
                video_request = self.youtube.videos().list(
                    part='snippet,contentDetails,liveStreamingDetails,player',
                    id=','.join(batch)
                )
                video_response = video_request.execute()
                
                for video in video_response['items']:
                    processed_count += 1
                    video_id = video['id']
                    title = video['snippet']['title']
                    
                    # Parse duration (ISO 8601 format: PT1H2M3S)
                    duration_str = video['contentDetails']['duration']
                    duration = self._parse_duration(duration_str)
                    
                    # Check if livestream - always filter these out
                    is_live = 'liveStreamingDetails' in video
                    if is_live:
                        filter_reasons['livestreams'] += 1
                        # Report progress
                        if progress_callback:
                            progress_callback(total_to_process, processed_count, len(filtered_videos), title)
                        continue
                    
                    # Get thumbnail
                    thumbnails = video['snippet']['thumbnails']
                    thumbnail = thumbnails.get('maxres', thumbnails.get('high', thumbnails.get('default', {})))
                    thumbnail_url = thumbnail.get('url', '')
                    
                    # Detect if Short
                    is_short = self._detect_short(video_id, title, duration, thumbnail)
                    
                    # Create video data
                    video_data = {
                        'id': video_id,
                        'title': title,
                        'duration': duration,
                        'thumbnail': thumbnail_url,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'is_short': is_short
                    }
                    
                    # Filter based on video_type
                    if video_type == "all":
                        filtered_videos.append(video_data)
                    elif video_type == "shorts" and is_short:
                        filtered_videos.append(video_data)
                    elif video_type == "videos" and not is_short:
                        filtered_videos.append(video_data)
                    else:
                        if is_short:
                            filter_reasons['shorts'] += 1
                        else:
                            filter_reasons['long_videos'] += 1
                    
                    # Report progress AFTER filtering decision
                    if progress_callback:
                        progress_callback(total_to_process, processed_count, len(filtered_videos), title)
            
            # Log filter breakdown
            logger.info(f"Filtered to {len(filtered_videos)} videos")
            logger.info(f"Filter breakdown: {filter_reasons['shorts']} Shorts filtered, {filter_reasons['livestreams']} Livestreams filtered")
            
            return channel_name, filtered_videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise Exception(f"YouTube API error: {e}")
        except Exception as e:
            logger.error(f"Error scraping channel: {str(e)}")
            raise Exception(f"Failed to scrape channel: {str(e)}")
    
    def _detect_short(self, video_id: str, title: str, duration: int, thumbnail: dict) -> bool:
        """
        Detect if a video is a Short using yt-dlp (most reliable method).
        
        YouTube Shorts can be up to 3 minutes. The only reliable way to detect them
        is to check if YouTube serves them on the /shorts/ URL path.
        """
        # Quick heuristic: Videos over 3 minutes (180s) cannot be Shorts
        if duration > 180:
            return False
        
        # For videos under 3 minutes, use yt-dlp to definitively check
        # This is the only reliable method as YouTube's API doesn't expose Short status
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': False,
            }
            
            # Try the /shorts/ URL - this is the definitive check
            # If YouTube serves the video at /shorts/{id}, it's a Short
            shorts_url = f"https://www.youtube.com/shorts/{video_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(shorts_url, download=False)
                    # If we successfully extracted from /shorts/ URL, it's a Short
                    if info:
                        logger.debug(f"Video {video_id} confirmed as Short via /shorts/ URL")
                        return True
                except Exception:
                    # /shorts/ URL failed - not a Short
                    logger.debug(f"Video {video_id} is NOT a Short (/shorts/ URL failed)")
                    return False
            
            return False
            
        except Exception as e:
            logger.debug(f"yt-dlp Short detection failed for {video_id}: {e}")
            # On error, fall back to heuristics
            return self._detect_short_heuristic(title, duration, thumbnail)
    
    def _detect_short_heuristic(self, title: str, duration: int, thumbnail: dict) -> bool:
        """
        Fallback heuristic detection when yt-dlp fails.
        Less reliable but better than nothing.
        """
        # Check title patterns
        title_lower = title.lower()
        short_indicators = ['#shorts', '#short']
        if any(indicator in title_lower for indicator in short_indicators):
            return True
        
        # Check thumbnail aspect ratio (Shorts have vertical thumbnails)
        if thumbnail:
            thumb_width = thumbnail.get('width', 0)
            thumb_height = thumbnail.get('height', 0)
            if thumb_height > 0 and thumb_width > 0:
                aspect_ratio = thumb_width / thumb_height
                # Very vertical (9:16 ≈ 0.56) suggests Short
                if aspect_ratio < 0.7:
                    return True
        
        return False
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration to seconds
        
        Args:
            duration_str: ISO 8601 duration (e.g., PT1H2M3S)
            
        Returns:
            Duration in seconds
        """
        import re
        
        # Remove PT prefix
        duration_str = duration_str.replace('PT', '')
        
        # Extract hours, minutes, seconds
        hours = 0
        minutes = 0
        seconds = 0
        
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds

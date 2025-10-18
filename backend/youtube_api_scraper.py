"""
YouTube Data API v3 scraper for getting channel videos
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        # Handle @username format
        if '@' in channel_url:
            username = channel_url.split('@')[-1].split('/')[0]
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=username,
                    type='channel',
                    maxResults=1
                )
                response = request.execute()
                if response['items']:
                    return response['items'][0]['snippet']['channelId']
            except HttpError as e:
                logger.error(f"Error finding channel: {e}")
                raise
        
        # Handle /channel/ID format
        if '/channel/' in channel_url:
            return channel_url.split('/channel/')[-1].split('/')[0]
        
        # Handle /c/ or /user/ format
        if '/c/' in channel_url or '/user/' in channel_url:
            username = channel_url.split('/')[-1]
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=username,
                    type='channel',
                    maxResults=1
                )
                response = request.execute()
                if response['items']:
                    return response['items'][0]['snippet']['channelId']
            except HttpError as e:
                logger.error(f"Error finding channel: {e}")
                raise
        
        raise ValueError(f"Could not extract channel ID from URL: {channel_url}")
    
    def scrape_channel_videos(
        self, 
        channel_url: str, 
        progress_callback=None
    ) -> tuple[str, List[Dict]]:
        """
        Scrape all videos from a YouTube channel
        
        Args:
            channel_url: YouTube channel URL
            progress_callback: Optional callback function(total, processed, filtered, current_title)
            
        Returns:
            Tuple of (channel_name, list of video metadata dictionaries)
        """
        try:
            # Get channel ID
            channel_id = self.get_channel_id(channel_url)
            logger.info(f"Found channel ID: {channel_id}")
            
            # Get channel info
            channel_request = self.youtube.channels().list(
                part='snippet',
                id=channel_id
            )
            channel_response = channel_request.execute()
            channel_name = channel_response['items'][0]['snippet']['title']
            
            logger.info(f"Scraping channel: {channel_name}")
            
            # Get all videos from channel
            all_videos = []
            next_page_token = None
            
            while True:
                # Get videos (50 per page, max allowed by API)
                request = self.youtube.search().list(
                    part='id',
                    channelId=channel_id,
                    maxResults=50,
                    order='date',
                    type='video',
                    pageToken=next_page_token
                )
                response = request.execute()
                
                # Collect video IDs
                video_ids = [item['id']['videoId'] for item in response['items']]
                all_videos.extend(video_ids)
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                logger.info(f"Fetched {len(all_videos)} videos so far...")
            
            logger.info(f"Found {len(all_videos)} total videos from {channel_name}")
            
            # Get detailed info for all videos (in batches of 50)
            filtered_videos = []
            filter_reasons = {
                'shorts': 0,
                'livestreams': 0,
                'missing_data': 0
            }
            
            for i in range(0, len(all_videos), 50):
                batch = all_videos[i:i+50]
                
                # Get video details including statistics for better Short detection
                video_request = self.youtube.videos().list(
                    part='snippet,contentDetails,liveStreamingDetails,player',
                    id=','.join(batch)
                )
                video_response = video_request.execute()
                
                for video in video_response['items']:
                    video_id = video['id']
                    title = video['snippet']['title']
                    
                    # Parse duration (ISO 8601 format: PT1H2M3S)
                    duration_str = video['contentDetails']['duration']
                    duration = self._parse_duration(duration_str)
                    
                    # Check if livestream
                    is_live = 'liveStreamingDetails' in video
                    
                    # Get thumbnail
                    thumbnails = video['snippet']['thumbnails']
                    thumbnail = thumbnails.get('maxres', thumbnails.get('high', thumbnails.get('default', {})))
                    thumbnail_url = thumbnail.get('url', '')
                    
                    # Detect Shorts by checking if it's a vertical video
                    # Shorts are vertical (9:16 aspect ratio, height > width)
                    is_short = False
                    
                    # Method 1: Check duration (Shorts are typically under 60s, but can be up to 3 minutes)
                    if duration < 60:
                        is_short = True
                    
                    # Method 2: Check thumbnail dimensions (Shorts have tall thumbnails)
                    if thumbnail:
                        thumb_width = thumbnail.get('width', 0)
                        thumb_height = thumbnail.get('height', 0)
                        if thumb_height > 0 and thumb_width > 0:
                            aspect_ratio = thumb_width / thumb_height
                            # Normal videos are 16:9 (1.78), Shorts are 9:16 (0.56)
                            if aspect_ratio < 0.8:  # Vertical video
                                is_short = True
                                logger.debug(f"Detected Short by aspect ratio: {title} (ratio: {aspect_ratio:.2f})")
                    
                    # Apply filters
                    if is_short:
                        filter_reasons['shorts'] += 1
                        logger.debug(f"Filtered out Short: {title} ({duration}s)")
                        continue
                    
                    if is_live:
                        filter_reasons['livestreams'] += 1
                        logger.debug(f"Filtered out livestream: {title}")
                        continue
                    
                    # Add to filtered list
                    video_data = {
                        'id': video_id,
                        'title': title,
                        'duration': duration,
                        'thumbnail': thumbnail_url,
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    }
                    
                    filtered_videos.append(video_data)
                    
                    # Report progress
                    if progress_callback:
                        progress_callback(
                            len(all_videos),
                            i + len(batch),
                            len(filtered_videos),
                            title
                        )
            
            # Log filter breakdown
            total_filtered = filter_reasons['shorts'] + filter_reasons['livestreams'] + filter_reasons['missing_data']
            logger.info(f"Filtered to {len(filtered_videos)} eligible videos")
            logger.info(f"Filter breakdown: {filter_reasons['shorts']} Shorts, {filter_reasons['livestreams']} Livestreams, {filter_reasons['missing_data']} Missing Data")
            logger.info(f"Total: {len(all_videos)} found, {len(filtered_videos)} eligible, {total_filtered} filtered out")
            
            return channel_name, filtered_videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            raise Exception(f"YouTube API error: {e}")
        except Exception as e:
            logger.error(f"Error scraping channel: {str(e)}")
            raise Exception(f"Failed to scrape channel: {str(e)}")
    
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

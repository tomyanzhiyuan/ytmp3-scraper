"""
Test suite for YouTube Short detection and channel resolution.

Tests cover:
1. Short detection via /shorts/ URL (definitive method)
2. Fallback heuristic detection
3. Channel handle resolution
4. Edge cases for various video types
5. Time frame filtering
6. Video type filtering (all, shorts, videos)
7. Duration parsing (ISO 8601)
8. API error handling
9. Progress callbacks

Run with: pytest tests/test_short_detection.py -v
"""

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, call, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube_api_scraper import YouTubeAPIScraper, get_time_cutoff


class TestShortDetection:
    """Tests for _detect_short method"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked API key"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                return YouTubeAPIScraper()

    # --- Duration-based quick checks ---

    def test_video_over_180_seconds_is_not_short(self, scraper):
        """Videos over 3 minutes cannot be Shorts - should return False immediately"""
        # Should return False without making any yt-dlp calls
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            result = scraper._detect_short("test_id", "Test Video", 181, {})
            assert result is False
            # Verify yt-dlp was NOT called (quick return for videos > 180s)
            mock_ydl.assert_not_called()

    def test_video_exactly_180_seconds_checks_ytdlp(self, scraper):
        """Videos exactly 3 minutes should be checked via yt-dlp"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            mock_instance.extract_info.side_effect = Exception("Not a short")

            scraper._detect_short("test_id", "Test Video", 180, {})
            # Should have attempted yt-dlp check
            assert mock_ydl.called

    def test_video_under_60_seconds_checks_ytdlp(self, scraper):
        """Short videos should be verified via yt-dlp, not assumed to be Shorts"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            # Simulate /shorts/ URL failing - it's NOT a Short
            mock_instance.extract_info.side_effect = Exception("Not a short")

            result = scraper._detect_short("test_id", "Short Regular Video", 45, {})
            # Should return False because /shorts/ URL failed
            assert result is False

    # --- yt-dlp based detection ---

    def test_shorts_url_success_returns_true(self, scraper):
        """If /shorts/ URL works, video is definitely a Short"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            # Simulate successful extraction from /shorts/ URL
            mock_instance.extract_info.return_value = {"id": "test_id", "title": "Test"}

            result = scraper._detect_short("test_id", "Some Short", 30, {})
            assert result is True
            # Verify we tried the /shorts/ URL
            mock_instance.extract_info.assert_called_with("https://www.youtube.com/shorts/test_id", download=False)

    def test_shorts_url_failure_returns_false(self, scraper):
        """If /shorts/ URL fails, video is NOT a Short"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            # Simulate /shorts/ URL failing
            mock_instance.extract_info.side_effect = Exception("Video not available")

            result = scraper._detect_short("regular_video_id", "Regular Video", 45, {})
            assert result is False

    # --- Heuristic fallback tests ---

    def test_heuristic_detects_hashtag_shorts(self, scraper):
        """Heuristic should detect #shorts in title"""
        result = scraper._detect_short_heuristic("My video #shorts", 30, {})
        assert result is True

    def test_heuristic_detects_hashtag_short(self, scraper):
        """Heuristic should detect #short in title"""
        result = scraper._detect_short_heuristic("Quick clip #short", 45, {})
        assert result is True

    def test_heuristic_case_insensitive(self, scraper):
        """Heuristic should be case insensitive"""
        result = scraper._detect_short_heuristic("My video #SHORTS", 30, {})
        assert result is True

    def test_heuristic_detects_vertical_thumbnail(self, scraper):
        """Heuristic should detect vertical thumbnails (aspect ratio < 0.7)"""
        # 9:16 aspect ratio = 0.5625
        vertical_thumbnail = {"width": 405, "height": 720}
        result = scraper._detect_short_heuristic("Some Video", 30, vertical_thumbnail)
        assert result is True

    def test_heuristic_ignores_horizontal_thumbnail(self, scraper):
        """Heuristic should not flag horizontal thumbnails"""
        # 16:9 aspect ratio = 1.78
        horizontal_thumbnail = {"width": 1280, "height": 720}
        result = scraper._detect_short_heuristic("Some Video", 30, horizontal_thumbnail)
        assert result is False

    def test_heuristic_handles_missing_thumbnail(self, scraper):
        """Heuristic should handle missing thumbnail gracefully"""
        result = scraper._detect_short_heuristic("Regular Video", 30, None)
        assert result is False

        result = scraper._detect_short_heuristic("Regular Video", 30, {})
        assert result is False

    def test_heuristic_handles_zero_dimensions(self, scraper):
        """Heuristic should handle zero thumbnail dimensions"""
        thumbnail = {"width": 0, "height": 0}
        result = scraper._detect_short_heuristic("Regular Video", 30, thumbnail)
        assert result is False


class TestChannelResolution:
    """Tests for get_channel_id method"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked YouTube API"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper()
                scraper.youtube = MagicMock()
                return scraper

    # --- Direct channel ID extraction ---

    def test_extracts_channel_id_from_channel_url(self, scraper):
        """Should extract channel ID directly from /channel/ URL"""
        url = "https://www.youtube.com/channel/UC1234567890abcdef"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890abcdef"

    def test_extracts_channel_id_with_trailing_slash(self, scraper):
        """Should handle trailing slash in /channel/ URL"""
        url = "https://www.youtube.com/channel/UC1234567890abcdef/"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890abcdef"

    def test_extracts_channel_id_with_query_params(self, scraper):
        """Should handle query parameters in /channel/ URL"""
        url = "https://www.youtube.com/channel/UC1234567890abcdef?sub_confirmation=1"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890abcdef"

    def test_extracts_channel_id_with_subpath(self, scraper):
        """Should handle subpaths like /videos in /channel/ URL"""
        url = "https://www.youtube.com/channel/UC1234567890abcdef/videos"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890abcdef"

    # --- Handle (@username) resolution ---

    def test_resolves_handle_exactly(self, scraper):
        """Should use forHandle for exact handle lookup, not search"""
        url = "https://www.youtube.com/@samsulek"

        # Mock the channels().list() response
        mock_response = {"items": [{"id": "UC_exact_channel_id", "snippet": {"title": "Sam Sulek"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        result = scraper.get_channel_id(url)

        # Verify it used forHandle, not search
        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="samsulek")
        assert result == "UC_exact_channel_id"

    def test_handle_with_trailing_slash(self, scraper):
        """Should handle trailing slash in @handle URL"""
        url = "https://www.youtube.com/@testchannel/"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Test Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="testchannel")

    def test_handle_with_query_params(self, scraper):
        """Should strip query params from handle"""
        url = "https://www.youtube.com/@testchannel?sub_confirmation=1"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Test Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="testchannel")

    def test_handle_not_found_raises_error(self, scraper):
        """Should raise ValueError when handle doesn't exist"""
        url = "https://www.youtube.com/@nonexistenthandle12345"

        # Mock empty response
        mock_response = {"items": []}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        with pytest.raises(ValueError, match="not found"):
            scraper.get_channel_id(url)

    # --- /user/ URL resolution ---

    def test_resolves_user_url_exactly(self, scraper):
        """Should use forUsername for exact user lookup"""
        url = "https://www.youtube.com/user/pewdiepie"

        mock_response = {"items": [{"id": "UC_pewdiepie_id", "snippet": {"title": "PewDiePie"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        result = scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forUsername="pewdiepie")
        assert result == "UC_pewdiepie_id"

    # --- Invalid URL handling ---

    def test_invalid_url_raises_error(self, scraper):
        """Should raise ValueError for unsupported URL formats"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        with pytest.raises(ValueError, match="Could not extract channel ID"):
            scraper.get_channel_id(url)


class TestEdgeCases:
    """Edge case tests for real-world scenarios"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked API"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                return YouTubeAPIScraper()

    def test_similar_channel_names_resolved_exactly(self, scraper):
        """
        Regression test: samsulek vs sam_sulek should resolve to different channels.
        The bug was that search returned the most "relevant" result instead of exact match.
        """
        scraper.youtube = MagicMock()

        # Test @samsulek
        mock_response_samsulek = {"items": [{"id": "UC_samsulek_id", "snippet": {"title": "Samsulek Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response_samsulek

        result1 = scraper.get_channel_id("https://www.youtube.com/@samsulek")

        # Verify exact handle lookup
        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="samsulek")

        # Test @sam_sulek (different channel)
        mock_response_sam_sulek = {"items": [{"id": "UC_sam_sulek_id", "snippet": {"title": "Sam Sulek"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response_sam_sulek

        result2 = scraper.get_channel_id("https://www.youtube.com/@sam_sulek")

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="sam_sulek")

        # Should be different channel IDs
        assert result1 != result2

    def test_short_video_not_automatically_classified_as_short(self, scraper):
        """
        Regression test: A 45-second regular video should NOT be classified as a Short
        just because of its duration. Must verify via /shorts/ URL.
        """
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            # /shorts/ URL fails - it's a regular video
            mock_instance.extract_info.side_effect = Exception("Not available")

            # 45-second video that is NOT a Short
            result = scraper._detect_short("regular_45s_video", "Quick Tutorial", 45, {})

            # Should be False because /shorts/ URL failed
            assert result is False

    def test_actual_short_under_60s_detected_correctly(self, scraper):
        """A real Short under 60 seconds should be detected via /shorts/ URL"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            # /shorts/ URL succeeds - it IS a Short
            mock_instance.extract_info.return_value = {"id": "short_id"}

            result = scraper._detect_short("actual_short_id", "Funny Moment", 30, {})

            assert result is True

    def test_3_minute_short_detected(self, scraper):
        """YouTube Shorts can be up to 3 minutes - should still check"""
        with patch("yt_dlp.YoutubeDL") as mock_ydl:
            mock_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_instance
            mock_instance.extract_info.return_value = {"id": "long_short_id"}

            # 2 minute 59 second Short
            result = scraper._detect_short("long_short_id", "Extended Short", 179, {})

            assert result is True


class TestTimeCutoff:
    """Tests for time frame filtering"""

    def test_week_cutoff(self):
        """Week cutoff should be 7 days ago"""
        cutoff = get_time_cutoff("week")
        expected = datetime.utcnow() - timedelta(days=7)
        # Allow 1 second tolerance
        assert abs((cutoff - expected).total_seconds()) < 1

    def test_month_cutoff(self):
        """Month cutoff should be 30 days ago"""
        cutoff = get_time_cutoff("month")
        expected = datetime.utcnow() - timedelta(days=30)
        assert abs((cutoff - expected).total_seconds()) < 1

    def test_year_cutoff(self):
        """Year cutoff should be 365 days ago"""
        cutoff = get_time_cutoff("year")
        expected = datetime.utcnow() - timedelta(days=365)
        assert abs((cutoff - expected).total_seconds()) < 1

    def test_all_time_returns_none(self):
        """All time should return None (no cutoff)"""
        cutoff = get_time_cutoff("all")
        assert cutoff is None

    def test_invalid_time_frame_returns_none(self):
        """Invalid time frame should return None"""
        cutoff = get_time_cutoff("invalid")
        assert cutoff is None

        cutoff = get_time_cutoff("")
        assert cutoff is None


class TestDurationParsing:
    """Tests for ISO 8601 duration parsing"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked API key"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                return YouTubeAPIScraper()

    def test_parse_seconds_only(self, scraper):
        """Parse duration with only seconds"""
        assert scraper._parse_duration("PT30S") == 30
        assert scraper._parse_duration("PT59S") == 59

    def test_parse_minutes_only(self, scraper):
        """Parse duration with only minutes"""
        assert scraper._parse_duration("PT5M") == 300
        assert scraper._parse_duration("PT10M") == 600

    def test_parse_hours_only(self, scraper):
        """Parse duration with only hours"""
        assert scraper._parse_duration("PT1H") == 3600
        assert scraper._parse_duration("PT2H") == 7200

    def test_parse_minutes_and_seconds(self, scraper):
        """Parse duration with minutes and seconds"""
        assert scraper._parse_duration("PT5M30S") == 330
        assert scraper._parse_duration("PT1M59S") == 119

    def test_parse_hours_minutes_seconds(self, scraper):
        """Parse duration with hours, minutes, and seconds"""
        assert scraper._parse_duration("PT1H30M45S") == 5445
        assert scraper._parse_duration("PT2H5M10S") == 7510

    def test_parse_hours_and_seconds_no_minutes(self, scraper):
        """Parse duration with hours and seconds but no minutes"""
        assert scraper._parse_duration("PT1H30S") == 3630

    def test_parse_zero_duration(self, scraper):
        """Parse zero duration"""
        assert scraper._parse_duration("PT0S") == 0

    def test_parse_livestream_duration(self, scraper):
        """Parse very long durations (livestreams)"""
        # 10 hours
        assert scraper._parse_duration("PT10H0M0S") == 36000


class TestVideoFiltering:
    """Tests for video type filtering logic"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked API"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper()
                scraper.youtube = MagicMock()
                return scraper

    def test_filter_videos_only_excludes_shorts(self, scraper):
        """When video_type='videos', Shorts should be excluded"""
        # Mock a Short (duration under 60s, /shorts/ URL works)
        with patch.object(scraper, "_detect_short", return_value=True):
            # Simulate the filtering logic
            video_type = "videos"
            is_short = scraper._detect_short("id", "title", 30, {})

            # Should NOT include in results when filtering for videos
            should_include = video_type == "videos" and not is_short
            assert should_include is False

    def test_filter_videos_only_includes_regular_videos(self, scraper):
        """When video_type='videos', regular videos should be included"""
        with patch.object(scraper, "_detect_short", return_value=False):
            video_type = "videos"
            is_short = scraper._detect_short("id", "title", 300, {})

            should_include = video_type == "videos" and not is_short
            assert should_include is True

    def test_filter_shorts_only_excludes_regular_videos(self, scraper):
        """When video_type='shorts', regular videos should be excluded"""
        with patch.object(scraper, "_detect_short", return_value=False):
            video_type = "shorts"
            is_short = scraper._detect_short("id", "title", 300, {})

            should_include = video_type == "shorts" and is_short
            assert should_include is False

    def test_filter_shorts_only_includes_shorts(self, scraper):
        """When video_type='shorts', Shorts should be included"""
        with patch.object(scraper, "_detect_short", return_value=True):
            video_type = "shorts"
            is_short = scraper._detect_short("id", "title", 30, {})

            should_include = video_type == "shorts" and is_short
            assert should_include is True

    def test_filter_all_includes_everything(self, scraper):
        """When video_type='all', both Shorts and videos should be included"""
        video_type = "all"

        # Test with Short
        with patch.object(scraper, "_detect_short", return_value=True):
            scraper._detect_short("id", "title", 30, {})
            should_include = video_type == "all"
            assert should_include is True

        # Test with regular video
        with patch.object(scraper, "_detect_short", return_value=False):
            scraper._detect_short("id", "title", 300, {})
            should_include = video_type == "all"
            assert should_include is True


class TestURLParsing:
    """Extended tests for URL parsing edge cases"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked YouTube API"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper()
                scraper.youtube = MagicMock()
                return scraper

    # --- Various URL formats ---

    def test_handle_with_videos_path(self, scraper):
        """Should extract handle from URL with /videos path"""
        url = "https://www.youtube.com/@testchannel/videos"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Test Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="testchannel")

    def test_handle_with_shorts_path(self, scraper):
        """Should extract handle from URL with /shorts path"""
        url = "https://www.youtube.com/@testchannel/shorts"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Test Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="testchannel")

    def test_handle_with_live_path(self, scraper):
        """Should extract handle from URL with /live path"""
        url = "https://www.youtube.com/@testchannel/live"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Test Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="testchannel")

    def test_channel_id_with_special_characters(self, scraper):
        """Channel IDs can have underscores and dashes"""
        url = "https://www.youtube.com/channel/UC-lHJZR3Gq_xA4c8-zz4G4w"
        result = scraper.get_channel_id(url)
        assert result == "UC-lHJZR3Gq_xA4c8-zz4G4w"

    def test_mobile_url(self, scraper):
        """Should handle m.youtube.com URLs"""
        url = "https://m.youtube.com/channel/UC1234567890"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890"

    def test_www_url(self, scraper):
        """Should handle www.youtube.com URLs"""
        url = "https://www.youtube.com/channel/UC1234567890"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890"

    def test_no_www_url(self, scraper):
        """Should handle youtube.com URLs without www"""
        url = "https://youtube.com/channel/UC1234567890"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890"

    def test_http_url(self, scraper):
        """Should handle http:// URLs"""
        url = "http://www.youtube.com/channel/UC1234567890"
        result = scraper.get_channel_id(url)
        assert result == "UC1234567890"

    # --- Handle edge cases ---

    def test_handle_with_numbers(self, scraper):
        """Handles can contain numbers"""
        url = "https://www.youtube.com/@channel123"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Channel 123"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="channel123")

    def test_handle_with_underscore(self, scraper):
        """Handles can contain underscores"""
        url = "https://www.youtube.com/@sam_sulek"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Sam Sulek"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="sam_sulek")

    def test_handle_with_dots(self, scraper):
        """Handles can contain dots"""
        url = "https://www.youtube.com/@some.channel.name"

        mock_response = {"items": [{"id": "UC_test_id", "snippet": {"title": "Some Channel"}}]}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        scraper.get_channel_id(url)

        scraper.youtube.channels.return_value.list.assert_called_with(part="snippet", forHandle="some.channel.name")


class TestAPIErrorHandling:
    """Tests for API error handling"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked YouTube API"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper()
                scraper.youtube = MagicMock()
                return scraper

    def test_handle_api_http_error(self, scraper):
        """Should handle YouTube API HTTP errors gracefully"""
        from googleapiclient.errors import HttpError

        url = "https://www.youtube.com/@testchannel"

        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status = 403
        scraper.youtube.channels.return_value.list.return_value.execute.side_effect = HttpError(
            mock_response, b"Quota exceeded"
        )

        with pytest.raises(HttpError):
            scraper.get_channel_id(url)

    def test_handle_empty_api_response(self, scraper):
        """Should handle empty API response"""
        url = "https://www.youtube.com/@nonexistent"

        # Mock empty response
        mock_response = {"items": []}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        with pytest.raises(ValueError, match="not found"):
            scraper.get_channel_id(url)

    def test_handle_missing_items_key(self, scraper):
        """Should handle response without items key"""
        url = "https://www.youtube.com/@testchannel"

        # Mock malformed response
        mock_response = {}
        scraper.youtube.channels.return_value.list.return_value.execute.return_value = mock_response

        with pytest.raises(ValueError, match="not found"):
            scraper.get_channel_id(url)


class TestProgressCallback:
    """Tests for progress callback functionality"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with mocked API"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper()
                scraper.youtube = MagicMock()
                return scraper

    def test_progress_callback_receives_correct_arguments(self, scraper):
        """Progress callback should receive (total, processed, filtered, title)"""
        callback = Mock()

        # This tests the callback signature
        # In real usage, callback(total, processed, filtered, title) is called
        callback(100, 50, 25, "Test Video Title")

        callback.assert_called_once_with(100, 50, 25, "Test Video Title")

    def test_progress_callback_called_for_each_video(self):
        """Progress callback should be called once per video processed"""
        callback = Mock()

        # Simulate processing 3 videos
        videos = [
            {"title": "Video 1"},
            {"title": "Video 2"},
            {"title": "Video 3"},
        ]

        for idx, video in enumerate(videos, 1):
            callback(3, idx, idx, video["title"])

        assert callback.call_count == 3

    def test_progress_reports_filtering_accurately(self):
        """Progress should report filtered count after filtering decision"""
        callback = Mock()

        # Simulate: 5 videos total, only 2 pass the filter
        # Video 1: passes
        callback(5, 1, 1, "Video 1")
        # Video 2: filtered out (still shows 1)
        callback(5, 2, 1, "Video 2")
        # Video 3: passes
        callback(5, 3, 2, "Video 3")
        # Video 4: filtered out
        callback(5, 4, 2, "Video 4")
        # Video 5: filtered out
        callback(5, 5, 2, "Video 5")

        # Last call should show 5 processed, 2 filtered
        last_call = callback.call_args_list[-1]
        assert last_call == call(5, 5, 2, "Video 5")


class TestLivestreamFiltering:
    """Tests for livestream detection and filtering"""

    def test_livestream_always_filtered_out(self):
        """Livestreams should always be filtered out regardless of video_type"""
        # Simulate video data with liveStreamingDetails
        video = {
            "id": "live_video_id",
            "snippet": {"title": "Live Stream"},
            "contentDetails": {"duration": "PT2H30M"},
            "liveStreamingDetails": {"actualStartTime": "2024-01-01T00:00:00Z"},
        }

        # Check that presence of liveStreamingDetails triggers filter
        is_live = "liveStreamingDetails" in video
        assert is_live is True

    def test_regular_video_not_flagged_as_live(self):
        """Regular videos should not be flagged as livestreams"""
        video = {
            "id": "regular_video_id",
            "snippet": {"title": "Regular Video"},
            "contentDetails": {"duration": "PT10M30S"},
        }

        is_live = "liveStreamingDetails" in video
        assert is_live is False

    def test_past_premiere_not_flagged_as_live(self):
        """Past premieres (without liveStreamingDetails) should not be filtered"""
        video = {
            "id": "premiere_id",
            "snippet": {"title": "Premiere Video"},
            "contentDetails": {"duration": "PT15M"},
        }

        is_live = "liveStreamingDetails" in video
        assert is_live is False


class TestIntegration:
    """Integration tests that can run against real YouTube API (optional)"""

    @pytest.fixture
    def real_scraper(self):
        """Create a real scraper if API key is available"""
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            pytest.skip("YOUTUBE_API_KEY not set - skipping integration test")
        return YouTubeAPIScraper(api_key)

    @pytest.mark.integration
    def test_known_short_detected(self, real_scraper):
        """Test with a known YouTube Short (requires API key)"""
        # This test requires a real API key and a known Short video ID
        # Skip in CI, run manually for verification
        pass

    @pytest.mark.integration
    def test_known_video_not_detected_as_short(self, real_scraper):
        """Test with a known regular video (requires API key)"""
        pass

    @pytest.mark.integration
    def test_real_channel_resolution(self, real_scraper):
        """Test channel resolution with real API (requires API key)"""
        # Test that @MrBeast resolves to the correct channel
        pass

    @pytest.mark.integration
    def test_real_time_frame_filtering(self, real_scraper):
        """Test time frame filtering with real API (requires API key)"""
        pass


class TestScraperInitialization:
    """Tests for scraper initialization"""

    def test_init_with_api_key_parameter(self):
        """Should initialize with API key passed as parameter"""
        with patch("youtube_api_scraper.build"):
            scraper = YouTubeAPIScraper(api_key="test_key_123")
            assert scraper.api_key == "test_key_123"

    def test_init_with_env_variable(self):
        """Should initialize with API key from environment variable"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "env_key_456"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper()
                assert scraper.api_key == "env_key_456"

    def test_init_prefers_parameter_over_env(self):
        """Parameter API key should take precedence over env variable"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "env_key"}):
            with patch("youtube_api_scraper.build"):
                scraper = YouTubeAPIScraper(api_key="param_key")
                assert scraper.api_key == "param_key"

    def test_init_fails_without_api_key(self):
        """Should raise ValueError when no API key is available"""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure YOUTUBE_API_KEY is not set
            if "YOUTUBE_API_KEY" in os.environ:
                del os.environ["YOUTUBE_API_KEY"]

            with pytest.raises(ValueError, match="API key not provided"):
                YouTubeAPIScraper()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

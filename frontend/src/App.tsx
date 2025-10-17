/**
 * Main App component
 */
import { useState, useEffect } from 'react';
import ChannelInput from './components/ChannelInput';
import VideoList from './components/VideoList';
import DownloadProgress from './components/DownloadProgress';
import ScrapeProgress from './components/ScrapeProgress';
import {
  startScrape,
  getScrapeProgress,
  downloadVideos,
  getProgress,
  VideoMetadata,
  DownloadProgress as ProgressType,
  ScrapeProgress as ScrapeProgressType,
} from './api';

function App() {
  const [videos, setVideos] = useState<VideoMetadata[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<ProgressType>({
    current: 0,
    total: 0,
    percentage: 0,
    status: 'idle',
    current_video: null,
    completed_videos: [],
    failed_videos: [],
  });
  const [scrapeProgress, setScrapeProgress] = useState<ScrapeProgressType>({
    status: 'idle',
    total_videos: 0,
    processed_videos: 0,
    filtered_videos: 0,
    current_video: null,
    percentage: 0,
    error: null,
  });

  // Poll for scraping progress
  useEffect(() => {
    let interval: number | null = null;

    if (scrapeProgress.status === 'scraping') {
      interval = window.setInterval(async () => {
        try {
          const newProgress = await getScrapeProgress();
          setScrapeProgress(newProgress);

          // When scraping completes, set the videos
          if (newProgress.status === 'completed' && newProgress.result) {
            setVideos(newProgress.result.videos);
            if (newProgress.result.videos.length === 0) {
              setError('No eligible videos found. Channel may only have Shorts or livestreams.');
            }
          } else if (newProgress.status === 'error') {
            setError(newProgress.error || 'Failed to scrape channel');
          }
        } catch (err) {
          console.error('Error fetching scrape progress:', err);
        }
      }, 500); // Poll every 500ms for real-time updates
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [scrapeProgress.status]);

  // Poll for download progress
  useEffect(() => {
    let interval: number | null = null;

    if (progress.status === 'downloading') {
      interval = window.setInterval(async () => {
        try {
          const newProgress = await getProgress();
          setProgress(newProgress);
        } catch (err) {
          console.error('Error fetching progress:', err);
        }
      }, 1000); // Poll every second
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [progress.status]);

  const handleScrape = async (url: string) => {
    setError(null);
    setVideos([]);
    setScrapeProgress({
      status: 'scraping',
      total_videos: 0,
      processed_videos: 0,
      filtered_videos: 0,
      current_video: null,
      percentage: 0,
      error: null,
    });

    try {
      await startScrape(url);
      // Polling will handle the rest
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start scraping');
      console.error('Scrape error:', err);
      setScrapeProgress({ ...scrapeProgress, status: 'error', error: err.message });
    }
  };

  const handleDownload = async (videoIds: string[]) => {
    setError(null);

    try {
      await downloadVideos(videoIds);
      // Start polling by setting status to downloading
      setProgress({
        current: 0,
        total: videoIds.length,
        percentage: 0,
        status: 'downloading',
        current_video: null,
        completed_videos: [],
        failed_videos: [],
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start download');
      console.error('Download error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="container mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            🎵 YouTube MP3 Scraper
          </h1>
          <p className="text-gray-600 text-lg">
            Download videos from YouTube channels as high-quality MP3 files
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Automatically filters out Shorts and livestreams • Only videos longer than 1 minute
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-4xl mx-auto mb-6">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <p className="font-medium">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Channel Input */}
        <ChannelInput onScrape={handleScrape} isLoading={scrapeProgress.status === 'scraping'} />

        {/* Scrape Progress */}
        <ScrapeProgress progress={scrapeProgress} />

        {/* Video List */}
        {videos.length > 0 && (
          <VideoList
            videos={videos}
            onDownload={handleDownload}
            isDownloading={progress.status === 'downloading'}
          />
        )}

        {/* Download Progress */}
        <DownloadProgress progress={progress} />

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Built with FastAPI, React, and yt-dlp</p>
          <p className="mt-1">For personal use only • Respect copyright laws</p>
        </div>
      </div>
    </div>
  );
}

export default App;

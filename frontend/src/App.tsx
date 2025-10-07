/**
 * Main App component
 */
import { useState, useEffect } from 'react';
import ChannelInput from './components/ChannelInput';
import VideoList from './components/VideoList';
import DownloadProgress from './components/DownloadProgress';
import {
  scrapeChannel,
  downloadVideos,
  getProgress,
  VideoMetadata,
  DownloadProgress as ProgressType,
} from './api';

function App() {
  const [videos, setVideos] = useState<VideoMetadata[]>([]);
  const [isScrapingLoading, setIsScrapingLoading] = useState(false);
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

  // Poll for download progress
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (progress.status === 'downloading') {
      interval = setInterval(async () => {
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
    setIsScrapingLoading(true);
    setError(null);
    setVideos([]);

    try {
      const response = await scrapeChannel(url);
      setVideos(response.videos);

      if (response.videos.length === 0) {
        setError('No eligible videos found. Channel may only have Shorts or livestreams.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to scrape channel');
      console.error('Scrape error:', err);
    } finally {
      setIsScrapingLoading(false);
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
        <ChannelInput onScrape={handleScrape} isLoading={isScrapingLoading} />

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

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
  VideoType,
  TimeFrame,
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
              setError('No videos found matching your filters.');
            }
          } else if (newProgress.status === 'error') {
            setError(newProgress.error || 'Failed to scrape channel');
          }
        } catch (err) {
          console.error('Error fetching scrape progress:', err);
        }
      }, 500);
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
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [progress.status]);

  const handleScrape = async (url: string, videoType: VideoType, timeFrame: TimeFrame) => {
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
      await startScrape(url, videoType, timeFrame);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(error.response?.data?.detail || error.message || 'Failed to start scraping');
      console.error('Scrape error:', err);
      setScrapeProgress((prev) => ({ ...prev, status: 'error', error: String(err) }));
    }
  };

  const handleDownload = async (videoIds: string[]) => {
    setError(null);

    try {
      await downloadVideos(videoIds);
      setProgress({
        current: 0,
        total: videoIds.length,
        percentage: 0,
        status: 'downloading',
        current_video: null,
        completed_videos: [],
        failed_videos: [],
      });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(error.response?.data?.detail || error.message || 'Failed to start download');
      console.error('Download error:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] py-12 px-4">
      <div className="container mx-auto max-w-5xl">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-semibold text-white mb-2">
            YouTube to MP3
          </h1>
          <p className="text-slate-500 text-sm">
            Download audio from YouTube channels
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-6">
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          </div>
        )}

        {/* Channel Input */}
        <ChannelInput
          onScrape={handleScrape}
          isLoading={scrapeProgress.status === 'scraping'}
        />

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
        <div className="text-center mt-16 text-slate-600 text-xs">
          For personal use only
        </div>
      </div>
    </div>
  );
}

export default App;

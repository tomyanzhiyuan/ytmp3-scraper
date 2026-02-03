/**
 * API client for YouTube MP3 Scraper backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for scraping large channels
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface VideoMetadata {
  id: string;
  title: string;
  duration: number;
  thumbnail: string;
  url: string;
}

export type VideoType = 'all' | 'shorts' | 'videos';
export type TimeFrame = 'all' | 'week' | 'month' | 'year';
export type DownloadFormat = 'mp3' | 'mp4';

export interface ScrapeResponse {
  videos: VideoMetadata[];
  total_found: number;
  filtered_count: number;
}

export interface ScrapeProgress {
  status: 'idle' | 'scraping' | 'completed' | 'error';
  total_videos: number;
  processed_videos: number;
  filtered_videos: number;
  current_video: string | null;
  percentage: number;
  error: string | null;
  result?: {
    channel_name: string;
    videos: VideoMetadata[];
  };
}

export interface DownloadProgress {
  current: number;
  total: number;
  percentage: number;
  status: 'idle' | 'downloading' | 'completed' | 'error';
  current_video: string | null;
  completed_videos: string[];
  failed_videos: string[];
}

export interface FilesResponse {
  files: string[];
  total: number;
}

/**
 * Start scraping a YouTube channel (non-blocking)
 */
export const startScrape = async (
  channelUrl: string,
  videoType: VideoType = 'videos',
  timeFrame: TimeFrame = 'all'
): Promise<void> => {
  await api.post('/api/scrape', {
    channel_url: channelUrl,
    video_type: videoType,
    time_frame: timeFrame,
  });
};

/**
 * Get current scraping progress
 */
export const getScrapeProgress = async (): Promise<ScrapeProgress> => {
  const response = await api.get<ScrapeProgress>('/api/scrape-progress');
  return response.data;
};

/**
 * Start downloading selected videos in the specified format
 */
export const downloadVideos = async (
  videoIds: string[],
  format: DownloadFormat = 'mp3'
): Promise<void> => {
  await api.post('/api/download', {
    video_ids: videoIds,
    format: format,
  });
};

/**
 * Get current download progress
 */
export const getProgress = async (): Promise<DownloadProgress> => {
  const response = await api.get<DownloadProgress>('/api/progress');
  return response.data;
};

/**
 * Get list of downloaded files
 */
export const getFiles = async (): Promise<FilesResponse> => {
  const response = await api.get<FilesResponse>('/api/files');
  return response.data;
};

/**
 * Get output directory path
 */
export const getOutputDirectory = async (): Promise<string> => {
  const response = await api.get<{ output_directory: string }>('/api/output-dir');
  return response.data.output_directory;
};

export default api;

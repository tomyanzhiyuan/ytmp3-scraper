/**
 * API client for YouTube MP3 Scraper backend
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for scraping large channels
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

export interface ScrapeResponse {
  videos: VideoMetadata[];
  total_found: number;
  filtered_count: number;
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
 * Scrape a YouTube channel for videos
 */
export const scrapeChannel = async (channelUrl: string): Promise<ScrapeResponse> => {
  const response = await api.post<ScrapeResponse>('/api/scrape', {
    channel_url: channelUrl,
  });
  return response.data;
};

/**
 * Start downloading selected videos
 */
export const downloadVideos = async (videoIds: string[]): Promise<void> => {
  await api.post('/api/download', {
    video_ids: videoIds,
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

/**
 * Video list component with selection
 */
import { useState, useEffect } from 'react';
import { VideoMetadata } from '../api';

interface VideoListProps {
  videos: VideoMetadata[];
  onDownload: (videoIds: string[]) => void;
  isDownloading: boolean;
}

export default function VideoList({ videos, onDownload, isDownloading }: VideoListProps) {
  const [selectedVideos, setSelectedVideos] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Reset selection when videos change
    setSelectedVideos(new Set());
  }, [videos]);

  const toggleVideo = (videoId: string) => {
    const newSelected = new Set(selectedVideos);
    if (newSelected.has(videoId)) {
      newSelected.delete(videoId);
    } else {
      newSelected.add(videoId);
    }
    setSelectedVideos(newSelected);
  };

  const selectAll = () => {
    setSelectedVideos(new Set(videos.map(v => v.id)));
  };

  const deselectAll = () => {
    setSelectedVideos(new Set());
  };

  const handleDownloadSelected = () => {
    if (selectedVideos.size > 0) {
      onDownload(Array.from(selectedVideos));
    }
  };

  const handleDownloadAll = () => {
    onDownload(videos.map(v => v.id));
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  if (videos.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-6xl mx-auto mt-8">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            Found {videos.length} Videos
          </h2>
          <div className="flex gap-2">
            <button
              onClick={selectAll}
              className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              disabled={isDownloading}
            >
              Select All
            </button>
            <button
              onClick={deselectAll}
              className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              disabled={isDownloading}
            >
              Deselect All
            </button>
          </div>
        </div>

        <div className="mb-4 flex gap-3">
          <button
            onClick={handleDownloadSelected}
            disabled={selectedVideos.size === 0 || isDownloading}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            Download Selected ({selectedVideos.size})
          </button>
          <button
            onClick={handleDownloadAll}
            disabled={isDownloading}
            className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            Download All ({videos.length})
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[600px] overflow-y-auto">
          {videos.map((video) => (
            <div
              key={video.id}
              className={`border rounded-lg overflow-hidden cursor-pointer transition ${
                selectedVideos.has(video.id)
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => toggleVideo(video.id)}
            >
              <div className="relative">
                <img
                  src={video.thumbnail}
                  alt={video.title}
                  className="w-full h-40 object-cover"
                />
                <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                  {formatDuration(video.duration)}
                </div>
                {selectedVideos.has(video.id) && (
                  <div className="absolute top-2 right-2 bg-blue-600 text-white rounded-full p-1">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              <div className="p-3">
                <h3 className="text-sm font-medium text-gray-800 line-clamp-2">
                  {video.title}
                </h3>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

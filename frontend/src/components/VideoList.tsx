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
    setSelectedVideos(new Set(videos.map((v) => v.id)));
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
    onDownload(videos.map((v) => v.id));
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
    <div className="w-full max-w-4xl mx-auto mt-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-medium text-white">{videos.length} videos</h2>
        <div className="flex gap-2 text-xs">
          <button
            onClick={selectAll}
            className="px-3 py-1.5 text-slate-400 hover:text-white transition-colors"
            disabled={isDownloading}
          >
            Select all
          </button>
          <button
            onClick={deselectAll}
            className="px-3 py-1.5 text-slate-400 hover:text-white transition-colors"
            disabled={isDownloading}
          >
            Clear
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-5">
        <button
          onClick={handleDownloadSelected}
          disabled={selectedVideos.size === 0 || isDownloading}
          className="flex-1 bg-white text-black py-2.5 px-4 rounded-lg text-sm font-medium hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Download selected ({selectedVideos.size})
        </button>
        <button
          onClick={handleDownloadAll}
          disabled={isDownloading}
          className="px-4 py-2.5 bg-[#1a1a24] border border-white/10 text-white rounded-lg text-sm font-medium hover:bg-[#22222e] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Download all
        </button>
      </div>

      {/* Video Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 max-h-[500px] overflow-y-auto pr-1">
        {videos.map((video) => (
          <div
            key={video.id}
            className={`group bg-[#1a1a24] rounded-lg overflow-hidden cursor-pointer border transition-colors ${
              selectedVideos.has(video.id)
                ? 'border-white/40'
                : 'border-transparent hover:border-white/20'
            }`}
            onClick={() => toggleVideo(video.id)}
          >
            <div className="relative aspect-video">
              <img
                src={video.thumbnail}
                alt={video.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-1.5 right-1.5 bg-black/80 text-white text-[10px] px-1.5 py-0.5 rounded font-mono">
                {formatDuration(video.duration)}
              </div>
              {selectedVideos.has(video.id) && (
                <div className="absolute top-1.5 right-1.5 bg-white text-black rounded p-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              )}
            </div>
            <div className="p-2.5">
              <h3 className="text-xs text-slate-300 line-clamp-2 leading-tight">
                {video.title}
              </h3>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

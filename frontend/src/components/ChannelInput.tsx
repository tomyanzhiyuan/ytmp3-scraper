/**
 * Channel URL input component with filter options
 */
import { useState } from 'react';
import { VideoType, TimeFrame } from '../api';

interface ChannelInputProps {
  onScrape: (url: string, videoType: VideoType, timeFrame: TimeFrame) => void;
  isLoading: boolean;
}

export default function ChannelInput({ onScrape, isLoading }: ChannelInputProps) {
  const [url, setUrl] = useState('');
  const [videoType, setVideoType] = useState<VideoType>('videos');
  const [timeFrame, setTimeFrame] = useState<TimeFrame>('all');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onScrape(url.trim(), videoType, timeFrame);
    }
  };

  return (
    <div className="mx-auto w-full max-w-2xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* URL Input */}
        <input
          id="channel-url"
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.youtube.com/@channelname"
          className="w-full rounded-lg border border-white/10 bg-[#1a1a24] px-4 py-3.5 text-white placeholder-slate-500 transition-colors focus:border-white/30 focus:outline-none"
          disabled={isLoading}
        />

        {/* Filter Options */}
        <div className="flex flex-col gap-3 sm:flex-row">
          {/* Video Type Filter */}
          <div className="flex-1">
            <label className="mb-1.5 block text-xs uppercase tracking-wide text-slate-500">
              Content Type
            </label>
            <select
              value={videoType}
              onChange={(e) => setVideoType(e.target.value as VideoType)}
              disabled={isLoading}
              className="w-full cursor-pointer rounded-lg border border-white/10 bg-[#1a1a24] px-3 py-2.5 text-sm text-white transition-colors focus:border-white/30 focus:outline-none disabled:opacity-50"
            >
              <option value="videos">Videos only</option>
              <option value="shorts">Shorts only</option>
              <option value="all">All content</option>
            </select>
          </div>

          {/* Time Frame Filter */}
          <div className="flex-1">
            <label className="mb-1.5 block text-xs uppercase tracking-wide text-slate-500">
              Time Frame
            </label>
            <select
              value={timeFrame}
              onChange={(e) => setTimeFrame(e.target.value as TimeFrame)}
              disabled={isLoading}
              className="w-full cursor-pointer rounded-lg border border-white/10 bg-[#1a1a24] px-3 py-2.5 text-sm text-white transition-colors focus:border-white/30 focus:outline-none disabled:opacity-50"
            >
              <option value="week">Last week</option>
              <option value="month">Last month</option>
              <option value="year">Last year</option>
              <option value="all">All time</option>
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="w-full rounded-lg bg-white px-6 py-3.5 font-medium text-black transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg
                className="h-5 w-5 animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Scanning...
            </span>
          ) : (
            'Scan Channel'
          )}
        </button>
      </form>
    </div>
  );
}

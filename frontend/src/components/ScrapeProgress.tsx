/**
 * Scraping progress component
 */
import { ScrapeProgress as ProgressType } from '../api';

interface ScrapeProgressProps {
  progress: ProgressType;
}

export default function ScrapeProgress({ progress }: ScrapeProgressProps) {
  if (progress.status === 'idle') {
    return null;
  }

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <div className="bg-[#1a1a24] border border-white/5 rounded-lg p-5">
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>
              {progress.processed_videos > 0
                ? `Processing ${progress.processed_videos} of ${progress.total_videos}`
                : 'Fetching videos...'}
            </span>
            <span>{Math.round(progress.percentage)}%</span>
          </div>
          <div className="w-full bg-[#12121a] rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-white h-full transition-all duration-300 ease-out"
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-6 text-sm">
          <div>
            <span className="text-slate-500">Found:</span>{' '}
            <span className="text-white">{progress.total_videos}</span>
          </div>
          <div>
            <span className="text-slate-500">Eligible:</span>{' '}
            <span className="text-white">{progress.filtered_videos}</span>
          </div>
        </div>

        {/* Current Video */}
        {progress.current_video && progress.status === 'scraping' && (
          <div className="mt-3 text-xs text-slate-500 truncate">
            {progress.current_video}
          </div>
        )}

        {/* Error */}
        {progress.status === 'error' && progress.error && (
          <div className="mt-3 text-sm text-red-400">{progress.error}</div>
        )}
      </div>
    </div>
  );
}

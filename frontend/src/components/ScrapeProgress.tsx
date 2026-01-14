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
    <div className="mx-auto mt-8 w-full max-w-2xl">
      <div className="rounded-lg border border-white/5 bg-[#1a1a24] p-5">
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="mb-2 flex justify-between text-xs text-slate-500">
            <span>
              {progress.processed_videos > 0
                ? `Processing ${progress.processed_videos} of ${progress.total_videos}`
                : 'Fetching videos...'}
            </span>
            <span>{Math.round(progress.percentage)}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#12121a]">
            <div
              className="h-full bg-white transition-all duration-300 ease-out"
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
          <div className="mt-3 truncate text-xs text-slate-500">{progress.current_video}</div>
        )}

        {/* Error */}
        {progress.status === 'error' && progress.error && (
          <div className="mt-3 text-sm text-red-400">{progress.error}</div>
        )}
      </div>
    </div>
  );
}

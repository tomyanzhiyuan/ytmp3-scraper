/**
 * Download progress component
 */
import { DownloadProgress as ProgressType } from '../api';

interface DownloadProgressProps {
  progress: ProgressType;
}

export default function DownloadProgress({ progress }: DownloadProgressProps) {
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
              {progress.current} / {progress.total} downloads
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

        {/* Current Video */}
        {progress.current_video && progress.status === 'downloading' && (
          <div className="mb-3 truncate text-sm text-slate-400">{progress.current_video}</div>
        )}

        {/* Status */}
        {progress.status === 'completed' && (
          <div className="text-sm text-emerald-400">
            ✓ {progress.completed_videos.length} downloads complete
          </div>
        )}

        {/* Failed Videos */}
        {progress.failed_videos.length > 0 && (
          <div className="mt-3 text-sm text-red-400">{progress.failed_videos.length} failed</div>
        )}
      </div>
    </div>
  );
}

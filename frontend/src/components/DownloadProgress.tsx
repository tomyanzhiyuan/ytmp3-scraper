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
    <div className="w-full max-w-2xl mx-auto mt-8">
      <div className="bg-[#1a1a24] border border-white/5 rounded-lg p-5">
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>
              {progress.current} / {progress.total} downloads
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

        {/* Current Video */}
        {progress.current_video && progress.status === 'downloading' && (
          <div className="text-sm text-slate-400 truncate mb-3">
            {progress.current_video}
          </div>
        )}

        {/* Status */}
        {progress.status === 'completed' && (
          <div className="text-sm text-emerald-400">
            ✓ {progress.completed_videos.length} downloads complete
          </div>
        )}

        {/* Failed Videos */}
        {progress.failed_videos.length > 0 && (
          <div className="mt-3 text-sm text-red-400">
            {progress.failed_videos.length} failed
          </div>
        )}
      </div>
    </div>
  );
}

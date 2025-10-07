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
    <div className="w-full max-w-4xl mx-auto mt-8">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Download Progress</h2>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>
              {progress.current} / {progress.total} videos
            </span>
            <span>{Math.round(progress.percentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="bg-blue-600 h-full transition-all duration-300 ease-out"
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>

        {/* Current Video */}
        {progress.current_video && progress.status === 'downloading' && (
          <div className="mb-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Currently downloading:</p>
            <p className="font-medium text-gray-800">{progress.current_video}</p>
          </div>
        )}

        {/* Status */}
        <div className="mb-4">
          <span
            className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
              progress.status === 'downloading'
                ? 'bg-blue-100 text-blue-800'
                : progress.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : progress.status === 'error'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {progress.status === 'downloading' && '⏳ Downloading...'}
            {progress.status === 'completed' && '✅ Completed'}
            {progress.status === 'error' && '❌ Error'}
            {progress.status === 'idle' && '⏸️ Idle'}
          </span>
        </div>

        {/* Completed Videos */}
        {progress.completed_videos.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">
              Completed ({progress.completed_videos.length})
            </h3>
            <div className="max-h-40 overflow-y-auto bg-gray-50 rounded-lg p-3">
              <ul className="space-y-1">
                {progress.completed_videos.map((video, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="flex-1">{video}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Failed Videos */}
        {progress.failed_videos.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-red-700 mb-2">
              Failed ({progress.failed_videos.length})
            </h3>
            <div className="max-h-40 overflow-y-auto bg-red-50 rounded-lg p-3">
              <ul className="space-y-1">
                {progress.failed_videos.map((video, idx) => (
                  <li key={idx} className="text-sm text-red-600 flex items-start">
                    <span className="mr-2">✗</span>
                    <span className="flex-1">{video}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

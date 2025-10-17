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
    <div className="w-full max-w-4xl mx-auto mt-8">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Scraping Channel...</h2>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>
              Processing video {progress.processed_videos} of {progress.total_videos}
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

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{progress.total_videos}</div>
            <div className="text-sm text-gray-600">Total Found</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{progress.filtered_videos}</div>
            <div className="text-sm text-gray-600">Eligible Videos</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">
              {progress.total_videos - progress.filtered_videos}
            </div>
            <div className="text-sm text-gray-600">Filtered Out</div>
          </div>
        </div>

        {/* Current Video */}
        {progress.current_video && progress.status === 'scraping' && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Currently processing:</p>
            <p className="font-medium text-gray-800 truncate">{progress.current_video}</p>
          </div>
        )}

        {/* Error */}
        {progress.status === 'error' && progress.error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm font-semibold text-red-700 mb-1">Error:</p>
            <p className="text-sm text-red-600">{progress.error}</p>
          </div>
        )}

        {/* Status */}
        <div className="mt-4">
          <span
            className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
              progress.status === 'scraping'
                ? 'bg-blue-100 text-blue-800'
                : progress.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : progress.status === 'error'
                ? 'bg-red-100 text-red-800'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {progress.status === 'scraping' && '⏳ Scraping...'}
            {progress.status === 'completed' && '✅ Completed'}
            {progress.status === 'error' && '❌ Error'}
          </span>
        </div>
      </div>
    </div>
  );
}

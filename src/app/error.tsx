'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log error to error reporting service
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center py-16">
      <div className="container">
        <div className="max-w-2xl mx-auto text-center">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-24 h-24 bg-red-100 rounded-full mb-6">
            <svg
              className="w-12 h-12 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            Something went wrong
          </h1>

          {/* Description */}
          <p className="text-lg text-neutral-600 mb-8">
            We&apos;re having trouble loading this page. This might be a temporary issue.
            Please try again.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <button onClick={() => reset()} className="btn-primary">
              Try Again
            </button>
            <Link href="/" className="btn-secondary">
              Go Home
            </Link>
          </div>

          {/* Error Details */}
          {error.digest && (
            <div className="mb-8 p-4 bg-neutral-100 rounded-lg border border-neutral-300">
              <p className="text-sm text-neutral-600">
                <strong>Error ID:</strong>{' '}
                <code className="font-mono text-xs">{error.digest}</code>
              </p>
            </div>
          )}

          {/* Help Text */}
          <div className="p-6 bg-white rounded-lg border border-neutral-200 text-left">
            <h3 className="text-lg font-semibold text-neutral-900 mb-3">
              What happened?
            </h3>
            <p className="text-sm text-neutral-700 mb-4">
              An unexpected error occurred while processing your request. This could be
              due to:
            </p>
            <ul className="space-y-2 text-sm text-neutral-700 mb-6">
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>A temporary server issue</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>Invalid or corrupted data</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>Network connectivity problems</span>
              </li>
            </ul>
            <p className="text-sm text-neutral-700">
              If this problem persists, please{' '}
              <a
                href="https://github.com/yourusername/OpenUSPolitics/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-700 hover:text-primary-800 font-medium"
              >
                report it on GitHub
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

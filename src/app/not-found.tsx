import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center py-16">
      <div className="container">
        <div className="max-w-2xl mx-auto text-center">
          {/* 404 Number */}
          <div className="mb-6">
            <h1 className="text-9xl font-bold text-primary-800 opacity-20">404</h1>
          </div>

          {/* Icon */}
          <div className="inline-flex items-center justify-center w-24 h-24 bg-primary-100 rounded-full mb-6 -mt-20">
            <svg
              className="w-12 h-12 text-primary-700"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* Title */}
          <h2 className="text-4xl font-bold text-neutral-900 mb-4">
            Page Not Found
          </h2>

          {/* Description */}
          <p className="text-lg text-neutral-600 mb-8">
            The page you&apos;re looking for doesn&apos;t exist. It may have been moved, or the
            URL might be incorrect.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/" className="btn-primary">
              Browse All Bills
            </Link>
            <Link href="/about" className="btn-secondary">
              Learn More
            </Link>
          </div>

          {/* Help Text */}
          <div className="mt-12 p-6 bg-white rounded-lg border border-neutral-200 text-left">
            <h3 className="text-lg font-semibold text-neutral-900 mb-3">
              What you can do:
            </h3>
            <ul className="space-y-2 text-sm text-neutral-700">
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Check the URL for typos or formatting errors
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Use the search feature to find specific bills
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Visit our homepage to browse recently analyzed bills
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Check out the About page to learn how our analysis works
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

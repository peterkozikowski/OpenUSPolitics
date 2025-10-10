import Link from 'next/link'

export default function BillNotFound() {
  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center py-16">
      <div className="container">
        <div className="max-w-2xl mx-auto text-center">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-24 h-24 bg-neutral-200 rounded-full mb-6">
            <svg
              className="w-12 h-12 text-neutral-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            Bill Not Found
          </h1>

          {/* Description */}
          <p className="text-lg text-neutral-600 mb-8">
            We couldn&apos;t find the bill you&apos;re looking for. It may not exist in our
            database yet, or the bill number might be incorrect.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/" className="btn-primary">
              Browse All Bills
            </Link>
            <Link
              href="https://www.congress.gov"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              Search Congress.gov
            </Link>
          </div>

          {/* Help Text */}
          <div className="mt-12 p-6 bg-white rounded-lg border border-neutral-200 text-left">
            <h2 className="text-lg font-semibold text-neutral-900 mb-3">
              Common Issues
            </h2>
            <ul className="space-y-2 text-sm text-neutral-700">
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Check the bill number format (e.g., &quot;H.R. 1234&quot; or &quot;S. 5678&quot;)
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Very recent bills may not be analyzed yet (we update daily)
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Bills from previous congresses may not be in our database
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

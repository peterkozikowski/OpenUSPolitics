import Link from 'next/link'

export default function RepresentativeNotFound() {
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
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-4xl font-bold text-neutral-900 mb-4">
            Representative Not Found
          </h1>

          {/* Description */}
          <p className="text-lg text-neutral-600 mb-8">
            We couldn&apos;t find the representative you&apos;re looking for. They may not have
            sponsored any bills yet, or the ID might be incorrect.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/" className="btn-primary">
              Browse All Bills
            </Link>
            <Link
              href="https://www.congress.gov/members"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              Find on Congress.gov
            </Link>
          </div>

          {/* Help Text */}
          <div className="mt-12 p-6 bg-white rounded-lg border border-neutral-200 text-left">
            <h2 className="text-lg font-semibold text-neutral-900 mb-3">
              How to Find Representatives
            </h2>
            <ul className="space-y-2 text-sm text-neutral-700">
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Browse bills to find representatives who sponsored them
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  Representative profiles are created when they sponsor legislation
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary-600 mt-0.5">•</span>
                <span>
                  For comprehensive member directories, visit Congress.gov
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

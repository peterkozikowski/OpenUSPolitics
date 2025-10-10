import { Bill, BillStatus } from '@/lib/types'
import Link from 'next/link'

interface BillHeaderProps {
  bill: Bill
}

/**
 * Get status color and label
 */
function getStatusInfo(status: BillStatus): { color: string; label: string } {
  const statusMap: Record<BillStatus, { color: string; label: string }> = {
    [BillStatus.INTRODUCED]: {
      color: 'bg-neutral-200 text-neutral-800',
      label: 'Introduced',
    },
    [BillStatus.IN_COMMITTEE]: {
      color: 'bg-yellow-100 text-yellow-800',
      label: 'In Committee',
    },
    [BillStatus.PASSED_HOUSE]: {
      color: 'bg-blue-100 text-blue-800',
      label: 'Passed House',
    },
    [BillStatus.PASSED_SENATE]: {
      color: 'bg-blue-100 text-blue-800',
      label: 'Passed Senate',
    },
    [BillStatus.SIGNED]: {
      color: 'bg-green-100 text-green-800',
      label: 'Signed into Law',
    },
    [BillStatus.VETOED]: {
      color: 'bg-red-100 text-red-800',
      label: 'Vetoed',
    },
    [BillStatus.FAILED]: {
      color: 'bg-neutral-300 text-neutral-800',
      label: 'Failed',
    },
  }

  return statusMap[status] || statusMap[BillStatus.INTRODUCED]
}

/**
 * Format date to readable string
 */
function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * Get party full name
 */
function getPartyName(party: string): string {
  switch (party) {
    case 'D':
      return 'Democrat'
    case 'R':
      return 'Republican'
    case 'I':
      return 'Independent'
    default:
      return party
  }
}

export default function BillHeader({ bill }: BillHeaderProps) {
  const statusInfo = getStatusInfo(bill.status)

  return (
    <header className="bg-gradient-to-br from-primary-800 to-primary-900 text-white">
      <div className="container py-8 md:py-12">
        {/* Bill Number and Status */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <span className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-lg text-lg font-bold">
            {bill.bill_number}
          </span>
          <span
            className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold ${statusInfo.color}`}
          >
            {statusInfo.label}
          </span>
        </div>

        {/* Bill Title */}
        <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6 leading-tight">
          {bill.title}
        </h1>

        {/* Sponsor Information */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 mb-8">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-lg font-bold">
              {bill.sponsor.name.charAt(0)}
            </div>
            <div>
              <div className="text-sm text-primary-100">Sponsored by</div>
              <div className="font-semibold">
                {bill.sponsor.name}{' '}
                <span className="text-primary-200">
                  ({getPartyName(bill.sponsor.party)}-{bill.sponsor.state})
                </span>
              </div>
            </div>
          </div>

          <div className="hidden sm:block text-primary-300">•</div>

          <div>
            <div className="text-sm text-primary-100">Introduced</div>
            <div className="font-semibold">{formatDate(bill.introduced_date)}</div>
          </div>

          {bill.cosponsors.length > 0 && (
            <>
              <div className="hidden sm:block text-primary-300">•</div>
              <div>
                <div className="text-sm text-primary-100">Cosponsors</div>
                <div className="font-semibold">{bill.cosponsors.length}</div>
              </div>
            </>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3">
          <a
            href={bill.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-primary-800 rounded-lg font-semibold hover:bg-primary-50 transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
            View on Congress.gov
          </a>

          <Link
            href={`https://github.com/yourusername/OpenUSPolitics/issues/new?title=Issue with ${encodeURIComponent(bill.bill_number)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 backdrop-blur-sm text-white rounded-lg font-semibold hover:bg-white/20 transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-800"
          >
            <svg
              className="w-5 h-5"
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
            Report Issue
          </Link>
        </div>
      </div>
    </header>
  )
}

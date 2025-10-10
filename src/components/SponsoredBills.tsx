import { BillSummary, BillStatus } from '@/lib/types'
import BillCard from './BillCard'

interface SponsoredBillsProps {
  bills: BillSummary[]
}

/**
 * Group bills by status
 */
function groupBillsByStatus(bills: BillSummary[]): {
  active: BillSummary[]
  passed: BillSummary[]
  other: BillSummary[]
} {
  const groups = {
    active: [] as BillSummary[],
    passed: [] as BillSummary[],
    other: [] as BillSummary[],
  }

  bills.forEach((bill) => {
    if (
      bill.status === BillStatus.SIGNED ||
      bill.status === BillStatus.PASSED_HOUSE ||
      bill.status === BillStatus.PASSED_SENATE
    ) {
      groups.passed.push(bill)
    } else if (
      bill.status === BillStatus.INTRODUCED ||
      bill.status === BillStatus.IN_COMMITTEE
    ) {
      groups.active.push(bill)
    } else {
      groups.other.push(bill)
    }
  })

  return groups
}

export default function SponsoredBills({ bills }: SponsoredBillsProps) {
  // Sort bills by most recent first
  const sortedBills = [...bills].sort((a, b) => {
    return new Date(b.introduced_date).getTime() - new Date(a.introduced_date).getTime()
  })

  const groupedBills = groupBillsByStatus(sortedBills)

  if (bills.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-neutral-100 rounded-full mb-4">
          <svg
            className="w-8 h-8 text-neutral-400"
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
        <h3 className="text-lg font-semibold text-neutral-900 mb-2">
          No Sponsored Bills
        </h3>
        <p className="text-neutral-600">
          No bills have been sponsored by this representative yet.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-neutral-900">
          Sponsored Legislation
        </h2>
        <span className="text-sm text-neutral-600">
          {bills.length} {bills.length === 1 ? 'bill' : 'bills'}
        </span>
      </div>

      {/* Active Bills */}
      {groupedBills.active.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-accent-600 rounded-full animate-pulse" />
            Active Bills ({groupedBills.active.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {groupedBills.active.map((bill) => (
              <BillCard key={bill.bill_number} bill={bill} />
            ))}
          </div>
        </section>
      )}

      {/* Passed Bills */}
      {groupedBills.passed.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Passed Bills ({groupedBills.passed.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {groupedBills.passed.map((bill) => (
              <BillCard key={bill.bill_number} bill={bill} />
            ))}
          </div>
        </section>
      )}

      {/* Other Bills */}
      {groupedBills.other.length > 0 && (
        <section>
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">
            Other Bills ({groupedBills.other.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {groupedBills.other.map((bill) => (
              <BillCard key={bill.bill_number} bill={bill} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

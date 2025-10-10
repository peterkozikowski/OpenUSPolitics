import Link from 'next/link'
import { BillSummary, BillStatus, BillTopic } from '@/lib/types'

interface BillCardProps {
  bill: BillSummary
}

/**
 * Get status color and label
 */
function getStatusInfo(status: BillStatus): { color: string; label: string } {
  const statusMap: Record<BillStatus, { color: string; label: string }> = {
    [BillStatus.INTRODUCED]: {
      color: 'bg-neutral-200 text-neutral-700',
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
      color: 'bg-neutral-300 text-neutral-700',
      label: 'Failed',
    },
  }

  return statusMap[status] || statusMap[BillStatus.INTRODUCED]
}

/**
 * Get topic display name
 */
function getTopicLabel(topic: BillTopic): string {
  const topicMap: Record<BillTopic, string> = {
    [BillTopic.HEALTHCARE]: 'Healthcare',
    [BillTopic.DEFENSE]: 'Defense',
    [BillTopic.ECONOMY]: 'Economy',
    [BillTopic.EDUCATION]: 'Education',
    [BillTopic.ENVIRONMENT]: 'Environment',
    [BillTopic.INFRASTRUCTURE]: 'Infrastructure',
    [BillTopic.IMMIGRATION]: 'Immigration',
    [BillTopic.JUSTICE]: 'Justice',
    [BillTopic.TECHNOLOGY]: 'Technology',
    [BillTopic.FOREIGN_POLICY]: 'Foreign Policy',
    [BillTopic.AGRICULTURE]: 'Agriculture',
    [BillTopic.ENERGY]: 'Energy',
    [BillTopic.LABOR]: 'Labor',
    [BillTopic.SOCIAL_SERVICES]: 'Social Services',
    [BillTopic.OTHER]: 'Other',
  }

  return topicMap[topic] || topic
}

/**
 * Format date to readable string
 */
function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Get party color
 */
function getPartyColor(party: string): string {
  switch (party) {
    case 'D':
      return 'text-blue-600'
    case 'R':
      return 'text-red-600'
    case 'I':
      return 'text-purple-600'
    default:
      return 'text-neutral-600'
  }
}

export default function BillCard({ bill }: BillCardProps) {
  const statusInfo = getStatusInfo(bill.status)

  return (
    <Link
      href={`/bills/${encodeURIComponent(bill.bill_number)}/`}
      className="card p-6 block group transition-all duration-200 hover:scale-[1.02]"
    >
      {/* Header: Bill number and status */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-primary-800 group-hover:text-primary-700 transition-colors mb-1">
            {bill.bill_number}
          </h3>
          <p className="text-sm text-neutral-600">
            Sponsor:{' '}
            <span className={`font-medium ${getPartyColor(bill.sponsor_party)}`}>
              {bill.sponsor_name}
            </span>
          </p>
        </div>

        <span
          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${statusInfo.color} whitespace-nowrap`}
        >
          {statusInfo.label}
        </span>
      </div>

      {/* Title */}
      <h4 className="text-neutral-900 font-medium mb-3 line-clamp-2 leading-snug">
        {bill.title}
      </h4>

      {/* Footer: Topics and date */}
      <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-neutral-200">
        {/* Topics */}
        <div className="flex flex-wrap gap-1.5 flex-1">
          {bill.topic.slice(0, 3).map((topic) => (
            <span
              key={topic}
              className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-neutral-100 text-neutral-700"
            >
              {getTopicLabel(topic)}
            </span>
          ))}
          {bill.topic.length > 3 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-neutral-100 text-neutral-700">
              +{bill.topic.length - 3} more
            </span>
          )}
        </div>

        {/* Date */}
        <time
          className="text-xs text-neutral-500 whitespace-nowrap"
          dateTime={bill.introduced_date}
        >
          {formatDate(bill.introduced_date)}
        </time>
      </div>
    </Link>
  )
}

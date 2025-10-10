import Link from 'next/link'
import { ExecutiveOrderStatus, ExecutiveOrderTopic } from '@/lib/types'

interface ExecutiveOrderSummary {
  executive_order_number: string
  title: string
  president: string
  signing_date: string
  status: ExecutiveOrderStatus
  topic: ExecutiveOrderTopic[]
}

interface ExecutiveOrderCardProps {
  order: ExecutiveOrderSummary
}

/**
 * Get status color and label
 */
function getStatusInfo(status: ExecutiveOrderStatus): { color: string; label: string } {
  const statusMap: Record<ExecutiveOrderStatus, { color: string; label: string }> = {
    [ExecutiveOrderStatus.ACTIVE]: {
      color: 'bg-green-100 text-green-800',
      label: 'Active',
    },
    [ExecutiveOrderStatus.REVOKED]: {
      color: 'bg-red-100 text-red-800',
      label: 'Revoked',
    },
    [ExecutiveOrderStatus.AMENDED]: {
      color: 'bg-yellow-100 text-yellow-800',
      label: 'Amended',
    },
    [ExecutiveOrderStatus.EXPIRED]: {
      color: 'bg-neutral-300 text-neutral-700',
      label: 'Expired',
    },
  }

  return statusMap[status] || statusMap[ExecutiveOrderStatus.ACTIVE]
}

/**
 * Get topic display name
 */
function getTopicLabel(topic: ExecutiveOrderTopic): string {
  const topicMap: Record<ExecutiveOrderTopic, string> = {
    healthcare: 'Healthcare',
    defense: 'Defense',
    economy: 'Economy',
    education: 'Education',
    environment: 'Environment',
    infrastructure: 'Infrastructure',
    immigration: 'Immigration',
    justice: 'Justice',
    technology: 'Technology',
    foreign_policy: 'Foreign Policy',
    agriculture: 'Agriculture',
    energy: 'Energy',
    labor: 'Labor',
    social_services: 'Social Services',
    other: 'Other',
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
 * Get president badge color
 */
function getPresidentColor(president: string): string {
  const pres = president.toLowerCase()
  if (pres.includes('biden')) return 'text-blue-600'
  if (pres.includes('trump')) return 'text-red-600'
  if (pres.includes('obama')) return 'text-blue-600'
  return 'text-neutral-600'
}

export default function ExecutiveOrderCard({ order }: ExecutiveOrderCardProps) {
  const statusInfo = getStatusInfo(order.status)

  return (
    <Link
      href={`/executive-orders/EO%20${order.executive_order_number}/`}
      className="card p-6 block group transition-all duration-200 hover:scale-[1.02]"
    >
      {/* Header: EO number and status */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-primary-800 group-hover:text-primary-700 transition-colors mb-1">
            Executive Order {order.executive_order_number}
          </h3>
          <p className="text-sm text-neutral-600">
            President:{' '}
            <span className={`font-medium ${getPresidentColor(order.president)}`}>
              {order.president}
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
        {order.title}
      </h4>

      {/* Footer: Topics and date */}
      <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-neutral-200">
        {/* Topics */}
        <div className="flex flex-wrap gap-1.5 flex-1">
          {order.topic.slice(0, 3).map((topic) => (
            <span
              key={topic}
              className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-neutral-100 text-neutral-700"
            >
              {getTopicLabel(topic)}
            </span>
          ))}
          {order.topic.length > 3 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-neutral-100 text-neutral-700">
              +{order.topic.length - 3} more
            </span>
          )}
          {order.topic.length === 0 && (
            <span className="text-xs text-neutral-500">No topics</span>
          )}
        </div>

        {/* Date */}
        <time
          className="text-xs text-neutral-500 whitespace-nowrap"
          dateTime={order.signing_date}
        >
          {formatDate(order.signing_date)}
        </time>
      </div>
    </Link>
  )
}

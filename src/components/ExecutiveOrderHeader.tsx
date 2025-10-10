import Link from 'next/link'
import { ExecutiveOrder, ExecutiveOrderStatus } from '@/lib/types'

interface ExecutiveOrderHeaderProps {
  order: ExecutiveOrder
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
 * Format date to readable string
 */
function formatDate(isoDate: string): string {
  if (!isoDate) return 'Unknown'

  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function ExecutiveOrderHeader({ order }: ExecutiveOrderHeaderProps) {
  const statusInfo = getStatusInfo(order.status)

  return (
    <section className="bg-gradient-to-br from-primary-800 to-primary-900 text-white py-12">
      <div className="container">
        <div className="max-w-5xl mx-auto">
          {/* Breadcrumb */}
          <nav className="mb-6">
            <ol className="flex items-center space-x-2 text-sm text-primary-200">
              <li>
                <Link href="/" className="hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>/</li>
              <li>
                <Link href="/executive-orders/" className="hover:text-white transition-colors">
                  Executive Orders
                </Link>
              </li>
              <li>/</li>
              <li className="text-white font-medium">EO {order.executive_order_number}</li>
            </ol>
          </nav>

          {/* Header Content */}
          <div className="flex flex-col gap-4">
            {/* EO Number and Status */}
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl md:text-4xl font-bold">
                Executive Order {order.executive_order_number}
              </h1>
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusInfo.color}`}
              >
                {statusInfo.label}
              </span>
            </div>

            {/* Title */}
            <h2 className="text-xl md:text-2xl text-primary-100 font-normal">
              {order.title}
            </h2>

            {/* Metadata Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-6 border-t border-primary-700">
              {/* President */}
              <div>
                <div className="text-sm text-primary-300 mb-1">President</div>
                <div className="text-lg font-semibold">{order.president}</div>
              </div>

              {/* Signing Date */}
              <div>
                <div className="text-sm text-primary-300 mb-1">Signed</div>
                <div className="text-lg font-semibold">
                  {formatDate(order.signing_date)}
                </div>
              </div>

              {/* Publication Date */}
              <div>
                <div className="text-sm text-primary-300 mb-1">Published</div>
                <div className="text-lg font-semibold">
                  {formatDate(order.publication_date)}
                </div>
              </div>
            </div>

            {/* Links */}
            <div className="flex flex-wrap gap-3 mt-4">
              <a
                href={order.html_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary text-sm"
              >
                <svg
                  className="w-4 h-4 inline-block mr-2"
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
                View on Federal Register
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

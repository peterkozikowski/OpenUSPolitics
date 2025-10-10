import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getExecutiveOrderData, getAllExecutiveOrdersFull } from '@/lib/executive-orders'
import ExecutiveOrderHeader from '@/components/ExecutiveOrderHeader'
import ExecutiveOrderTabs from '@/components/ExecutiveOrderTabs'

interface ExecutiveOrderPageProps {
  params: Promise<{
    id: string
  }>
}

/**
 * Generate static params for all executive orders at build time
 */
export async function generateStaticParams() {
  const orders = await getAllExecutiveOrdersFull()

  return orders.map((order) => ({
    id: encodeURIComponent(`EO ${order.executive_order_number}`),
  }))
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({
  params,
}: ExecutiveOrderPageProps): Promise<Metadata> {
  try {
    const { id } = await params
    const order = await getExecutiveOrderData(decodeURIComponent(id))

    return {
      title: `EO ${order.executive_order_number}: ${order.title} | OpenUSPolitics.org`,
      description:
        order.plain_english_summary.length > 160
          ? order.plain_english_summary.slice(0, 157) + '...'
          : order.plain_english_summary,
      keywords: [
        `Executive Order ${order.executive_order_number}`,
        order.president,
        ...order.topic,
        'executive order',
        'presidential action',
      ],
      openGraph: {
        title: `EO ${order.executive_order_number}: ${order.title}`,
        description: order.plain_english_summary.slice(0, 200),
        type: 'article',
        publishedTime: order.signing_date,
        modifiedTime: order.last_updated,
        authors: [order.president],
        siteName: 'OpenUSPolitics.org',
      },
      twitter: {
        card: 'summary_large_image',
        title: `EO ${order.executive_order_number}: ${order.title}`,
        description: order.plain_english_summary.slice(0, 200),
      },
    }
  } catch (error) {
    return {
      title: 'Executive Order Not Found | OpenUSPolitics.org',
      description: 'The requested executive order could not be found.',
    }
  }
}

/**
 * Executive order detail page
 */
export default async function ExecutiveOrderPage({ params }: ExecutiveOrderPageProps) {
  let order

  try {
    const { id } = await params
    // Decode URL-encoded EO number (e.g., "EO%2014110" -> "EO 14110")
    const eoNumber = decodeURIComponent(id)
    order = await getExecutiveOrderData(eoNumber)
  } catch (error) {
    // If order not found, show 404
    notFound()
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Executive Order Header */}
      <ExecutiveOrderHeader order={order} />

      {/* Executive Order Content Tabs */}
      <ExecutiveOrderTabs order={order} />

      {/* AI Transparency Notice */}
      <section className="bg-neutral-100 border-t border-neutral-200 py-8">
        <div className="container">
          <div className="max-w-4xl mx-auto bg-white rounded-lg border border-neutral-300 p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <svg
                  className="w-6 h-6 text-primary-700"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  About This Analysis
                </h3>
                <p className="text-neutral-700 mb-4">
                  This analysis was generated using AI (Claude) and is designed to
                  be strictly non-partisan. All analysis is based solely on the
                  official executive order text from the Federal Register, with full
                  traceability to source documents.
                </p>
                <div className="flex flex-wrap gap-3">
                  <a
                    href="/about"
                    className="text-sm text-primary-700 hover:text-primary-800 font-medium"
                  >
                    Learn about our methodology →
                  </a>
                  <a
                    href={order.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-700 hover:text-primary-800 font-medium"
                  >
                    View original on Federal Register →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

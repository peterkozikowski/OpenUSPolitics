import { Metadata } from 'next'
import { getAllExecutiveOrdersFull } from '@/lib/executive-orders'
import ExecutiveOrderCard from '@/components/ExecutiveOrderCard'

export const metadata: Metadata = {
  title: 'Executive Orders | OpenUSPolitics.org',
  description: 'Presidential executive orders explained in plain English. Non-partisan AI analysis of executive actions from the White House.',
  keywords: [
    'executive orders',
    'presidential orders',
    'White House',
    'presidential actions',
    'federal government',
    'Biden executive orders',
    'Trump executive orders',
  ],
}

export default async function ExecutiveOrdersPage() {
  // Fetch all executive orders at build time for static export
  const orders = await getAllExecutiveOrdersFull()

  // Sort by signing date (most recent first)
  const sortedOrders = orders.sort((a, b) => {
    return new Date(b.signing_date).getTime() - new Date(a.signing_date).getTime()
  })

  // Create summaries for cards
  const orderSummaries = sortedOrders.map((order) => ({
    executive_order_number: order.executive_order_number,
    title: order.title,
    president: order.president,
    signing_date: order.signing_date,
    status: order.status,
    topic: order.topic,
  }))

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-800 to-primary-900 text-white py-16 md:py-24">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-balance">
              Executive Orders in Plain English
            </h1>
            <p className="text-xl md:text-2xl text-primary-100 mb-8 text-balance">
              Presidential executive orders explained without partisan spin or legal jargon.
              AI-powered analysis of White House directives.
            </p>

            {/* Stats */}
            <div className="mt-12 flex flex-wrap justify-center gap-8 text-center">
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {orders.length}
                </div>
                <div className="text-sm text-primary-200 mt-1">
                  Orders Analyzed
                </div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  100%
                </div>
                <div className="text-sm text-primary-200 mt-1">
                  Non-Partisan
                </div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  Free
                </div>
                <div className="text-sm text-primary-200 mt-1">
                  & Open Source
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="container py-8 md:py-12">
        {/* Results Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">
              Recent Executive Orders
            </h2>
            <p className="text-neutral-600 mt-1">
              {orders.length === 0 ? (
                'No executive orders found'
              ) : (
                <>
                  Showing {orders.length} executive {orders.length === 1 ? 'order' : 'orders'}
                </>
              )}
            </p>
          </div>
        </div>

        {/* Executive Order Grid */}
        {orderSummaries.length === 0 ? (
          <div className="text-center py-16">
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
              No executive orders found
            </h3>
            <p className="text-neutral-600 mb-6">
              Executive orders will appear here once they are analyzed
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {orderSummaries.map((order) => (
              <ExecutiveOrderCard key={order.executive_order_number} order={order} />
            ))}
          </div>
        )}
      </section>

      {/* Value Proposition */}
      <section className="bg-white border-t border-neutral-200 py-16">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center text-neutral-900 mb-12">
              Understanding Executive Power
            </h2>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mb-4">
                  <svg
                    className="w-6 h-6 text-primary-800"
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
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  Plain English
                </h3>
                <p className="text-neutral-600">
                  Executive orders translated from legal jargon into clear, accessible language
                </p>
              </div>

              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-accent-100 rounded-lg mb-4">
                  <svg
                    className="w-6 h-6 text-accent-800"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  Impact Analysis
                </h3>
                <p className="text-neutral-600">
                  Understand the real-world effects of presidential directives on citizens and agencies
                </p>
              </div>

              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-neutral-100 rounded-lg mb-4">
                  <svg
                    className="w-6 h-6 text-neutral-800"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  Non-Partisan
                </h3>
                <p className="text-neutral-600">
                  Objective analysis without political bias or editorial spin
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

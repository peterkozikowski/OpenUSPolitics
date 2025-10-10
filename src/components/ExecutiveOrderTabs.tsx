'use client'

import { useState } from 'react'
import { ExecutiveOrder } from '@/lib/types'

interface ExecutiveOrderTabsProps {
  order: ExecutiveOrder
}

type Tab = 'summary' | 'provisions' | 'impact'

export default function ExecutiveOrderTabs({ order }: ExecutiveOrderTabsProps) {
  const [activeTab, setActiveTab] = useState<Tab>('summary')

  const tabs: { id: Tab; label: string; count?: number }[] = [
    { id: 'summary', label: 'Summary' },
    { id: 'provisions', label: 'Key Provisions', count: order.key_provisions.length },
    { id: 'impact', label: 'Practical Impact' },
  ]

  return (
    <section className="container py-8">
      <div className="max-w-5xl mx-auto">
        {/* Tabs Navigation */}
        <div className="border-b border-neutral-200 mb-8">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    activeTab === tab.id
                      ? 'border-primary-800 text-primary-800'
                      : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
                  }
                `}
                aria-current={activeTab === tab.id ? 'page' : undefined}
              >
                {tab.label}
                {tab.count !== undefined && tab.count > 0 && (
                  <span
                    className={`
                      ml-2 py-0.5 px-2 rounded-full text-xs
                      ${
                        activeTab === tab.id
                          ? 'bg-primary-100 text-primary-800'
                          : 'bg-neutral-100 text-neutral-600'
                      }
                    `}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="prose prose-neutral max-w-none">
          {activeTab === 'summary' && (
            <div className="space-y-6">
              <div className="card p-8">
                <h2 className="text-2xl font-bold text-neutral-900 mb-4">
                  Plain English Summary
                </h2>
                <div className="text-neutral-700 leading-relaxed whitespace-pre-wrap">
                  {order.plain_english_summary}
                </div>
              </div>

              {order.abstract && (
                <div className="card p-8 bg-neutral-50">
                  <h3 className="text-lg font-semibold text-neutral-900 mb-3">
                    Official Abstract
                  </h3>
                  <div className="text-neutral-600 text-sm leading-relaxed">
                    {order.abstract}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'provisions' && (
            <div className="card p-8">
              <h2 className="text-2xl font-bold text-neutral-900 mb-6">
                Key Provisions
              </h2>

              {order.key_provisions.length > 0 ? (
                <div className="space-y-4">
                  {order.key_provisions.map((provision, index) => (
                    <div
                      key={index}
                      className="flex gap-4 p-4 bg-neutral-50 rounded-lg border border-neutral-200"
                    >
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-800 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        {index + 1}
                      </div>
                      <div className="flex-1 text-neutral-700 leading-relaxed">
                        {provision}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
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
                    No Provisions Listed
                  </h3>
                  <p className="text-neutral-600">
                    Key provisions analysis is not yet available for this executive order.
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'impact' && (
            <div className="card p-8">
              <h2 className="text-2xl font-bold text-neutral-900 mb-4">
                Practical Impact
              </h2>
              <div className="text-neutral-700 leading-relaxed whitespace-pre-wrap">
                {order.practical_impact}
              </div>

              {/* Additional Info Box */}
              <div className="mt-8 p-6 bg-accent-50 border border-accent-200 rounded-lg">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <svg
                      className="w-6 h-6 text-accent-700"
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
                  <div>
                    <h3 className="text-lg font-semibold text-accent-900 mb-2">
                      Understanding Executive Orders
                    </h3>
                    <p className="text-accent-800 text-sm leading-relaxed">
                      Executive orders are directives issued by the President to manage operations
                      of the federal government. They have the force of law but can be reversed
                      by future presidents or challenged in court.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

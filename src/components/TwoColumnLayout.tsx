'use client'

import { Bill } from '@/lib/types'
import { useTraceability } from '@/hooks/useTraceability'
import TraceableText from './TraceableText'
import SourcePanel from './SourcePanel'

interface TwoColumnLayoutProps {
  bill: Bill
}

/**
 * Two-column layout with traceable summary and source panel
 *
 * This is the core traceability feature that makes OpenUSPolitics unique.
 * The left column shows AI-generated analysis with traceable phrases,
 * and the right column shows the source bill text. When users hover over
 * or click traceable phrases, the corresponding source text is highlighted.
 *
 * @param bill - Complete bill data including provenance links
 */
export default function TwoColumnLayout({ bill }: TwoColumnLayoutProps) {
  const { activePhrase, activeChunk, onPhraseHover, clearHighlight } =
    useTraceability(bill.provenance)

  /**
   * Format currency
   */
  function formatCurrency(amount: number): string {
    if (amount >= 1_000_000_000) {
      return `$${(amount / 1_000_000_000).toFixed(1)}B`
    } else if (amount >= 1_000_000) {
      return `$${(amount / 1_000_000).toFixed(1)}M`
    } else if (amount >= 1_000) {
      return `$${(amount / 1_000).toFixed(1)}K`
    }
    return `$${amount}`
  }

  return (
    <div className="container py-8">
      {/* Introduction banner */}
      <div className="mb-8 p-6 bg-primary-50 border-2 border-primary-200 rounded-lg">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <svg
              className="w-6 h-6 text-white"
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
          <div className="flex-1">
            <h2 className="text-xl font-bold text-primary-900 mb-2">
              Interactive Traceability
            </h2>
            <p className="text-primary-800 mb-3">
              This analysis is fully traceable to the original bill text. Hover over
              any <span className="traceable-text px-1 mx-1">underlined phrase</span>{' '}
              to see the exact source passage it references.
            </p>
            <div className="flex items-center gap-2 text-sm text-primary-700">
              <svg
                className="w-4 h-4"
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
              <span>100% verifiable • No hallucinations</span>
            </div>
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left column: AI Analysis */}
        <div className="space-y-8">
          {/* Plain English Summary */}
          <section>
            <h2 className="text-2xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
              <span className="text-3xl" aria-hidden="true">
                📊
              </span>
              Plain English Summary
            </h2>
            <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
              <TraceableText
                text={bill.plain_english_summary}
                provenance={bill.provenance}
                onPhraseHover={onPhraseHover}
                onPhraseLeave={clearHighlight}
                activePhrase={activePhrase}
              />
            </div>
          </section>

          {/* Key Provisions */}
          <section>
            <h2 className="text-2xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
              <span className="text-3xl" aria-hidden="true">
                📋
              </span>
              Key Provisions
            </h2>
            <div className="bg-white rounded-lg border border-neutral-200 shadow-sm">
              <ul className="divide-y divide-neutral-200">
                {bill.key_provisions.map((provision, index) => (
                  <li key={index} className="p-4 flex gap-3">
                    <span className="flex-shrink-0 w-7 h-7 flex items-center justify-center bg-primary-100 text-primary-800 rounded-full text-sm font-bold">
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <TraceableText
                        text={provision}
                        provenance={bill.provenance}
                        onPhraseHover={onPhraseHover}
                        onPhraseLeave={clearHighlight}
                        activePhrase={activePhrase}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          {/* Practical Impact */}
          <section>
            <h2 className="text-2xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
              <span className="text-3xl" aria-hidden="true">
                👥
              </span>
              What This Means For You
            </h2>
            <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
              <TraceableText
                text={bill.practical_impact}
                provenance={bill.provenance}
                onPhraseHover={onPhraseHover}
                onPhraseLeave={clearHighlight}
                activePhrase={activePhrase}
              />
            </div>
          </section>

          {/* Fiscal Impact */}
          {bill.fiscal_impact && (
            <section>
              <h2 className="text-2xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
                <span className="text-3xl" aria-hidden="true">
                  💰
                </span>
                Fiscal Impact
              </h2>
              <div className="bg-white rounded-lg border border-neutral-200 shadow-sm p-6">
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  {bill.fiscal_impact.cost_estimate !== null && (
                    <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                      <div className="text-sm text-red-700 mb-1 font-medium">
                        Estimated Cost
                      </div>
                      <div className="text-3xl font-bold text-red-600">
                        {formatCurrency(bill.fiscal_impact.cost_estimate)}
                      </div>
                    </div>
                  )}
                  {bill.fiscal_impact.revenue_estimate !== null && (
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="text-sm text-green-700 mb-1 font-medium">
                        Estimated Revenue
                      </div>
                      <div className="text-3xl font-bold text-green-600">
                        {formatCurrency(bill.fiscal_impact.revenue_estimate)}
                      </div>
                    </div>
                  )}
                </div>
                <TraceableText
                  text={bill.fiscal_impact.summary}
                  provenance={bill.provenance}
                  onPhraseHover={onPhraseHover}
                  onPhraseLeave={clearHighlight}
                  activePhrase={activePhrase}
                />
                {bill.fiscal_impact.cbo_score_url && (
                  <a
                    href={bill.fiscal_impact.cbo_score_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 mt-4 text-primary-700 hover:text-primary-800 font-medium"
                  >
                    View CBO Score
                    <svg
                      className="w-4 h-4"
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
                  </a>
                )}
              </div>
            </section>
          )}
        </div>

        {/* Right column: Source panel (sticky) */}
        <div className="hidden lg:block">
          <SourcePanel chunks={bill.source_chunks} activeChunkId={activeChunk} />
        </div>
      </div>

      {/* Mobile source panel (expandable) */}
      <div className="lg:hidden mt-8">
        <details className="bg-white rounded-lg border-2 border-neutral-300">
          <summary className="cursor-pointer p-6 font-semibold text-neutral-900 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-primary-700"
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
              View Source Text
            </span>
            <svg
              className="w-5 h-5 text-neutral-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </summary>
          <div className="border-t border-neutral-300">
            <SourcePanel
              chunks={bill.source_chunks}
              activeChunkId={activeChunk}
            />
          </div>
        </details>
      </div>
    </div>
  )
}

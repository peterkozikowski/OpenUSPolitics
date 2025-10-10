'use client'

import { useState, useEffect } from 'react'
import { Bill, BillTopic } from '@/lib/types'
import StatusTimeline from './StatusTimeline'
import TwoColumnLayout from './TwoColumnLayout'

interface BillTabsProps {
  bill: Bill
}

type TabId = 'analysis' | 'fulltext' | 'timeline' | 'voting' | 'related'

interface Tab {
  id: TabId
  label: string
  icon: string
}

const tabs: Tab[] = [
  { id: 'analysis', label: 'Analysis', icon: '📊' },
  { id: 'fulltext', label: 'Full Text', icon: '📄' },
  { id: 'timeline', label: 'Timeline', icon: '⏱️' },
  { id: 'voting', label: 'Voting', icon: '🗳️' },
  { id: 'related', label: 'Related', icon: '🔗' },
]

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

export default function BillTabs({ bill }: BillTabsProps) {
  const [activeTab, setActiveTab] = useState<TabId>('analysis')

  // Sync with URL hash
  useEffect(() => {
    const hash = window.location.hash.replace('#', '') as TabId
    if (tabs.some((tab) => tab.id === hash)) {
      setActiveTab(hash)
    }
  }, [])

  // Update hash when tab changes
  const handleTabChange = (tabId: TabId) => {
    setActiveTab(tabId)
    window.history.replaceState(null, '', `#${tabId}`)
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target !== document.body) return

      const currentIndex = tabs.findIndex((tab) => tab.id === activeTab)

      if (e.key === 'ArrowLeft' && currentIndex > 0) {
        handleTabChange(tabs[currentIndex - 1]!.id)
      } else if (e.key === 'ArrowRight' && currentIndex < tabs.length - 1) {
        handleTabChange(tabs[currentIndex + 1]!.id)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [activeTab])

  return (
    <div className="container py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Tab Navigation */}
          <div className="border-b border-neutral-200 mb-8">
            <nav
              className="flex gap-2 overflow-x-auto scrollbar-hide -mb-px"
              role="tablist"
              aria-label="Bill information tabs"
            >
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  role="tab"
                  aria-selected={activeTab === tab.id}
                  aria-controls={`panel-${tab.id}`}
                  onClick={() => handleTabChange(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-600 text-primary-700'
                      : 'border-transparent text-neutral-600 hover:text-neutral-900 hover:border-neutral-300'
                  }`}
                >
                  <span className="text-lg" aria-hidden="true">
                    {tab.icon}
                  </span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Panels */}
          <div className="min-h-[400px]">
            {/* Analysis Tab with Interactive Traceability */}
            {activeTab === 'analysis' && (
              <div
                id="panel-analysis"
                role="tabpanel"
                aria-labelledby="tab-analysis"
                className="animate-fadeIn -mx-4 sm:-mx-6 lg:-mx-8"
              >
                <TwoColumnLayout bill={bill} />
              </div>
            )}

            {/* Full Text Tab */}
            {activeTab === 'fulltext' && (
              <div
                id="panel-fulltext"
                role="tabpanel"
                aria-labelledby="tab-fulltext"
                className="animate-fadeIn"
              >
                <div className="bg-white rounded-lg border border-neutral-200 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-neutral-900">
                      Bill Text
                    </h2>
                    <span className="text-sm text-neutral-600">
                      {bill.source_chunks.length} sections
                    </span>
                  </div>
                  <div className="space-y-6 max-h-[600px] overflow-y-auto custom-scrollbar">
                    {bill.source_chunks.map((chunk) => (
                      <div key={chunk.id} className="border-b border-neutral-200 pb-4">
                        <h3 className="text-sm font-semibold text-primary-800 mb-2">
                          {chunk.section}
                        </h3>
                        <p className="text-neutral-700 leading-relaxed font-serif">
                          {chunk.text}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Timeline Tab */}
            {activeTab === 'timeline' && (
              <div
                id="panel-timeline"
                role="tabpanel"
                aria-labelledby="tab-timeline"
                className="animate-fadeIn"
              >
                <div className="bg-white rounded-lg border border-neutral-200 p-6">
                  <h2 className="text-2xl font-bold text-neutral-900 mb-6">
                    Legislative Timeline
                  </h2>
                  <StatusTimeline
                    status={bill.status}
                    introducedDate={bill.introduced_date}
                    lastUpdated={bill.last_updated}
                  />
                </div>
              </div>
            )}

            {/* Voting Tab */}
            {activeTab === 'voting' && (
              <div
                id="panel-voting"
                role="tabpanel"
                aria-labelledby="tab-voting"
                className="animate-fadeIn"
              >
                <div className="bg-white rounded-lg border border-neutral-200 p-6">
                  <h2 className="text-2xl font-bold text-neutral-900 mb-4">
                    Voting Information
                  </h2>
                  <p className="text-neutral-600">
                    Voting data will be available when this bill reaches the floor.
                  </p>
                </div>
              </div>
            )}

            {/* Related Tab */}
            {activeTab === 'related' && (
              <div
                id="panel-related"
                role="tabpanel"
                aria-labelledby="tab-related"
                className="animate-fadeIn"
              >
                <div className="bg-white rounded-lg border border-neutral-200 p-6">
                  <h2 className="text-2xl font-bold text-neutral-900 mb-4">
                    Related Information
                  </h2>
                  <p className="text-neutral-600">
                    Related bills and committee reports coming soon.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar - Quick Facts */}
        <div className="lg:col-span-1">
          <div className="sticky top-8 space-y-6">
            {/* Bill Metadata */}
            <div className="bg-white rounded-lg border border-neutral-200 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                Quick Facts
              </h3>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm text-neutral-600 mb-1">Congress</dt>
                  <dd className="text-sm font-semibold text-neutral-900">
                    {bill.congress}th Congress
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-neutral-600 mb-1">Bill Type</dt>
                  <dd className="text-sm font-semibold text-neutral-900 uppercase">
                    {bill.bill_type}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-neutral-600 mb-1">Topics</dt>
                  <dd className="flex flex-wrap gap-1.5">
                    {bill.topic.map((topic) => (
                      <span
                        key={topic}
                        className="inline-block px-2.5 py-0.5 bg-neutral-100 text-neutral-700 rounded-md text-xs font-medium"
                      >
                        {getTopicLabel(topic)}
                      </span>
                    ))}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-neutral-600 mb-1">Cosponsors</dt>
                  <dd className="text-sm font-semibold text-neutral-900">
                    {bill.cosponsors.length}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Quick Links */}
            <div className="bg-white rounded-lg border border-neutral-200 p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                External Links
              </h3>
              <div className="space-y-3">
                <a
                  href={bill.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-primary-700 hover:text-primary-800"
                >
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
                  Congress.gov
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

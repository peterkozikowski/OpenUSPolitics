'use client'

import { DocumentChunk } from '@/lib/types'

interface SourcePanelProps {
  chunks: DocumentChunk[]
  activeChunkId: string | null
}

/**
 * Source text panel with highlighting
 *
 * Displays the original bill text in chunks, with the ability to highlight
 * specific chunks when the user hovers over traceable phrases in the summary.
 *
 * @param chunks - Array of document chunks to display
 * @param activeChunkId - ID of chunk to highlight
 */
export default function SourcePanel({
  chunks,
  activeChunkId,
}: SourcePanelProps) {
  return (
    <div className="sticky top-8 bg-white rounded-lg border-2 border-neutral-300 overflow-hidden">
      {/* Header */}
      <div className="bg-neutral-100 border-b border-neutral-300 px-6 py-4">
        <h3 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
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
          Source Text
        </h3>
        <p className="text-sm text-neutral-600 mt-1">
          Hover over <span className="traceable-text px-1">blue text</span> to see sources
        </p>
      </div>

      {/* Scrollable content */}
      <div className="max-h-[600px] overflow-y-auto custom-scrollbar px-6 py-4">
        <div className="space-y-6">
          {chunks.map((chunk) => {
            const isActive = activeChunkId === chunk.id

            return (
              <div
                key={chunk.id}
                id={`chunk-${chunk.id}`}
                className={`
                  transition-all duration-300 rounded-lg p-4
                  ${
                    isActive
                      ? 'source-highlight border-2 border-yellow-400 shadow-lg'
                      : 'border border-transparent'
                  }
                `}
              >
                {/* Section header */}
                <div className="text-xs font-semibold text-primary-800 uppercase tracking-wide mb-2">
                  {chunk.section}
                  {chunk.page && ` • Page ${chunk.page}`}
                </div>

                {/* Chunk text */}
                <p className="text-sm text-neutral-700 leading-relaxed font-serif">
                  {chunk.text}
                </p>

                {/* Active indicator */}
                {isActive && (
                  <div className="mt-3 flex items-center gap-2 text-xs text-yellow-800 font-medium">
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
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Referenced in summary
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Footer with count */}
      <div className="bg-neutral-50 border-t border-neutral-300 px-6 py-3">
        <p className="text-xs text-neutral-600">
          {chunks.length} source {chunks.length === 1 ? 'section' : 'sections'}
        </p>
      </div>
    </div>
  )
}

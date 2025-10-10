'use client'

import { useState, useCallback } from 'react'
import { ProvenanceLink } from '@/lib/types'

interface TraceabilityState {
  activePhrase: string | null
  activeChunk: string | null
  onPhraseHover: (phrase: string) => void
  clearHighlight: () => void
  highlightSource: (chunkId: string) => void
}

/**
 * Custom hook for managing traceability interactions
 *
 * Handles state and interactions for the traceability feature, including:
 * - Tracking active phrase and chunk
 * - Highlighting source text on hover
 * - Scrolling to source chunks
 * - Clearing highlights
 *
 * @param provenance - Array of provenance links connecting summary to source
 * @returns Traceability state and handlers
 */
export function useTraceability(provenance: ProvenanceLink[]): TraceabilityState {
  const [activePhrase, setActivePhrase] = useState<string | null>(null)
  const [activeChunk, setActiveChunk] = useState<string | null>(null)

  /**
   * Highlight a source chunk and scroll to it
   */
  const highlightSource = useCallback((chunkId: string) => {
    setActiveChunk(chunkId)

    // Scroll source panel to chunk
    const element = document.getElementById(`chunk-${chunkId}`)
    if (element) {
      element.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      })
    }
  }, [])

  /**
   * Clear all highlights
   */
  const clearHighlight = useCallback(() => {
    setActiveChunk(null)
    setActivePhrase(null)
  }, [])

  /**
   * Handle phrase hover - activate phrase and highlight source
   */
  const onPhraseHover = useCallback(
    (phrase: string) => {
      setActivePhrase(phrase)

      // Find chunk ID for this phrase
      const link = provenance.find((p) => p.summary_phrase === phrase)
      if (link) {
        highlightSource(link.source_chunk_id)
      }
    },
    [provenance, highlightSource]
  )

  return {
    activePhrase,
    activeChunk,
    onPhraseHover,
    clearHighlight,
    highlightSource,
  }
}

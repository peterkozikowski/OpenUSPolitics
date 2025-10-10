'use client'

import React from 'react'
import { ProvenanceLink } from '@/lib/types'

interface TraceableTextProps {
  text: string
  provenance: ProvenanceLink[]
  onPhraseHover: (phrase: string) => void
  onPhraseLeave: () => void
  activePhrase: string | null
}

/**
 * Interactive text component with traceable phrases
 *
 * Splits text into segments where some phrases are linked to source text.
 * When hovering over or clicking a traceable phrase, the corresponding
 * source text is highlighted in the source panel.
 *
 * @param text - The full text to render
 * @param provenance - Links connecting phrases to source chunks
 * @param onPhraseHover - Callback when phrase is hovered
 * @param onPhraseLeave - Callback when hover ends
 * @param activePhrase - Currently active phrase
 */
export default function TraceableText({
  text,
  provenance,
  onPhraseHover,
  onPhraseLeave,
  activePhrase,
}: TraceableTextProps) {
  /**
   * Split text into segments: traceable phrases and regular text
   */
  const renderSegments = () => {
    const segments: React.JSX.Element[] = []
    let lastIndex = 0

    // Sort provenance by position in text to process in order
    const sortedProvenance = [...provenance].sort((a, b) => {
      const posA = text.indexOf(a.summary_phrase, lastIndex)
      const posB = text.indexOf(b.summary_phrase, lastIndex)
      return posA - posB
    })

    sortedProvenance.forEach((link, i) => {
      const phraseStart = text.indexOf(link.summary_phrase, lastIndex)

      // Skip if phrase not found in text
      if (phraseStart === -1) return

      // Add regular text before this phrase
      if (phraseStart > lastIndex) {
        segments.push(
          <span key={`regular-${i}`}>
            {text.slice(lastIndex, phraseStart)}
          </span>
        )
      }

      // Add traceable phrase with interactivity
      const isActive = activePhrase === link.summary_phrase

      segments.push(
        <span
          key={`trace-${i}`}
          className={`
            traceable-text
            ${isActive ? 'bg-primary-100 border-primary-600' : ''}
          `}
          onMouseEnter={() => onPhraseHover(link.summary_phrase)}
          onMouseLeave={onPhraseLeave}
          onClick={() => onPhraseHover(link.summary_phrase)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              onPhraseHover(link.summary_phrase)
            }
          }}
          role="button"
          tabIndex={0}
          aria-label={`View source for: ${link.summary_phrase}`}
        >
          {link.summary_phrase}
        </span>
      )

      lastIndex = phraseStart + link.summary_phrase.length
    })

    // Add remaining text after last phrase
    if (lastIndex < text.length) {
      segments.push(
        <span key="regular-final">{text.slice(lastIndex)}</span>
      )
    }

    return segments
  }

  return (
    <div className="text-lg leading-relaxed text-neutral-800">
      {renderSegments()}
    </div>
  )
}

'use client'

interface ReportIssueButtonProps {
  billNumber?: string
  context?: string
  variant?: 'primary' | 'secondary' | 'outline'
}

/**
 * Button to report issues with bill analysis
 *
 * Opens GitHub issue with pre-filled template including
 * bill number and context for easier issue tracking.
 *
 * @param billNumber - Bill identifier for context
 * @param context - Additional context about the issue
 * @param variant - Button style variant
 */
export default function ReportIssueButton({
  billNumber,
  context,
  variant = 'outline',
}: ReportIssueButtonProps) {
  const handleReport = () => {
    // Create GitHub issue URL with pre-filled template
    const title = billNumber
      ? `Issue with ${billNumber}`
      : 'Issue with OpenUSPolitics.org'

    const body = `
**Bill:** ${billNumber || 'General Issue'}
**Issue Type:**
- [ ] Factual Error
- [ ] Missing Context
- [ ] Perceived Bias
- [ ] Technical Issue
- [ ] Other

**Context:** ${context || 'N/A'}

**Description:**
<!-- Please describe the issue in detail -->

**Expected:**
<!-- What should it say or do instead? -->

**Additional Information:**
<!-- Any other relevant details -->
    `.trim()

    const url = `https://github.com/yourusername/OpenUSPolitics/issues/new?title=${encodeURIComponent(
      title
    )}&body=${encodeURIComponent(body)}&labels=content-issue`

    window.open(url, '_blank', 'noopener,noreferrer')
  }

  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    outline:
      'px-5 py-2.5 bg-white text-neutral-700 border-2 border-neutral-300 rounded-lg font-semibold hover:border-neutral-400 hover:bg-neutral-50 transition-colors',
  }

  return (
    <button
      onClick={handleReport}
      className={`inline-flex items-center gap-2 ${variantClasses[variant]} focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2`}
      aria-label={billNumber ? `Report issue with ${billNumber}` : 'Report issue'}
    >
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      Report Issue
    </button>
  )
}

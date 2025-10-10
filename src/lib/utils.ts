/**
 * Utility functions for OpenUSPolitics.org
 *
 * This module provides helper functions for formatting, styling,
 * and manipulating data throughout the application.
 */

import { BillStatus, Party, BillTopic } from './types'

// ============================================================================
// BILL NUMBER FORMATTING
// ============================================================================

/**
 * Format a bill number for display
 *
 * Ensures consistent formatting with proper spacing and capitalization
 *
 * @param num - Raw bill number
 * @returns Formatted bill number
 *
 * @example
 * formatBillNumber("hr1234") // "H.R. 1234"
 * formatBillNumber("s567") // "S. 567"
 * formatBillNumber("H.R.1234") // "H.R. 1234"
 */
export function formatBillNumber(num: string): string {
  // Remove existing formatting
  const clean = num.replace(/[.\s]/g, '').toUpperCase()

  // Extract bill type and number
  const match = clean.match(/^([A-Z]+)(\d+)$/)
  if (!match) return num

  const [, type = '', number = ''] = match

  // Format based on bill type
  const typeMap: Record<string, string> = {
    HR: 'H.R.',
    S: 'S.',
    HJRES: 'H.J.Res.',
    SJRES: 'S.J.Res.',
    HCONRES: 'H.Con.Res.',
    SCONRES: 'S.Con.Res.',
    HRES: 'H.Res.',
    SRES: 'S.Res.',
  }

  const formattedType = typeMap[type] ?? type
  return `${formattedType} ${number}`
}

/**
 * Get the short bill type (e.g., "HR" from "H.R. 1234")
 *
 * @param billNumber - Full bill number
 * @returns Short bill type
 *
 * @example
 * getBillType("H.R. 1234") // "HR"
 * getBillType("S. 567") // "S"
 */
export function getBillType(billNumber: string): string {
  const match = billNumber.match(/^([A-Z.]+)\s/)
  if (!match || !match[1]) return ''
  return match[1].replace(/\./g, '')
}

// ============================================================================
// DATE FORMATTING
// ============================================================================

/**
 * Format an ISO date string for display
 *
 * @param date - ISO 8601 date string
 * @param format - Format style ('short', 'long', 'relative')
 * @returns Formatted date string
 *
 * @example
 * formatDate("2024-01-15T00:00:00Z") // "Jan 15, 2024"
 * formatDate("2024-01-15T00:00:00Z", "long") // "January 15, 2024"
 * formatDate("2024-01-15T00:00:00Z", "relative") // "3 days ago"
 */
export function formatDate(
  date: string,
  format: 'short' | 'long' | 'relative' = 'short'
): string {
  const d = new Date(date)

  if (format === 'relative') {
    return getRelativeTime(d)
  }

  const options: Intl.DateTimeFormatOptions =
    format === 'long'
      ? { year: 'numeric', month: 'long', day: 'numeric' }
      : { year: 'numeric', month: 'short', day: 'numeric' }

  return d.toLocaleDateString('en-US', options)
}

/**
 * Get relative time string (e.g., "3 days ago")
 *
 * @param date - Date to compare
 * @returns Relative time string
 */
function getRelativeTime(date: Date): string {
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const weeks = Math.floor(days / 7)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)

  if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`
  if (months > 0) return `${months} month${months > 1 ? 's' : ''} ago`
  if (weeks > 0) return `${weeks} week${weeks > 1 ? 's' : ''} ago`
  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'just now'
}

// ============================================================================
// STATUS AND PARTY STYLING
// ============================================================================

/**
 * Get Tailwind CSS color class for bill status
 *
 * @param status - Bill status
 * @returns Tailwind color class name
 *
 * @example
 * getStatusColor("signed") // "green"
 * getStatusColor("vetoed") // "red"
 */
export function getStatusColor(status: BillStatus): string {
  const colorMap: Record<BillStatus, string> = {
    [BillStatus.INTRODUCED]: 'blue',
    [BillStatus.IN_COMMITTEE]: 'yellow',
    [BillStatus.PASSED_HOUSE]: 'purple',
    [BillStatus.PASSED_SENATE]: 'indigo',
    [BillStatus.SIGNED]: 'green',
    [BillStatus.VETOED]: 'red',
    [BillStatus.FAILED]: 'gray',
  }

  return colorMap[status] || 'gray'
}

/**
 * Get display label for bill status
 *
 * @param status - Bill status
 * @returns Human-readable status label
 *
 * @example
 * getStatusLabel("passed_house") // "Passed House"
 */
export function getStatusLabel(status: BillStatus): string {
  const labelMap: Record<BillStatus, string> = {
    [BillStatus.INTRODUCED]: 'Introduced',
    [BillStatus.IN_COMMITTEE]: 'In Committee',
    [BillStatus.PASSED_HOUSE]: 'Passed House',
    [BillStatus.PASSED_SENATE]: 'Passed Senate',
    [BillStatus.SIGNED]: 'Signed into Law',
    [BillStatus.VETOED]: 'Vetoed',
    [BillStatus.FAILED]: 'Failed',
  }

  return labelMap[status] || status
}

/**
 * Get party color for styling
 *
 * @param party - Political party
 * @returns Color name for CSS/Tailwind
 *
 * @example
 * getPartyColor("D") // "blue"
 * getPartyColor("R") // "red"
 */
export function getPartyColor(party: Party): string {
  const colorMap: Record<Party, string> = {
    [Party.DEMOCRAT]: 'blue',
    [Party.REPUBLICAN]: 'red',
    [Party.INDEPENDENT]: 'purple',
  }

  return colorMap[party] || 'gray'
}

/**
 * Get party name
 *
 * @param party - Party code
 * @returns Full party name
 *
 * @example
 * getPartyName("D") // "Democratic"
 */
export function getPartyName(party: Party): string {
  const nameMap: Record<Party, string> = {
    [Party.DEMOCRAT]: 'Democratic',
    [Party.REPUBLICAN]: 'Republican',
    [Party.INDEPENDENT]: 'Independent',
  }

  return nameMap[party] || party
}

// ============================================================================
// TOPIC FORMATTING
// ============================================================================

/**
 * Get display label for bill topic
 *
 * @param topic - Bill topic
 * @returns Human-readable topic label
 *
 * @example
 * getTopicLabel("healthcare") // "Healthcare"
 * getTopicLabel("foreign_policy") // "Foreign Policy"
 */
export function getTopicLabel(topic: BillTopic): string {
  return topic
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Get icon name for topic (for icon libraries like Heroicons)
 *
 * @param topic - Bill topic
 * @returns Icon name
 */
export function getTopicIcon(topic: BillTopic): string {
  const iconMap: Record<BillTopic, string> = {
    [BillTopic.HEALTHCARE]: 'heart',
    [BillTopic.DEFENSE]: 'shield',
    [BillTopic.ECONOMY]: 'currency-dollar',
    [BillTopic.EDUCATION]: 'academic-cap',
    [BillTopic.ENVIRONMENT]: 'globe',
    [BillTopic.INFRASTRUCTURE]: 'truck',
    [BillTopic.IMMIGRATION]: 'users',
    [BillTopic.JUSTICE]: 'scale',
    [BillTopic.TECHNOLOGY]: 'computer-desktop',
    [BillTopic.FOREIGN_POLICY]: 'flag',
    [BillTopic.AGRICULTURE]: 'sparkles',
    [BillTopic.ENERGY]: 'bolt',
    [BillTopic.LABOR]: 'briefcase',
    [BillTopic.SOCIAL_SERVICES]: 'user-group',
    [BillTopic.OTHER]: 'document',
  }

  return iconMap[topic] || 'document'
}

// ============================================================================
// TEXT MANIPULATION
// ============================================================================

/**
 * Truncate text to a maximum length
 *
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @param suffix - Suffix to add when truncated (default: "...")
 * @returns Truncated text
 *
 * @example
 * truncateText("This is a long text", 10) // "This is a..."
 * truncateText("Short", 10) // "Short"
 */
export function truncateText(
  text: string,
  maxLength: number,
  suffix: string = '...'
): string {
  if (text.length <= maxLength) return text

  // Try to break at word boundary
  const truncated = text.slice(0, maxLength - suffix.length)
  const lastSpace = truncated.lastIndexOf(' ')

  if (lastSpace > maxLength * 0.8) {
    return truncated.slice(0, lastSpace) + suffix
  }

  return truncated + suffix
}

/**
 * Extract excerpt from text around a search term
 *
 * @param text - Full text
 * @param searchTerm - Term to highlight
 * @param contextLength - Characters of context on each side
 * @returns Excerpt with context
 *
 * @example
 * extractExcerpt("The bill provides funding...", "funding", 20)
 * // "...bill provides funding for..."
 */
export function extractExcerpt(
  text: string,
  searchTerm: string,
  contextLength: number = 100
): string {
  const index = text.toLowerCase().indexOf(searchTerm.toLowerCase())
  if (index === -1) return truncateText(text, contextLength * 2)

  const start = Math.max(0, index - contextLength)
  const end = Math.min(text.length, index + searchTerm.length + contextLength)

  let excerpt = text.slice(start, end)

  if (start > 0) excerpt = '...' + excerpt
  if (end < text.length) excerpt = excerpt + '...'

  return excerpt
}

/**
 * Highlight search terms in text (returns HTML-safe string)
 *
 * @param text - Text to highlight
 * @param searchTerm - Term to highlight
 * @returns Text with <mark> tags around matches
 */
export function highlightText(text: string, searchTerm: string): string {
  if (!searchTerm) return text

  const regex = new RegExp(`(${escapeRegex(searchTerm)})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * Escape special regex characters
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// ============================================================================
// NUMBER FORMATTING
// ============================================================================

/**
 * Format a number as currency (USD)
 *
 * @param amount - Amount in dollars
 * @param compact - Use compact notation (e.g., "$1.2M")
 * @returns Formatted currency string
 *
 * @example
 * formatCurrency(1234567) // "$1,234,567"
 * formatCurrency(1234567, true) // "$1.2M"
 */
export function formatCurrency(amount: number, compact: boolean = false): string {
  if (compact) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(amount)
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format a large number with commas
 *
 * @param num - Number to format
 * @returns Formatted number string
 *
 * @example
 * formatNumber(1234567) // "1,234,567"
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num)
}

// ============================================================================
// URL HELPERS
// ============================================================================

/**
 * Generate a slug from text (for URLs)
 *
 * @param text - Text to slugify
 * @returns URL-safe slug
 *
 * @example
 * slugify("H.R. 1234 - Healthcare Act") // "hr-1234-healthcare-act"
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

/**
 * Get bill URL path
 *
 * @param billNumber - Bill number
 * @returns URL path for bill page
 *
 * @example
 * getBillUrl("H.R. 1234") // "/bills/hr-1234"
 */
export function getBillUrl(billNumber: string): string {
  const slug = slugify(billNumber)
  return `/bills/${slug}`
}

// ============================================================================
// VALIDATION HELPERS
// ============================================================================

/**
 * Check if a string is a valid bill number format
 *
 * @param str - String to validate
 * @returns True if valid bill number format
 *
 * @example
 * isValidBillNumber("H.R. 1234") // true
 * isValidBillNumber("invalid") // false
 */
export function isValidBillNumber(str: string): boolean {
  const pattern = /^(H\.R\.|S\.|H\.J\.Res\.|S\.J\.Res\.|H\.Con\.Res\.|S\.Con\.Res\.|H\.Res\.|S\.Res\.)\s\d+$/
  return pattern.test(str)
}

/**
 * Check if a string is a valid ISO date
 *
 * @param str - String to validate
 * @returns True if valid ISO date
 */
export function isValidDate(str: string): boolean {
  const date = new Date(str)
  return !isNaN(date.getTime())
}

/**
 * Data access functions for Executive Orders
 *
 * This module provides functions to load and query executive order data from the
 * file system. Data is read from local JSON files and bundled at build time for
 * static export.
 */

import { readFile } from 'fs/promises'
import { join } from 'path'
import {
  ExecutiveOrder,
  ExecutiveOrderMetadata,
  ExecutiveOrderStatus,
  ExecutiveOrderTopic,
} from './types'

// ============================================================================
// CONSTANTS
// ============================================================================

/**
 * Path to data directory (relative to project root)
 */
const DATA_DIR = process.env.NODE_ENV === 'production'
  ? join(process.cwd(), 'pipeline', 'data')
  : join(process.cwd(), 'pipeline', 'data')

/**
 * Path to executive orders directory
 */
const EXECUTIVE_ORDERS_DIR = join(DATA_DIR, 'executive-orders')

/**
 * Path to metadata file
 */
const METADATA_PATH = join(EXECUTIVE_ORDERS_DIR, 'metadata.json')

// ============================================================================
// CORE DATA ACCESS FUNCTIONS
// ============================================================================

/**
 * Get all executive orders metadata (index)
 *
 * @returns Promise resolving to executive orders metadata
 * @throws Error if metadata file cannot be read or is invalid
 *
 * @example
 * const metadata = await getAllExecutiveOrders()
 * console.log(`Total orders: ${metadata.total_orders}`)
 */
export async function getAllExecutiveOrders(): Promise<ExecutiveOrderMetadata> {
  try {
    const content = await readFile(METADATA_PATH, 'utf-8')
    const data = JSON.parse(content)

    // Convert raw metadata to typed structure
    const metadata: ExecutiveOrderMetadata = {
      total_orders: data.total_orders || 0,
      last_updated: data.last_updated || new Date().toISOString(),
      executive_orders: []
    }

    // Load summaries from metadata
    const rawOrders = data.executive_orders || {}
    for (const [eoId, eoData] of Object.entries(rawOrders)) {
      const order = eoData as any
      metadata.executive_orders.push({
        executive_order_number: eoId.replace('EO ', ''),
        title: order.title || '',
        president: order.president || 'Unknown',
        signing_date: order.signing_date || '',
        status: ExecutiveOrderStatus.ACTIVE, // Default to active
        topic: [], // Will be populated from full data if needed
      })
    }

    return metadata
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load executive orders metadata: ${error.message}`)
    }
    throw error
  }
}

/**
 * Get all full executive order objects (for static export with client-side filtering)
 *
 * @returns Promise resolving to array of all executive orders
 * @throws Error if executive orders cannot be loaded
 */
export async function getAllExecutiveOrdersFull(): Promise<ExecutiveOrder[]> {
  try {
    const content = await readFile(METADATA_PATH, 'utf-8')
    const data = JSON.parse(content)

    const rawOrders = data.executive_orders || {}
    const eoNumbers = Object.keys(rawOrders).map(id => id.replace('EO ', ''))

    const orders = await Promise.all(
      eoNumbers.map(async (eoNumber) => {
        try {
          return await getExecutiveOrderData(eoNumber)
        } catch {
          return null
        }
      })
    )

    return orders.filter((o): o is ExecutiveOrder => o !== null)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load executive orders: ${error.message}`)
    }
    throw error
  }
}

/**
 * Get detailed data for a specific executive order
 *
 * @param eoNumber - Executive order number (e.g., "14110" or "EO 14110")
 * @returns Promise resolving to executive order data
 * @throws Error if executive order not found or invalid
 *
 * @example
 * const order = await getExecutiveOrderData("14110")
 * console.log(order.title)
 */
export async function getExecutiveOrderData(eoNumber: string): Promise<ExecutiveOrder> {
  try {
    // Sanitize EO number for filename
    const cleanNumber = eoNumber.replace('EO ', '').replace('EO', '').trim()
    const filename = `EO_${cleanNumber}.json`
    const filepath = join(EXECUTIVE_ORDERS_DIR, filename)

    const content = await readFile(filepath, 'utf-8')
    const rawData = JSON.parse(content)

    // Transform to frontend format with defaults for AI-analyzed fields
    const order: ExecutiveOrder = {
      executive_order_number: rawData.executive_order_number || cleanNumber,
      title: rawData.title || '',
      president: rawData.president || derivePresidentFromDate(rawData.signing_date),
      signing_date: rawData.signing_date || '',
      publication_date: rawData.publication_date || '',
      document_number: rawData.document_number || '',
      status: rawData.status || ExecutiveOrderStatus.ACTIVE,
      topic: rawData.topic || [],
      plain_english_summary: rawData.plain_english_summary || rawData.abstract || 'Summary not yet available.',
      key_provisions: rawData.key_provisions || [],
      practical_impact: rawData.practical_impact || 'Impact analysis not yet available.',
      html_url: rawData.html_url || '',
      full_text_xml_url: rawData.full_text_xml_url || '',
      body_html_url: rawData.body_html_url || '',
      abstract: rawData.abstract || null,
      last_updated: rawData.last_updated || new Date().toISOString(),
      provenance: rawData.provenance || [],
      source_chunks: rawData.source_chunks || [],
    }

    return order
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('ENOENT')) {
        throw new Error(`Executive order not found: ${eoNumber}`)
      }
      throw new Error(`Failed to load executive order ${eoNumber}: ${error.message}`)
    }
    throw error
  }
}

/**
 * Derive president from signing date (approximate)
 *
 * This is a fallback when the API doesn't provide president info.
 */
function derivePresidentFromDate(signingDate: string): string {
  if (!signingDate) return 'Unknown'

  const date = new Date(signingDate)
  const year = date.getFullYear()

  // Approximate presidential terms
  if (year >= 2025) {
    if (date >= new Date('2025-01-20')) return 'Donald Trump'
    return 'Joe Biden'
  } else if (year >= 2021) {
    return 'Joe Biden'
  } else if (year >= 2017) {
    return 'Donald Trump'
  } else if (year >= 2009) {
    return 'Barack Obama'
  } else if (year >= 2001) {
    return 'George W. Bush'
  }

  return 'Unknown'
}

// ============================================================================
// FILTERING AND QUERYING
// ============================================================================

/**
 * Filter options for executive orders
 */
export interface ExecutiveOrderFilterOptions {
  /** Filter by president */
  president?: string | string[]
  /** Filter by topic */
  topic?: ExecutiveOrderTopic | ExecutiveOrderTopic[]
  /** Filter by status */
  status?: ExecutiveOrderStatus | ExecutiveOrderStatus[]
  /** Filter by date range */
  dateRange?: {
    start: string
    end: string
  }
  /** Search query for title/summary */
  search?: string
  /** Sort field */
  sortBy?: 'date' | 'title' | 'president'
  /** Sort order */
  sortOrder?: 'asc' | 'desc'
  /** Pagination limit */
  limit?: number
  /** Pagination offset */
  offset?: number
}

/**
 * Filter executive orders based on provided criteria
 *
 * @param filters - Filter options
 * @returns Promise resolving to filtered executive orders
 *
 * @example
 * const results = await filterExecutiveOrders({
 *   president: 'Joe Biden',
 *   topic: 'healthcare',
 *   limit: 10
 * })
 */
export async function filterExecutiveOrders(
  filters: ExecutiveOrderFilterOptions = {}
): Promise<ExecutiveOrder[]> {
  // Get all orders
  const allOrders = await getAllExecutiveOrdersFull()
  let orders = allOrders

  // Apply president filter
  if (filters.president) {
    const presidents = Array.isArray(filters.president)
      ? filters.president
      : [filters.president]
    orders = orders.filter((order) =>
      presidents.some(p => order.president.toLowerCase().includes(p.toLowerCase()))
    )
  }

  // Apply topic filter
  if (filters.topic) {
    const topics = Array.isArray(filters.topic) ? filters.topic : [filters.topic]
    orders = orders.filter((order) =>
      order.topic.some((t) => topics.includes(t))
    )
  }

  // Apply status filter
  if (filters.status) {
    const statuses = Array.isArray(filters.status)
      ? filters.status
      : [filters.status]
    orders = orders.filter((order) => statuses.includes(order.status))
  }

  // Apply date range filter
  if (filters.dateRange) {
    const start = new Date(filters.dateRange.start)
    const end = new Date(filters.dateRange.end)
    orders = orders.filter((order) => {
      const orderDate = new Date(order.signing_date)
      return orderDate >= start && orderDate <= end
    })
  }

  // Apply search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    orders = orders.filter(
      (order) =>
        order.title.toLowerCase().includes(searchLower) ||
        order.executive_order_number.toLowerCase().includes(searchLower) ||
        order.plain_english_summary.toLowerCase().includes(searchLower)
    )
  }

  // Apply sorting
  const sortBy = filters.sortBy || 'date'
  const sortOrder = filters.sortOrder || 'desc'

  orders.sort((a, b) => {
    let comparison = 0

    switch (sortBy) {
      case 'date':
        comparison =
          new Date(a.signing_date).getTime() -
          new Date(b.signing_date).getTime()
        break
      case 'title':
        comparison = a.title.localeCompare(b.title)
        break
      case 'president':
        comparison = a.president.localeCompare(b.president)
        break
    }

    return sortOrder === 'asc' ? comparison : -comparison
  })

  // Apply pagination
  if (filters.limit || filters.offset) {
    const limit = filters.limit || orders.length
    const offset = filters.offset || 0
    orders = orders.slice(offset, offset + limit)
  }

  return orders
}

/**
 * Search executive orders by text query
 *
 * @param query - Search query
 * @param limit - Maximum results to return
 * @returns Promise resolving to matching executive orders
 *
 * @example
 * const results = await searchExecutiveOrders("artificial intelligence", 10)
 */
export async function searchExecutiveOrders(
  query: string,
  limit: number = 20
): Promise<ExecutiveOrder[]> {
  return filterExecutiveOrders({
    search: query,
    limit,
  })
}

/**
 * Get executive orders by president
 *
 * @param president - President name
 * @param limit - Maximum results to return
 * @returns Promise resolving to executive orders by president
 *
 * @example
 * const bidenOrders = await getExecutiveOrdersByPresident("Joe Biden", 20)
 */
export async function getExecutiveOrdersByPresident(
  president: string,
  limit: number = 20
): Promise<ExecutiveOrder[]> {
  return filterExecutiveOrders({
    president,
    limit,
  })
}

/**
 * Get executive orders by topic
 *
 * @param topic - Executive order topic
 * @param limit - Maximum results to return
 * @returns Promise resolving to executive orders in topic
 *
 * @example
 * const healthcareOrders = await getExecutiveOrdersByTopic("healthcare", 20)
 */
export async function getExecutiveOrdersByTopic(
  topic: ExecutiveOrderTopic,
  limit: number = 20
): Promise<ExecutiveOrder[]> {
  return filterExecutiveOrders({
    topic,
    limit,
  })
}

/**
 * Get recent executive orders
 *
 * @param limit - Maximum results to return
 * @returns Promise resolving to recent executive orders
 *
 * @example
 * const recentOrders = await getRecentExecutiveOrders(10)
 */
export async function getRecentExecutiveOrders(limit: number = 20): Promise<ExecutiveOrder[]> {
  return filterExecutiveOrders({
    sortBy: 'date',
    sortOrder: 'desc',
    limit,
  })
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Check if executive order data exists
 *
 * @param eoNumber - Executive order number
 * @returns Promise resolving to true if order exists
 *
 * @example
 * if (await executiveOrderExists("14110")) {
 *   // Order exists
 * }
 */
export async function executiveOrderExists(eoNumber: string): Promise<boolean> {
  try {
    await getExecutiveOrderData(eoNumber)
    return true
  } catch {
    return false
  }
}

/**
 * Get executive order count by president
 *
 * @returns Promise resolving to president counts
 *
 * @example
 * const counts = await getExecutiveOrderCountsByPresident()
 * console.log(counts['Joe Biden']) // 42
 */
export async function getExecutiveOrderCountsByPresident(): Promise<Record<string, number>> {
  const orders = await getAllExecutiveOrdersFull()

  const counts: Record<string, number> = {}

  orders.forEach((order) => {
    const president = order.president || 'Unknown'
    counts[president] = (counts[president] || 0) + 1
  })

  return counts
}

/**
 * Get executive order count by topic
 *
 * @returns Promise resolving to topic counts
 *
 * @example
 * const counts = await getExecutiveOrderCountsByTopic()
 * console.log(counts.healthcare) // 15
 */
export async function getExecutiveOrderCountsByTopic(): Promise<Record<ExecutiveOrderTopic, number>> {
  const orders = await getAllExecutiveOrdersFull()

  const counts = {} as Record<ExecutiveOrderTopic, number>

  orders.forEach((order) => {
    order.topic.forEach((topic) => {
      counts[topic] = (counts[topic] || 0) + 1
    })
  })

  return counts
}

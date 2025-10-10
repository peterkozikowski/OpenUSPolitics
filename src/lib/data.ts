/**
 * Data access functions for OpenUSPolitics.org
 *
 * This module provides functions to load and query bill data from the
 * file system. In development, data is read from local JSON files. In
 * production (static export), data is bundled at build time.
 */

import { readFile } from 'fs/promises'
import { join } from 'path'
import {
  Bill,
  BillMetadata,
  Representative,
  FilterOptions,
  PaginatedBills,
  BillStatus,
  BillTopic,
} from './types'
import { adaptPipelineBill, adaptPipelineMetadata } from './adapter'

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
 * Path to bills directory
 */
const BILLS_DIR = join(DATA_DIR, 'bills')

/**
 * Path to representatives directory
 */
const REPRESENTATIVES_DIR = join(DATA_DIR, 'representatives')

/**
 * Path to metadata file
 */
const METADATA_PATH = join(DATA_DIR, 'bills', 'metadata.json')

// ============================================================================
// CORE DATA ACCESS FUNCTIONS
// ============================================================================

/**
 * Get all bills metadata (index)
 *
 * @returns Promise resolving to bills metadata
 * @throws Error if metadata file cannot be read or is invalid
 *
 * @example
 * const metadata = await getAllBills()
 * console.log(`Total bills: ${metadata.total_bills}`)
 */
export async function getAllBills(): Promise<BillMetadata> {
  try {
    const content = await readFile(METADATA_PATH, 'utf-8')
    const pipelineData = JSON.parse(content)

    // Load all bill files to create summaries
    const billNumbers = Object.keys(pipelineData.bills || {})
      .filter(num => !num.startsWith('TEST')) // Skip test bills

    const bills = await Promise.all(
      billNumbers.map(async (billNumber) => {
        try {
          return await getBillData(billNumber)
        } catch {
          return null
        }
      })
    )

    const validBills = bills.filter((b): b is Bill => b !== null)

    // Adapt to frontend format
    const metadata = adaptPipelineMetadata(pipelineData, validBills)

    return metadata
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load bills metadata: ${error.message}`)
    }
    throw error
  }
}

/**
 * Get all full bill objects (for static export with client-side filtering)
 *
 * @returns Promise resolving to array of all bills
 * @throws Error if bills cannot be loaded
 */
export async function getAllBillsFull(): Promise<Bill[]> {
  try {
    const content = await readFile(METADATA_PATH, 'utf-8')
    const pipelineData = JSON.parse(content)

    // Load all bill files
    const billNumbers = Object.keys(pipelineData.bills || {})
      .filter(num => !num.startsWith('TEST')) // Skip test bills

    const bills = await Promise.all(
      billNumbers.map(async (billNumber) => {
        try {
          return await getBillData(billNumber)
        } catch {
          return null
        }
      })
    )

    return bills.filter((b): b is Bill => b !== null)
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load bills: ${error.message}`)
    }
    throw error
  }
}

/**
 * Get detailed data for a specific bill
 *
 * @param billNumber - Bill identifier (e.g., "H.R. 1234")
 * @returns Promise resolving to bill data
 * @throws Error if bill not found or invalid
 *
 * @example
 * const bill = await getBillData("H.R. 1234")
 * console.log(bill.title)
 */
export async function getBillData(billNumber: string): Promise<Bill> {
  try {
    // Sanitize bill number for filename
    const filename = sanitizeBillNumber(billNumber) + '.json'
    const filepath = join(BILLS_DIR, filename)

    const content = await readFile(filepath, 'utf-8')
    const pipelineData = JSON.parse(content)

    // Transform pipeline format to frontend format
    const bill = adaptPipelineBill(pipelineData)

    return bill
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('ENOENT')) {
        throw new Error(`Bill not found: ${billNumber}`)
      }
      throw new Error(`Failed to load bill ${billNumber}: ${error.message}`)
    }
    throw error
  }
}

/**
 * Get representative data by ID
 *
 * @param id - Representative identifier
 * @returns Promise resolving to representative data
 * @throws Error if representative not found
 *
 * @example
 * const rep = await getRepresentative("bioguide-A000001")
 * console.log(rep.name)
 */
export async function getRepresentative(id: string): Promise<Representative> {
  try {
    const filename = `${id}.json`
    const filepath = join(REPRESENTATIVES_DIR, filename)

    const content = await readFile(filepath, 'utf-8')
    const data = JSON.parse(content)

    return data as Representative
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('ENOENT')) {
        throw new Error(`Representative not found: ${id}`)
      }
      throw new Error(`Failed to load representative ${id}: ${error.message}`)
    }
    throw error
  }
}

// ============================================================================
// FILTERING AND QUERYING
// ============================================================================

/**
 * Filter bills based on provided criteria
 *
 * @param filters - Filter options
 * @returns Promise resolving to paginated bills
 *
 * @example
 * const results = await filterBills({
 *   status: 'passed_house',
 *   topic: 'healthcare',
 *   limit: 10
 * })
 */
export async function filterBills(
  filters: FilterOptions = {}
): Promise<PaginatedBills> {
  // Get all bills metadata
  const metadata = await getAllBills()
  let bills = metadata.bills

  // Apply status filter
  if (filters.status) {
    const statuses = Array.isArray(filters.status)
      ? filters.status
      : [filters.status]
    bills = bills.filter((bill) => statuses.includes(bill.status))
  }

  // Apply topic filter
  if (filters.topic) {
    const topics = Array.isArray(filters.topic) ? filters.topic : [filters.topic]
    bills = bills.filter((bill) =>
      bill.topic.some((t) => topics.includes(t))
    )
  }

  // Apply party filter
  if (filters.party) {
    const parties = Array.isArray(filters.party) ? filters.party : [filters.party]
    bills = bills.filter((bill) => parties.includes(bill.sponsor_party))
  }

  // Apply date range filter
  if (filters.dateRange) {
    const start = new Date(filters.dateRange.start)
    const end = new Date(filters.dateRange.end)
    bills = bills.filter((bill) => {
      const billDate = new Date(bill.introduced_date)
      return billDate >= start && billDate <= end
    })
  }

  // Apply search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    bills = bills.filter(
      (bill) =>
        bill.title.toLowerCase().includes(searchLower) ||
        bill.bill_number.toLowerCase().includes(searchLower)
    )
  }

  // Apply sorting
  const sortBy = filters.sortBy || 'date'
  const sortOrder = filters.sortOrder || 'desc'

  bills.sort((a, b) => {
    let comparison = 0

    switch (sortBy) {
      case 'date':
        comparison =
          new Date(a.introduced_date).getTime() -
          new Date(b.introduced_date).getTime()
        break
      case 'title':
        comparison = a.title.localeCompare(b.title)
        break
      case 'status':
        comparison = a.status.localeCompare(b.status)
        break
    }

    return sortOrder === 'asc' ? comparison : -comparison
  })

  // Apply pagination
  const limit = filters.limit || 20
  const offset = filters.offset || 0
  const total = bills.length

  const paginatedBills = bills.slice(offset, offset + limit)

  // Load full bill data for paginated results
  const fullBills = await Promise.all(
    paginatedBills.map((summary) => getBillData(summary.bill_number))
  )

  return {
    bills: fullBills,
    total,
    limit,
    offset,
    hasMore: offset + limit < total,
  }
}

/**
 * Search bills by text query
 *
 * @param query - Search query
 * @param limit - Maximum results to return
 * @returns Promise resolving to matching bills
 *
 * @example
 * const results = await searchBills("healthcare reform", 10)
 */
export async function searchBills(
  query: string,
  limit: number = 20
): Promise<Bill[]> {
  const results = await filterBills({
    search: query,
    limit,
  })

  return results.bills
}

/**
 * Get bills by topic
 *
 * @param topic - Bill topic
 * @param limit - Maximum results to return
 * @returns Promise resolving to bills in topic
 *
 * @example
 * const healthcareBills = await getBillsByTopic("healthcare", 20)
 */
export async function getBillsByTopic(
  topic: BillTopic,
  limit: number = 20
): Promise<Bill[]> {
  const results = await filterBills({
    topic,
    limit,
  })

  return results.bills
}

/**
 * Get bills by status
 *
 * @param status - Bill status
 * @param limit - Maximum results to return
 * @returns Promise resolving to bills with status
 *
 * @example
 * const signedBills = await getBillsByStatus("signed", 10)
 */
export async function getBillsByStatus(
  status: BillStatus,
  limit: number = 20
): Promise<Bill[]> {
  const results = await filterBills({
    status,
    limit,
  })

  return results.bills
}

/**
 * Get recent bills
 *
 * @param limit - Maximum results to return
 * @returns Promise resolving to recent bills
 *
 * @example
 * const recentBills = await getRecentBills(10)
 */
export async function getRecentBills(limit: number = 20): Promise<Bill[]> {
  const results = await filterBills({
    sortBy: 'date',
    sortOrder: 'desc',
    limit,
  })

  return results.bills
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Sanitize bill number for use as filename
 *
 * @param billNumber - Bill number (e.g., "H.R. 1234")
 * @returns Sanitized filename
 *
 * @example
 * sanitizeBillNumber("H.R. 1234") // "HR_1234"
 */
function sanitizeBillNumber(billNumber: string): string {
  return billNumber.replace(/\./g, '').replace(/\s+/g, '_')
}

/**
 * Check if bill data exists
 *
 * @param billNumber - Bill identifier
 * @returns Promise resolving to true if bill exists
 *
 * @example
 * if (await billExists("H.R. 1234")) {
 *   // Bill exists
 * }
 */
export async function billExists(billNumber: string): Promise<boolean> {
  try {
    await getBillData(billNumber)
    return true
  } catch {
    return false
  }
}

/**
 * Get bill count by topic
 *
 * @returns Promise resolving to topic counts
 *
 * @example
 * const counts = await getBillCountsByTopic()
 * console.log(counts.healthcare) // 42
 */
export async function getBillCountsByTopic(): Promise<Record<BillTopic, number>> {
  const metadata = await getAllBills()

  const counts = Object.values(BillTopic).reduce(
    (acc, topic) => {
      acc[topic] = 0
      return acc
    },
    {} as Record<BillTopic, number>
  )

  metadata.bills.forEach((bill) => {
    bill.topic.forEach((topic) => {
      counts[topic]++
    })
  })

  return counts
}

/**
 * Get bill count by status
 *
 * @returns Promise resolving to status counts
 *
 * @example
 * const counts = await getBillCountsByStatus()
 * console.log(counts.signed) // 15
 */
export async function getBillCountsByStatus(): Promise<Record<BillStatus, number>> {
  const metadata = await getAllBills()

  const counts = Object.values(BillStatus).reduce(
    (acc, status) => {
      acc[status] = 0
      return acc
    },
    {} as Record<BillStatus, number>
  )

  metadata.bills.forEach((bill) => {
    counts[bill.status]++
  })

  return counts
}

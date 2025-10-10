/**
 * TypeScript type definitions for OpenUSPolitics.org
 *
 * This file contains all type definitions for bills, representatives,
 * and related data structures used throughout the application.
 */

import { z } from 'zod'

// ============================================================================
// ENUMS
// ============================================================================

/**
 * Bill status in the legislative process
 */
export enum BillStatus {
  INTRODUCED = 'introduced',
  IN_COMMITTEE = 'in_committee',
  PASSED_HOUSE = 'passed_house',
  PASSED_SENATE = 'passed_senate',
  SIGNED = 'signed',
  VETOED = 'vetoed',
  FAILED = 'failed',
}

/**
 * Political party affiliation
 */
export enum Party {
  DEMOCRAT = 'D',
  REPUBLICAN = 'R',
  INDEPENDENT = 'I',
}

/**
 * Congressional office
 */
export enum Office {
  HOUSE = 'House',
  SENATE = 'Senate',
}

/**
 * Bill topic categories
 */
export enum BillTopic {
  HEALTHCARE = 'healthcare',
  DEFENSE = 'defense',
  ECONOMY = 'economy',
  EDUCATION = 'education',
  ENVIRONMENT = 'environment',
  INFRASTRUCTURE = 'infrastructure',
  IMMIGRATION = 'immigration',
  JUSTICE = 'justice',
  TECHNOLOGY = 'technology',
  FOREIGN_POLICY = 'foreign_policy',
  AGRICULTURE = 'agriculture',
  ENERGY = 'energy',
  LABOR = 'labor',
  SOCIAL_SERVICES = 'social_services',
  OTHER = 'other',
}

/**
 * Executive order status
 */
export enum ExecutiveOrderStatus {
  ACTIVE = 'active',
  REVOKED = 'revoked',
  AMENDED = 'amended',
  EXPIRED = 'expired',
}

/**
 * Executive order topic categories (uses same categories as bills)
 */
export type ExecutiveOrderTopic = BillTopic

// ============================================================================
// CORE DATA TYPES
// ============================================================================

/**
 * Represents a member of Congress (House or Senate)
 */
export interface Representative {
  /** Unique identifier (e.g., "bioguide-A000001") */
  id: string
  /** Full name */
  name: string
  /** Political party */
  party: Party
  /** Two-letter state code (e.g., "CA") */
  state: string
  /** District number (null for Senators) */
  district: number | null
  /** URL to official photo */
  photo_url: string
  /** Congressional office */
  office: Office
  /** Link to congress.gov profile */
  congress_gov_url: string
}

/**
 * Fiscal impact information for a bill
 */
export interface FiscalImpact {
  /** Estimated cost in USD (null if not available) */
  cost_estimate: number | null
  /** Estimated revenue in USD (null if not available) */
  revenue_estimate: number | null
  /** URL to Congressional Budget Office score */
  cbo_score_url: string | null
  /** Plain English summary of fiscal impact */
  summary: string
}

/**
 * A chunk of bill text with metadata
 */
export interface DocumentChunk {
  /** Unique chunk identifier */
  id: string
  /** Chunk text content */
  text: string
  /** Section number or name (e.g., "SEC. 101") */
  section: string
  /** Starting character position in full document */
  start_char: number
  /** Ending character position in full document */
  end_char: number
  /** Page number (null if not paginated) */
  page: number | null
}

/**
 * Provenance link connecting AI summary to source text
 */
export interface ProvenanceLink {
  /** Phrase from the AI-generated summary */
  summary_phrase: string
  /** ID of the source chunk this phrase references */
  source_chunk_id: string
  /** Character offsets within the source chunk */
  source_offsets: {
    /** Starting character position */
    start: number
    /** Ending character position */
    end: number
  }
}

/**
 * Complete bill data structure
 */
export interface Bill {
  /** Bill identifier (e.g., "H.R. 1234") */
  bill_number: string
  /** Official bill title */
  title: string
  /** Primary sponsor */
  sponsor: Representative
  /** List of co-sponsors */
  cosponsors: Representative[]
  /** Current status in legislative process */
  status: BillStatus
  /** ISO 8601 date when bill was introduced */
  introduced_date: string
  /** ISO 8601 date of last update */
  last_updated: string
  /** Topic categories */
  topic: BillTopic[]
  /** Fiscal impact data (null if not applicable) */
  fiscal_impact: FiscalImpact | null
  /** AI-generated plain English summary */
  plain_english_summary: string
  /** Key provisions extracted from bill */
  key_provisions: string[]
  /** Practical impact on citizens */
  practical_impact: string
  /** URL to bill on congress.gov */
  source_url: string
  /** Provenance links for traceability */
  provenance: ProvenanceLink[]
  /** Source text chunks */
  source_chunks: DocumentChunk[]
  /** Congress number (e.g., 118) */
  congress: number
  /** Bill type (e.g., "hr", "s") */
  bill_type: string
}

/**
 * Simplified bill info for lists and indexes
 */
export interface BillSummary {
  bill_number: string
  title: string
  status: BillStatus
  topic: BillTopic[]
  introduced_date: string
  sponsor_name: string
  sponsor_party: Party
}

/**
 * Metadata index for all bills in the database
 */
export interface BillMetadata {
  /** Total number of bills in database */
  total_bills: number
  /** ISO 8601 timestamp of last update */
  last_updated: string
  /** Array of bill summaries */
  bills: BillSummary[]
}

// ============================================================================
// EXECUTIVE ORDER TYPES
// ============================================================================

/**
 * Complete executive order data structure
 */
export interface ExecutiveOrder {
  /** Executive order number (e.g., "14110") */
  executive_order_number: string
  /** Official title */
  title: string
  /** President who signed the order */
  president: string
  /** ISO 8601 date when order was signed */
  signing_date: string
  /** ISO 8601 date of publication in Federal Register */
  publication_date: string
  /** Federal Register document number */
  document_number: string
  /** Current status */
  status: ExecutiveOrderStatus
  /** Topic categories */
  topic: ExecutiveOrderTopic[]
  /** AI-generated plain English summary */
  plain_english_summary: string
  /** Key provisions extracted from order */
  key_provisions: string[]
  /** Practical impact on citizens and agencies */
  practical_impact: string
  /** URL to Federal Register page */
  html_url: string
  /** URL to full text XML */
  full_text_xml_url: string
  /** URL to full text HTML */
  body_html_url: string
  /** Abstract from Federal Register */
  abstract: string | null
  /** ISO 8601 date of last update */
  last_updated: string
  /** Provenance links for traceability */
  provenance: ProvenanceLink[]
  /** Source text chunks */
  source_chunks: DocumentChunk[]
}

/**
 * Simplified executive order info for lists and indexes
 */
export interface ExecutiveOrderSummary {
  executive_order_number: string
  title: string
  president: string
  signing_date: string
  status: ExecutiveOrderStatus
  topic: ExecutiveOrderTopic[]
}

/**
 * Metadata index for all executive orders in the database
 */
export interface ExecutiveOrderMetadata {
  /** Total number of executive orders in database */
  total_orders: number
  /** ISO 8601 timestamp of last update */
  last_updated: string
  /** Array of executive order summaries */
  executive_orders: ExecutiveOrderSummary[]
}

// ============================================================================
// FILTER AND QUERY TYPES
// ============================================================================

/**
 * Filter options for querying bills
 */
export interface FilterOptions {
  /** Filter by status */
  status?: BillStatus | BillStatus[]
  /** Filter by topic */
  topic?: BillTopic | BillTopic[]
  /** Filter by sponsor party */
  party?: Party | Party[]
  /** Filter by date range */
  dateRange?: {
    start: string
    end: string
  }
  /** Search query for title/summary */
  search?: string
  /** Sort field */
  sortBy?: 'date' | 'title' | 'status'
  /** Sort order */
  sortOrder?: 'asc' | 'desc'
  /** Pagination limit */
  limit?: number
  /** Pagination offset */
  offset?: number
}

/**
 * Paginated response for bill queries
 */
export interface PaginatedBills {
  /** Array of bills */
  bills: Bill[]
  /** Total count (before pagination) */
  total: number
  /** Number of items per page */
  limit: number
  /** Current offset */
  offset: number
  /** Whether there are more results */
  hasMore: boolean
}

// ============================================================================
// ZOD SCHEMAS FOR RUNTIME VALIDATION
// ============================================================================

/**
 * Zod schema for Representative validation
 */
export const RepresentativeSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  party: z.nativeEnum(Party),
  state: z.string().length(2),
  district: z.number().int().nullable(),
  photo_url: z.string().url(),
  office: z.nativeEnum(Office),
  congress_gov_url: z.string().url(),
})

/**
 * Zod schema for FiscalImpact validation
 */
export const FiscalImpactSchema = z.object({
  cost_estimate: z.number().nullable(),
  revenue_estimate: z.number().nullable(),
  cbo_score_url: z.string().url().nullable(),
  summary: z.string(),
})

/**
 * Zod schema for DocumentChunk validation
 */
export const DocumentChunkSchema = z.object({
  id: z.string().min(1),
  text: z.string().min(1),
  section: z.string(),
  start_char: z.number().int().nonnegative(),
  end_char: z.number().int().nonnegative(),
  page: z.number().int().positive().nullable(),
})

/**
 * Zod schema for ProvenanceLink validation
 */
export const ProvenanceLinkSchema = z.object({
  summary_phrase: z.string().min(1),
  source_chunk_id: z.string().min(1),
  source_offsets: z.object({
    start: z.number().int().nonnegative(),
    end: z.number().int().nonnegative(),
  }),
})

/**
 * Zod schema for Bill validation
 */
export const BillSchema = z.object({
  bill_number: z.string().min(1),
  title: z.string().min(1),
  sponsor: RepresentativeSchema,
  cosponsors: z.array(RepresentativeSchema),
  status: z.nativeEnum(BillStatus),
  introduced_date: z.string().datetime(),
  last_updated: z.string().datetime(),
  topic: z.array(z.nativeEnum(BillTopic)),
  fiscal_impact: FiscalImpactSchema.nullable(),
  plain_english_summary: z.string().min(1),
  key_provisions: z.array(z.string().min(1)),
  practical_impact: z.string().min(1),
  source_url: z.string().url(),
  provenance: z.array(ProvenanceLinkSchema),
  source_chunks: z.array(DocumentChunkSchema),
  congress: z.number().int().positive(),
  bill_type: z.string().min(1),
})

/**
 * Zod schema for BillSummary validation
 */
export const BillSummarySchema = z.object({
  bill_number: z.string().min(1),
  title: z.string().min(1),
  status: z.nativeEnum(BillStatus),
  topic: z.array(z.nativeEnum(BillTopic)),
  introduced_date: z.string().datetime(),
  sponsor_name: z.string().min(1),
  sponsor_party: z.nativeEnum(Party),
})

/**
 * Zod schema for BillMetadata validation
 */
export const BillMetadataSchema = z.object({
  total_bills: z.number().int().nonnegative(),
  last_updated: z.string().datetime(),
  bills: z.array(BillSummarySchema),
})

/**
 * Zod schema for ExecutiveOrder validation
 */
export const ExecutiveOrderSchema = z.object({
  executive_order_number: z.string().min(1),
  title: z.string().min(1),
  president: z.string().min(1),
  signing_date: z.string(),
  publication_date: z.string(),
  document_number: z.string().min(1),
  status: z.nativeEnum(ExecutiveOrderStatus),
  topic: z.array(z.nativeEnum(BillTopic)),
  plain_english_summary: z.string().min(1),
  key_provisions: z.array(z.string().min(1)),
  practical_impact: z.string().min(1),
  html_url: z.string().url(),
  full_text_xml_url: z.string().url(),
  body_html_url: z.string().url(),
  abstract: z.string().nullable(),
  last_updated: z.string(),
  provenance: z.array(ProvenanceLinkSchema),
  source_chunks: z.array(DocumentChunkSchema),
})

/**
 * Zod schema for ExecutiveOrderSummary validation
 */
export const ExecutiveOrderSummarySchema = z.object({
  executive_order_number: z.string().min(1),
  title: z.string().min(1),
  president: z.string().min(1),
  signing_date: z.string(),
  status: z.nativeEnum(ExecutiveOrderStatus),
  topic: z.array(z.nativeEnum(BillTopic)),
})

/**
 * Zod schema for ExecutiveOrderMetadata validation
 */
export const ExecutiveOrderMetadataSchema = z.object({
  total_orders: z.number().int().nonnegative(),
  last_updated: z.string(),
  executive_orders: z.array(ExecutiveOrderSummarySchema),
})

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard to check if a value is a valid BillStatus
 */
export function isBillStatus(value: unknown): value is BillStatus {
  return Object.values(BillStatus).includes(value as BillStatus)
}

/**
 * Type guard to check if a value is a valid Party
 */
export function isParty(value: unknown): value is Party {
  return Object.values(Party).includes(value as Party)
}

/**
 * Type guard to check if a value is a valid BillTopic
 */
export function isBillTopic(value: unknown): value is BillTopic {
  return Object.values(BillTopic).includes(value as BillTopic)
}

/**
 * Type guard to check if a value is a valid Bill
 */
export function isBill(value: unknown): value is Bill {
  return BillSchema.safeParse(value).success
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

/**
 * Partial bill for updates
 */
export type PartialBill = Partial<Bill> & Pick<Bill, 'bill_number'>

/**
 * Bill without large fields (for efficient listing)
 */
export type BillWithoutChunks = Omit<Bill, 'source_chunks' | 'provenance'>

/**
 * Type for bill field names (for type-safe filtering/sorting)
 */
export type BillField = keyof Bill

/**
 * Type for valid sort fields
 */
export type SortField = 'date' | 'title' | 'status'

/**
 * Type for sort order
 */
export type SortOrder = 'asc' | 'desc'

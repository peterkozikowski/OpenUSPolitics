/**
 * Data adapter for transforming pipeline output to frontend format
 *
 * This module converts the raw pipeline JSON format into the structured
 * format expected by the Next.js frontend.
 */

import {
  Bill,
  BillStatus,
  BillTopic,
  Representative,
  Party,
  Office,
  FiscalImpact,
  BillSummary,
  BillMetadata
} from './types'

/**
 * Parse sponsor string into Representative object
 * Format: "Rep. Name [Party-State-District]"
 */
function parseSponsor(sponsorString: string): Representative {
  // Example: "Rep. Steil, Bryan [R-WI-1]"
  const match = sponsorString.match(/^(Rep\.|Sen\.) (.+?) \[([RDI])-([A-Z]{2})(?:-(\d+))?\]$/);

  if (!match) {
    // Fallback if parsing fails
    return {
      id: 'unknown',
      name: sponsorString,
      party: Party.INDEPENDENT,
      state: 'XX',
      district: null,
      photo_url: '/images/default-avatar.jpg',
      office: Office.HOUSE,
      congress_gov_url: 'https://www.congress.gov'
    }
  }

  const office = match[1] || 'Rep.'
  const name = match[2] || 'Unknown'
  const party = match[3] || 'I'
  const state = match[4] || 'XX'
  const district = match[5]

  return {
    id: `bioguide-${name.replace(/[^a-zA-Z]/g, '')}`,
    name,
    party: party as Party,
    state,
    district: district ? parseInt(district) : null,
    photo_url: '/images/default-avatar.jpg',
    office: office === 'Sen.' ? Office.SENATE : Office.HOUSE,
    congress_gov_url: 'https://www.congress.gov'
  }
}

/**
 * Map status string to BillStatus enum
 */
function mapStatus(statusString: string): BillStatus {
  const lower = statusString.toLowerCase()

  if (lower.includes('public law') || lower.includes('signed')) {
    return BillStatus.SIGNED
  }
  if (lower.includes('passed house')) {
    return BillStatus.PASSED_HOUSE
  }
  if (lower.includes('passed senate')) {
    return BillStatus.PASSED_SENATE
  }
  if (lower.includes('vetoed')) {
    return BillStatus.VETOED
  }
  if (lower.includes('failed')) {
    return BillStatus.FAILED
  }
  if (lower.includes('committee')) {
    return BillStatus.IN_COMMITTEE
  }

  return BillStatus.INTRODUCED
}

/**
 * Infer topics from bill title (basic keyword matching)
 */
function inferTopics(title: string): BillTopic[] {
  const topics: BillTopic[] = []
  const titleLower = title.toLowerCase()

  const topicMap: Record<string, BillTopic> = {
    'health': BillTopic.HEALTHCARE,
    'medical': BillTopic.HEALTHCARE,
    'medicare': BillTopic.HEALTHCARE,
    'medicaid': BillTopic.HEALTHCARE,
    'defense': BillTopic.DEFENSE,
    'military': BillTopic.DEFENSE,
    'armed forces': BillTopic.DEFENSE,
    'education': BillTopic.EDUCATION,
    'school': BillTopic.EDUCATION,
    'student': BillTopic.EDUCATION,
    'environment': BillTopic.ENVIRONMENT,
    'climate': BillTopic.ENVIRONMENT,
    'pollution': BillTopic.ENVIRONMENT,
    'infrastructure': BillTopic.INFRASTRUCTURE,
    'transportation': BillTopic.INFRASTRUCTURE,
    'highway': BillTopic.INFRASTRUCTURE,
    'immigration': BillTopic.IMMIGRATION,
    'border': BillTopic.IMMIGRATION,
    'justice': BillTopic.JUSTICE,
    'criminal': BillTopic.JUSTICE,
    'court': BillTopic.JUSTICE,
    'technology': BillTopic.TECHNOLOGY,
    'cyber': BillTopic.TECHNOLOGY,
    'data': BillTopic.TECHNOLOGY,
    'foreign': BillTopic.FOREIGN_POLICY,
    'diplomatic': BillTopic.FOREIGN_POLICY,
    'agriculture': BillTopic.AGRICULTURE,
    'farm': BillTopic.AGRICULTURE,
    'energy': BillTopic.ENERGY,
    'power': BillTopic.ENERGY,
    'labor': BillTopic.LABOR,
    'worker': BillTopic.LABOR,
    'employment': BillTopic.LABOR,
    'social security': BillTopic.SOCIAL_SERVICES,
    'welfare': BillTopic.SOCIAL_SERVICES,
    'child': BillTopic.SOCIAL_SERVICES,
    'family': BillTopic.SOCIAL_SERVICES,
  }

  for (const [keyword, topic] of Object.entries(topicMap)) {
    if (titleLower.includes(keyword) && !topics.includes(topic)) {
      topics.push(topic)
    }
  }

  return topics.length > 0 ? topics : [BillTopic.OTHER]
}

/**
 * Parse fiscal impact from pipeline format
 */
function parseFiscalImpact(pipelineData: any): FiscalImpact | null {
  if (!pipelineData.analysis?.fiscal_impact) {
    return null
  }

  const fiscalData = pipelineData.analysis.fiscal_impact

  return {
    cost_estimate: null,
    revenue_estimate: null,
    cbo_score_url: null,
    summary: fiscalData.breakdown || 'No fiscal impact information available'
  }
}

/**
 * Extract congress number and bill type from bill_number
 * Example: "H.R. 9487" -> congress: 118, bill_type: "hr"
 */
function parseBillNumber(billNumber: string): { congress: number, bill_type: string } {
  // Extract bill type
  let billType = 'hr'
  if (billNumber.startsWith('S.')) {
    billType = 's'
  } else if (billNumber.startsWith('H.R.')) {
    billType = 'hr'
  } else if (billNumber.startsWith('H.J.Res.')) {
    billType = 'hjres'
  } else if (billNumber.startsWith('S.J.Res.')) {
    billType = 'sjres'
  }

  // Default to 118th Congress (current as of 2024)
  return { congress: 118, bill_type: billType }
}

/**
 * Transform pipeline bill data to frontend Bill format
 */
export function adaptPipelineBill(pipelineData: any): Bill {
  const sponsor = parseSponsor(pipelineData.sponsor)
  const status = mapStatus(pipelineData.status)
  const topics = inferTopics(pipelineData.title)
  const { congress, bill_type } = parseBillNumber(pipelineData.bill_number)

  return {
    bill_number: pipelineData.bill_number,
    title: pipelineData.title,
    sponsor,
    cosponsors: [], // Not in pipeline data yet
    status,
    introduced_date: pipelineData.introduced_date,
    last_updated: pipelineData._metadata?.saved_at || pipelineData.introduced_date,
    topic: topics,
    fiscal_impact: parseFiscalImpact(pipelineData),
    plain_english_summary: pipelineData.analysis?.plain_english_summary || '',
    key_provisions: pipelineData.analysis?.key_provisions || [],
    practical_impact: pipelineData.analysis?.practical_impact || '',
    source_url: pipelineData.text_url || 'https://www.congress.gov',
    provenance: [], // Not in pipeline data yet
    source_chunks: [], // Not in pipeline data yet
    congress,
    bill_type
  }
}

/**
 * Create BillSummary from Bill
 */
export function createBillSummary(bill: Bill): BillSummary {
  return {
    bill_number: bill.bill_number,
    title: bill.title,
    status: bill.status,
    topic: bill.topic,
    introduced_date: bill.introduced_date,
    sponsor_name: bill.sponsor.name,
    sponsor_party: bill.sponsor.party
  }
}

/**
 * Transform pipeline metadata to frontend format
 */
export function adaptPipelineMetadata(pipelineMetadata: any, billsData: Bill[]): BillMetadata {
  return {
    total_bills: pipelineMetadata.total_bills,
    last_updated: pipelineMetadata.last_updated,
    bills: billsData.map(createBillSummary)
  }
}

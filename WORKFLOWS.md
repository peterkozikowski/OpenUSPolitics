# OpenUSPolitics.org Workflows

This document explains the bill processing workflows and how they work together.

## Overview

The system is split into **two workflows** to separate fast, cheap metadata fetching from expensive AI analysis:

1. **Fetch Bills** - Fast, free, runs daily
2. **AI Analysis** - Slow, expensive, manual only

## Workflow 1: Fetch Bill Metadata

**File**: `.github/workflows/fetch-bills.yml`
**Schedule**: Daily at 1:00 AM UTC
**Duration**: ~2-3 minutes
**Cost**: Free (just API calls)

### What It Does

- Fetches bill metadata from Congress.gov API
- Filters out trivial bills (post office naming)
- Creates lightweight JSON files with basic info:
  - Bill number
  - Title
  - Sponsor
  - Date introduced
  - Current status
  - Text URL
- Updates metadata index
- Commits to git
- **Triggers website deployment automatically**

### Output Format

```json
{
  "bill_number": "H.R. 1234",
  "title": "Infrastructure Investment Act",
  "sponsor": "Rep. Smith, John [D-CA-12]",
  "introduced_date": "2024-01-15",
  "text_url": "https://www.congress.gov/...",
  "bill_version": "Introduced",
  "status": "Referred to Committee",
  "_metadata": {
    "fetched_at": "2024-01-16T01:00:00",
    "source": "Congress.gov API",
    "has_analysis": false
  }
}
```

### Manual Trigger

```bash
# Via GitHub Actions UI
Actions → Fetch Bill Metadata → Run workflow
  - Bill count: 50 (default)

# Via gh CLI
gh workflow run fetch-bills.yml -f bill_count=50
```

## Workflow 2: AI Bill Analysis (Enrichment)

**File**: `.github/workflows/analyze-bills.yml`
**Schedule**: Manual only (no automatic runs)
**Duration**: ~5-10 minutes per bill
**Cost**: ~$0.02-0.05 per bill (Claude API tokens)

### What It Does

- Takes bills created by Workflow 1
- Downloads and parses full bill text
- Chunks text for context management
- Generates semantic embeddings
- Runs Claude AI analysis:
  - Plain English summary
  - Key provisions breakdown
  - Fiscal impact analysis
  - Practical impact for citizens
  - Topic categorization
- Audits for bias
- Enriches existing JSON files
- Commits updated data
- Triggers website deployment

### When to Use

- After Workflow 1 has fetched new bills
- When you want to add analysis to specific bills
- Sparingly (it's expensive!)

### Manual Trigger

```bash
# Via GitHub Actions UI
Actions → AI Bill Analysis → Run workflow
  - Bill count: 5 (default, keep low!)
  - Force update: false (don't re-analyze)

# Via gh CLI
gh workflow run analyze-bills.yml -f bill_count=5
```

## Workflow 3: Deploy to Cloudflare Pages

**File**: `.github/workflows/deploy.yml`
**Triggers**:
- Push to main with changes in `src/`, `pipeline/data/`, or config files
- Repository dispatch event `deploy-site` (from other workflows)
- Manual trigger

### What It Does

- Builds Next.js static site
- Deploys to Cloudflare Pages
- Makes updated bills visible on openuspolitics.org

## How They Work Together

```
┌─────────────────────────────────────────────────────────┐
│  Daily Schedule (1:00 AM UTC)                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Workflow 1: Fetch Bill Metadata                        │
│  - Fetch 50 recent bills from Congress.gov              │
│  - Filter post office bills                             │
│  - Save lightweight JSON                                │
│  - Commit to git                                         │
│  Duration: ~2 minutes                                    │
│  Cost: $0                                                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Workflow 3: Deploy                                      │
│  - Build Next.js site with new bills                     │
│  - Deploy to Cloudflare Pages                            │
│  Duration: ~3 minutes                                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Website Updated!                                        │
│  - Bills visible on openuspolitics.org                   │
│  - No AI analysis yet (just metadata)                    │
└─────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────────┐
        │  Manual: When you want AI analysis  │
        └──────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Workflow 2: AI Analysis (Manual)                        │
│  - Select 5-10 bills to enrich                           │
│  - Parse full bill text                                  │
│  - Run Claude AI analysis                                │
│  - Add analysis to existing JSON                         │
│  - Commit enriched data                                  │
│  Duration: ~10 minutes per bill                          │
│  Cost: ~$0.03 per bill                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Workflow 3: Deploy                                      │
│  - Build Next.js site with enriched bills                │
│  - Deploy to Cloudflare Pages                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Website Updated!                                        │
│  - Bills now have full AI analysis                       │
│  - Summaries, provisions, impact visible                 │
└─────────────────────────────────────────────────────────┘
```

## Benefits of This Approach

### 1. **Fast Website Updates**
- Bills appear on website within 5 minutes
- No waiting for expensive AI analysis
- Users see new legislation immediately

### 2. **Cost Savings**
- Daily fetch: $0
- AI analysis: Only when needed
- No wasted tokens on bills you skip

### 3. **Easier Debugging**
- Test website updates without burning API credits
- Separate concerns (fetch vs. analyze)
- Clear logs for each workflow

### 4. **Flexibility**
- Fetch many bills daily (50+)
- Analyze only the important ones (5-10)
- Re-analyze specific bills if needed

## File Structure

```
pipeline/
  ├── fetch_bills.py          # NEW: Lightweight metadata fetcher
  ├── main.py                  # Full AI analysis pipeline
  ├── data/bills/
  │   ├── metadata.json        # Index of all bills
  │   ├── HR_1234.json         # Bill with metadata only
  │   └── HR_5678.json         # Bill with metadata + AI analysis
  └── logs/
      ├── fetch_bills_*.log    # Fetch workflow logs
      └── pipeline_*.log       # AI analysis logs

.github/workflows/
  ├── fetch-bills.yml          # NEW: Daily metadata fetch
  ├── analyze-bills.yml        # UPDATED: Manual AI analysis
  └── deploy.yml               # UPDATED: Accepts repository_dispatch
```

## Migration Notes

### Before (Old System)
- Single workflow did everything
- Daily AI analysis of all bills
- Expensive ($1-2 per day)
- Slow (30-60 minutes)
- Hard to debug

### After (New System)
- Two workflows, clear separation
- Daily metadata fetch (free, fast)
- AI analysis on demand (controlled cost)
- Easy to test and debug
- Website updates quickly

## Monitoring

### Check Workflow Runs

```bash
# List recent fetch runs
gh run list --workflow fetch-bills.yml --limit 5

# List recent AI analysis runs
gh run list --workflow analyze-bills.yml --limit 5

# List recent deployments
gh run list --workflow deploy.yml --limit 5
```

### Check Bill Counts

```bash
# Total bills
jq '.total_bills' pipeline/data/bills/metadata.json

# Bills with AI analysis
grep -l '"has_analysis": true' pipeline/data/bills/HR_*.json | wc -l

# Bills without AI analysis
grep -l '"has_analysis": false' pipeline/data/bills/HR_*.json | wc -l
```

## Troubleshooting

### Website not updating after fetch?

1. Check if fetch workflow committed changes:
   ```bash
   git log --oneline -5 --grep="metadata"
   ```

2. Check if deploy workflow ran:
   ```bash
   gh run list --workflow deploy.yml --limit 1
   ```

3. Manually trigger deploy:
   ```bash
   gh workflow run deploy.yml
   ```

### Bills missing on website?

Check if they're post office bills (filtered out):
```bash
jq -r '.title' pipeline/data/bills/HR_1234.json | grep -i "post office\|postal service"
```

### AI analysis not working?

1. Check API keys are set in GitHub secrets:
   - `ANTHROPIC_API_KEY`
   - `CONGRESS_GOV_API_KEY`

2. Check workflow logs for errors

3. Try with a single bill first:
   ```bash
   cd pipeline
   python main.py --bill-numbers "H.R. 1234"
   ```

## Best Practices

### Daily Fetch
- ✅ Let it run automatically
- ✅ Fetch 50+ bills to stay current
- ✅ Check logs weekly for issues

### AI Analysis
- ✅ Run manually 1-2 times per week
- ✅ Start with 5 bills at a time
- ✅ Prioritize important/popular legislation
- ✅ Check costs in workflow summary
- ❌ Don't run daily (too expensive)
- ❌ Don't analyze all bills (wasteful)

### Deployment
- ✅ Automatic deployment is fine
- ✅ Monitor for failures
- ✅ Manual trigger if needed

## Future Improvements

Potential enhancements to consider:

1. **Priority Queue**: Flag important bills for automatic AI analysis
2. **Incremental Analysis**: Only re-analyze bills that changed
3. **Cost Tracking**: Dashboard showing API spending
4. **Scheduled AI Analysis**: Weekly enrichment of top N bills
5. **User Requests**: Allow users to request analysis of specific bills

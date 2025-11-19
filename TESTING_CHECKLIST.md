# Testing Checklist for Two-Workflow System

Complete these tests before deploying to production.

## Local Testing

### 1. Test Bill Fetcher Script

```bash
cd pipeline

# Test with a single bill
python fetch_bills.py --bill-numbers "H.R. 4984" --verbose

# Check output
ls -lh data/bills/HR_4984.json
jq '.' data/bills/HR_4984.json | head -20

# Verify structure
jq 'keys' data/bills/HR_4984.json
# Should have: bill_number, title, sponsor, introduced_date, text_url, bill_version, status, _metadata

# Check metadata flag
jq '._metadata.has_analysis' data/bills/HR_4984.json
# Should be: false (no AI analysis yet)
```

**Expected Result:**
- ✅ Bill JSON created/updated
- ✅ No "analysis" field (just metadata)
- ✅ `has_analysis` = false
- ✅ File size small (~500 bytes vs 50KB with analysis)

### 2. Test Post Office Filtering

```bash
cd pipeline

# Test with a post office bill (should be skipped)
python fetch_bills.py --bill-numbers "H.R. 7893" --verbose

# Check logs
# Should see: "Skipping post office naming bill"

# Verify it wasn't saved or updated
git status data/bills/HR_7893.json
```

**Expected Result:**
- ✅ Post office bill skipped
- ✅ Log shows skip reason
- ✅ File not created/updated

### 3. Test Batch Fetching

```bash
cd pipeline

# Fetch 5 recent bills
python fetch_bills.py --bills 5 --verbose

# Check success rate
cat logs/fetch_summary_*.json | tail -1 | jq '.'

# Should show:
# - successful: N bills
# - skipped: M bills (post office)
# - failed: 0 bills
```

**Expected Result:**
- ✅ Multiple bills fetched
- ✅ metadata.json updated
- ✅ Summary file created
- ✅ No failures (unless API issue)

### 4. Test AI Analysis Script Still Works

```bash
cd pipeline

# Test full pipeline with one bill
python main.py --bill-numbers "H.R. 4984" --verbose

# Check output has analysis
jq '.analysis.plain_english_summary' data/bills/HR_4984.json | head -5

# Should see AI-generated summary
```

**Expected Result:**
- ✅ Full analysis added to existing bill
- ✅ File now has `analysis` field
- ✅ File now has `chunks` field with embeddings
- ✅ `has_analysis` = true

## GitHub Actions Testing

### 5. Test Workflow Syntax

```bash
# Validate workflow YAML syntax
yamllint .github/workflows/fetch-bills.yml
yamllint .github/workflows/analyze-bills.yml
yamllint .github/workflows/deploy.yml

# Or use GitHub's built-in validator
gh workflow view fetch-bills.yml
gh workflow view analyze-bills.yml
gh workflow view deploy.yml
```

**Expected Result:**
- ✅ No YAML syntax errors
- ✅ Workflows show up in list

### 6. Test Fetch Bills Workflow (Manual Trigger)

```bash
# Trigger manually with small count
gh workflow run fetch-bills.yml -f bill_count=3

# Wait 2-3 minutes, then check status
gh run list --workflow fetch-bills.yml --limit 1

# View logs
gh run view <run-id> --log

# Check if commit was made
git pull
git log --oneline -1 --grep="metadata"
```

**Expected Result:**
- ✅ Workflow completes successfully
- ✅ New commit with bill metadata
- ✅ No errors in logs
- ✅ Summary shows fetched bills

### 7. Test Deploy Workflow Triggers

**Test A: Push Trigger**

```bash
# Make a small change to trigger deploy
echo "# Test" >> src/app/page.tsx
git add src/app/page.tsx
git commit -m "Test deploy trigger"
git push

# Check if deploy workflow ran
gh run list --workflow deploy.yml --limit 1
```

**Expected Result:**
- ✅ Deploy workflow triggers automatically
- ✅ Build completes successfully
- ✅ Site deploys to Cloudflare Pages

**Test B: Repository Dispatch Trigger**

```bash
# Manually send dispatch event
gh api repos/:owner/:repo/dispatches \
  -f event_type=deploy-site

# Check if deploy workflow ran
gh run list --workflow deploy.yml --limit 1
```

**Expected Result:**
- ✅ Deploy workflow triggers from dispatch
- ✅ Build completes successfully

### 8. Test AI Analysis Workflow (Manual Only)

```bash
# Trigger AI analysis with 1 bill (cheap test)
gh workflow run analyze-bills.yml -f bill_count=1

# Wait 5-10 minutes, then check
gh run list --workflow analyze-bills.yml --limit 1

# View logs
gh run view <run-id> --log

# Check if bill was enriched
git pull
jq '.analysis.plain_english_summary' pipeline/data/bills/HR_*.json | grep -v null | wc -l
# Should increase by 1
```

**Expected Result:**
- ✅ Workflow completes successfully
- ✅ Bill gets AI analysis added
- ✅ Cost shown in summary (~$0.03)
- ✅ New commit with enriched data

### 9. Test Complete Flow End-to-End

```bash
# 1. Fetch bills
gh workflow run fetch-bills.yml -f bill_count=5
# Wait 2 minutes

# 2. Check website
curl -s https://openuspolitics.org | grep -o "Bills Analyzed" -A 2
# Should show increased count

# 3. Run AI analysis on 2 bills
gh workflow run analyze-bills.yml -f bill_count=2
# Wait 10 minutes

# 4. Check website again
# Bills should now have full analysis
```

**Expected Result:**
- ✅ Bills appear quickly after fetch
- ✅ Bills show metadata (no analysis)
- ✅ After AI analysis, bills show summaries
- ✅ Website updates both times

## Production Deployment Checklist

Before deploying to production, ensure:

- [ ] All local tests pass
- [ ] Workflow syntax validated
- [ ] Test runs completed successfully
- [ ] No hardcoded API keys (use secrets)
- [ ] fetch-bills.yml schedule set correctly (1 AM UTC)
- [ ] analyze-bills.yml has NO schedule (manual only)
- [ ] deploy.yml has repository_dispatch trigger
- [ ] WORKFLOWS.md documentation reviewed
- [ ] GitHub secrets configured:
  - [ ] `CONGRESS_GOV_API_KEY`
  - [ ] `ANTHROPIC_API_KEY`
  - [ ] `CLOUDFLARE_API_TOKEN`
  - [ ] `CLOUDFLARE_ACCOUNT_ID`
- [ ] Workflow concurrency groups unique
- [ ] Post office filter working
- [ ] Website displays bills correctly

## Rollback Plan

If something goes wrong:

```bash
# Revert to previous workflow
git revert <commit-hash>
git push

# Or disable new workflows temporarily
gh workflow disable fetch-bills.yml
# Keep using analyze-bills.yml in original form

# Re-enable old workflow if needed
gh workflow enable analyze-bills.yml
```

## Monitoring After Deployment

### First Week

- [ ] Day 1: Check fetch-bills runs successfully
- [ ] Day 2: Verify bills appear on website
- [ ] Day 3: Run AI analysis manually on 5 bills
- [ ] Day 4: Check enriched bills on website
- [ ] Day 5: Review logs for errors
- [ ] Day 6: Check API costs (should be lower)
- [ ] Day 7: Verify everything running smoothly

### Daily Checks

```bash
# Check if daily fetch ran
gh run list --workflow fetch-bills.yml --created ">=$(date -u -d '1 day ago' +%Y-%m-%d)" --limit 1

# Check for failures
gh run list --status failure --limit 5

# Check bill count
jq '.total_bills' pipeline/data/bills/metadata.json
```

## Success Criteria

The migration is successful if:

1. ✅ Daily fetch runs automatically without errors
2. ✅ Bills appear on website within 5 minutes
3. ✅ Manual AI analysis works on-demand
4. ✅ Website shows both metadata-only and analyzed bills
5. ✅ API costs reduced by ~60-80%
6. ✅ No daily AI analysis failures
7. ✅ Deploy workflow triggers correctly
8. ✅ Post office bills filtered out

## Troubleshooting

### Fetch workflow fails
- Check Congress.gov API key
- Check API rate limits
- Review error logs

### Deploy doesn't trigger
- Check repository_dispatch event type matches
- Verify workflow permissions
- Try manual trigger

### AI analysis times out
- Reduce bill count
- Check Claude API key
- Review timeout settings

### Website doesn't update
- Check deploy workflow logs
- Verify Cloudflare credentials
- Check build output

## Notes

- Keep `bill_count` low for AI analysis (5-10 max)
- Fetch workflow is free, run it often
- Monitor costs weekly
- Review skipped bills (post office filter)

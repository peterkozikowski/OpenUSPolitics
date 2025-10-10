# OpenUSPolitics.org Launch Checklist

**Last Updated:** 2025-10-09
**Target Launch:** TBD
**Status:** In Development

---

## 🔴 Critical Path (Minimum Viable Launch)

- [ ] 1. Fix storage bug (git "bytes-like object" error)
- [ ] 2. Analyze initial bills (20-50 recent bills)
- [ ] 3. Connect frontend to data
- [ ] 4. Deploy to Cloudflare Pages
- [ ] 5. Configure custom domain

**Estimated Time:** 4-8 hours

---

## 📋 Detailed Task List

### **Backend/Pipeline** 🔧

- [x] 1.1 Fix git storage "bytes-like object" error in `storage/git_store.py` ✅
  - Location: storage/git_store.py:200, 211, 368, 376
  - Fix: Added `text=True` to subprocess.run() calls
  - Priority: HIGH
  - Time: 15 min
  - Status: COMPLETE

- [ ] 1.2 Run pipeline on initial batch of bills
  - Command: `python main.py --bills 50`
  - Priority: HIGH
  - Estimate: 2-3 hours (with API rate limits)
  - Cost: ~$3.50 (50 bills × $0.07/bill)

- [ ] 1.3 Set up automated pipeline scheduling
  - Option A: Cron job on local/server
  - Option B: GitHub Actions workflow
  - Option C: Cloudflare Workers cron trigger
  - Priority: MEDIUM
  - Estimate: 30 min

- [ ] 1.4 Add production error handling and retry logic
  - Implement exponential backoff for API failures
  - Add error notification system
  - Priority: MEDIUM
  - Estimate: 1 hour

- [ ] 1.5 Configure logging for production monitoring
  - Set up structured logging
  - Configure log levels
  - Priority: LOW
  - Estimate: 30 min

- [ ] 1.6 Optimize vector DB queries if needed
  - Benchmark current performance
  - Add indexes if necessary
  - Priority: LOW
  - Estimate: 1 hour

---

### **Frontend/Data Integration** ⚛️

- [ ] 2.1 Update Next.js app to read from `pipeline/data/bills/*.json`
  - Create data fetching utilities
  - Priority: HIGH
  - Estimate: 30 min

- [ ] 2.2 Create API routes or static data endpoints
  - `/api/bills` - List all bills
  - `/api/bills/[id]` - Get specific bill
  - Priority: HIGH
  - Estimate: 45 min

- [ ] 2.3 Implement bill listing page
  - Show all analyzed bills in grid/list
  - Add sorting (by date, status, etc.)
  - Priority: HIGH
  - Estimate: 1.5 hours

- [ ] 2.4 Implement individual bill detail pages
  - Display full analysis
  - Format provisions, impact, fiscal data
  - Priority: HIGH
  - Estimate: 2 hours

- [ ] 2.5 Add search/filter functionality
  - Search by title, bill number
  - Filter by status, date range
  - Priority: MEDIUM
  - Estimate: 1.5 hours

- [ ] 2.6 Test frontend with real analyzed bill data
  - Manual testing all pages
  - Fix layout/formatting issues
  - Priority: HIGH
  - Estimate: 1 hour

---

### **Cloudflare Deployment** ☁️

- [ ] 3.1 Push code to GitHub repository
  - Create repo if needed
  - Push all code
  - Priority: HIGH
  - Estimate: 15 min

- [ ] 3.2 Set up Cloudflare Pages project
  - Connect GitHub repo
  - Configure project
  - Priority: HIGH
  - Estimate: 15 min

- [ ] 3.3 Configure build settings
  - Build command: `npm run build`
  - Build output: `.next` or `out`
  - Root directory: `/`
  - Node version: 20.x
  - Priority: HIGH
  - Estimate: 10 min

- [ ] 3.4 Set up environment variables (if needed)
  - Add any required env vars to Cloudflare dashboard
  - Priority: MEDIUM
  - Estimate: 5 min

- [ ] 3.5 Configure custom domain
  - Add openuspolitics.org to Cloudflare Pages
  - Update DNS records
  - Priority: HIGH
  - Estimate: 15 min

- [ ] 3.6 Set up SSL/HTTPS
  - Should be automatic with Cloudflare
  - Verify certificate
  - Priority: HIGH
  - Estimate: 5 min (verification only)

---

### **Data Strategy** 💾

- [ ] 4.1 Decide data serving approach
  - ✅ Chosen: Option A - Commit JSON files to git
  - Alternative: R2/KV storage (if files get too large)
  - Priority: HIGH
  - Estimate: Decision only

- [ ] 4.2 Set up data update workflow
  - Document how to refresh analyzed bills
  - Create script for updating production data
  - Priority: MEDIUM
  - Estimate: 30 min

---

### **Production Readiness** 🚀

- [ ] 5.1 Add analytics
  - Cloudflare Web Analytics (free, privacy-friendly)
  - Priority: MEDIUM
  - Estimate: 15 min

- [ ] 5.2 Set up error tracking
  - Option: Sentry, LogRocket, or Cloudflare errors
  - Priority: MEDIUM
  - Estimate: 30 min

- [ ] 5.3 Implement caching strategy
  - Configure Cloudflare CDN caching rules
  - Set cache headers on API routes
  - Priority: MEDIUM
  - Estimate: 20 min

- [ ] 5.4 Add rate limiting if needed
  - Protect API endpoints
  - Priority: LOW
  - Estimate: 20 min

- [ ] 5.5 Security audit
  - Verify no API keys exposed in frontend
  - Check CORS settings
  - Review dependencies for vulnerabilities
  - Priority: HIGH
  - Estimate: 30 min

---

### **Testing & QA** ✅

- [ ] 6.1 End-to-end testing with production data
  - Test all user flows
  - Verify data accuracy
  - Priority: HIGH
  - Estimate: 1 hour

- [ ] 6.2 Performance testing
  - Run Lighthouse audit
  - Target: 90+ performance score
  - Priority: MEDIUM
  - Estimate: 30 min

- [ ] 6.3 Mobile responsiveness testing
  - Test on various screen sizes
  - Fix mobile-specific issues
  - Priority: HIGH
  - Estimate: 45 min

- [ ] 6.4 Cross-browser testing
  - Chrome, Firefox, Safari, Edge
  - Priority: MEDIUM
  - Estimate: 30 min

---

### **Documentation** 📚

- [ ] 7.1 Update README with deployment instructions
  - Add setup guide
  - Document pipeline usage
  - Priority: MEDIUM
  - Estimate: 30 min

- [ ] 7.2 Add CONTRIBUTING.md (if open source)
  - Guidelines for contributors
  - Priority: LOW
  - Estimate: 20 min

- [ ] 7.3 Document data schema and API endpoints
  - API documentation
  - JSON schema reference
  - Priority: MEDIUM
  - Estimate: 30 min

- [ ] 7.4 Create user guide/FAQ section
  - How to use the site
  - Common questions
  - Priority: LOW
  - Estimate: 45 min

---

### **Optional Enhancements** 🎯

- [ ] 8.1 Add RSS feed for new bills
  - Priority: LOW
  - Estimate: 1 hour

- [ ] 8.2 Email notifications for bill updates
  - Priority: LOW
  - Estimate: 2 hours

- [ ] 8.3 Social sharing features
  - Share buttons for Twitter, Facebook
  - Priority: LOW
  - Estimate: 30 min

- [ ] 8.4 Bill comparison tool
  - Compare multiple bills side-by-side
  - Priority: LOW
  - Estimate: 3 hours

- [ ] 8.5 Representative contact information integration
  - Link to congress.gov member pages
  - Priority: LOW
  - Estimate: 1 hour

---

## 📊 Progress Summary

**Total Tasks:** 42
**Completed:** 1
**In Progress:** 1
**Blocked:** 0

**Backend/Pipeline:** 1/6
**Frontend/Data:** 0/6
**Cloudflare:** 0/6
**Data Strategy:** 0/2
**Production:** 0/5
**Testing:** 0/4
**Documentation:** 0/4
**Optional:** 0/5

---

## 🎯 Next Steps

1. **Start with Backend/Pipeline section** (most logical from engineering standpoint)
2. Fix storage bug first
3. Generate initial data
4. Move to frontend integration
5. Deploy

---

## 💰 Cost Estimates

- Initial 50 bills analysis: ~$3.50
- Ongoing (10 new bills/week): ~$0.70/week
- Cloudflare Pages: Free tier (should be sufficient)
- Domain: $12/year (if not already owned)

**Total estimated annual cost:** ~$50-100

---

## 📝 Notes

- Pipeline is fully functional with RAG
- ChromaDB vector database working
- Claude API integrated and tested
- Frontend skeleton exists
- Ready for data integration and deployment

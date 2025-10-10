# OpenUSPolitics.org

[![Deploy to Cloudflare Pages](https://github.com/openuspolitics/openuspolitics.org/actions/workflows/deploy.yml/badge.svg)](https://github.com/openuspolitics/openuspolitics.org/actions/workflows/deploy.yml)
[![Daily Bill Analysis](https://github.com/openuspolitics/openuspolitics.org/actions/workflows/analyze-bills.yml/badge.svg)](https://github.com/openuspolitics/openuspolitics.org/actions/workflows/analyze-bills.yml)
[![Run Tests](https://github.com/openuspolitics/openuspolitics.org/actions/workflows/test.yml/badge.svg)](https://github.com/openuspolitics/openuspolitics.org/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A non-partisan, open-source platform for US political information and civic engagement powered by AI.

## 🌟 Mission

OpenUSPolitics.org provides transparent, accessible, and unbiased analysis of US Congressional bills and political data. Our goal is to empower citizens with factual information without political spin.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│              (Next.js on Cloudflare Pages)                  │
└──────────────────┬────────────────────────────────────────┘
                   │
                   ├─ Static bill pages (SSG)
                   ├─ Interactive traceability UI
                   └─ Cloudflare Pages deployment
                   │
┌──────────────────▼────────────────────────────────────────┐
│                   DATA LAYER                              │
│         Git repository (JSON files)                       │
└──────────────────┬────────────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────────┐
│              AI ANALYSIS PIPELINE                         │
│           (Python + GitHub Actions)                       │
│                                                           │
│  Congress.gov API → Parse → Chunk → Embed →             │
│  RAG Analysis → Claude AI → Bias Audit →                │
│  Store → Commit → Trigger Rebuild                       │
└──────────────────┬────────────────────────────────────────┘
                   │
┌──────────────────▼────────────────────────────────────────┐
│              VECTOR DATABASE                              │
│              ChromaDB (persistent)                        │
└───────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+
- **Python** 3.10+
- **Git**
- **API Keys:**
  - [Congress.gov API](https://api.congress.gov/sign-up/)
  - [Anthropic Claude](https://console.anthropic.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/OpenUSPolitics.org.git
cd OpenUSPolitics.org

# Install frontend dependencies
npm install

# Install Python pipeline dependencies
cd pipeline
pip install -r requirements.txt
cd ..
```

### Configuration

```bash
# 1. Copy environment files
cp .env.example .env.local
cp pipeline/.env.example pipeline/.env

# 2. Add your API keys to both .env files
# Edit .env.local and pipeline/.env with your keys
```

### Run Locally

```bash
# Terminal 1: Run the ETL pipeline
cd pipeline
python main.py --bills 5

# Terminal 2: Run Next.js dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the site.

## 📁 Project Structure

```
OpenUSPolitics.org/
├── src/                        # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/             # React components
│   └── lib/                    # Utilities
│
├── pipeline/                   # Python ETL pipeline
│   ├── main.py                # Orchestrator
│   ├── config.py              # Configuration
│   ├── fetchers/              # Congress.gov API
│   ├── processors/            # Text processing
│   ├── analyzers/             # Claude AI + RAG
│   ├── tracers/               # Provenance tracking
│   ├── storage/               # Data persistence
│   ├── auditing/              # Bias detection
│   └── tests/                 # Unit tests
│
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml         # Cloudflare Pages deployment
│   │   ├── analyze-bills.yml  # Daily ETL pipeline
│   │   └── test.yml           # CI/CD tests
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
│
├── public/                     # Static assets
├── next.config.js             # Next.js config
├── tailwind.config.js         # Tailwind config
└── README.md
```

## 🤖 ETL Pipeline

The Python pipeline automatically:

1. **Fetches** recent bills from Congress.gov API
2. **Parses** bill text (HTML/PDF support)
3. **Chunks** documents for RAG processing
4. **Embeds** text using ChromaDB
5. **Analyzes** bills with Claude AI
6. **Audits** for political bias
7. **Stores** results in JSON with git versioning
8. **Tracks** complete data provenance

### Running the Pipeline

```bash
cd pipeline

# Analyze 10 bills
python main.py --bills 10

# Verbose output
python main.py --bills 5 --verbose

# Run tests
pytest
```

See [pipeline/README.md](pipeline/README.md) for detailed documentation.

## 🌐 Deployment

### Cloudflare Pages (Automatic)

Every push to `main` automatically deploys to Cloudflare Pages via GitHub Actions.

**Required Secrets:**
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

### Manual Deployment

```bash
# Build the site
npm run build

# Deploy to Cloudflare Pages
npm run pages:deploy
```

## 🔄 Automated Workflows

### Daily Bill Analysis
- **Trigger:** 2 AM UTC daily (or manual)
- **Action:** Fetches and analyzes new bills
- **Output:** Commits updated data to repository
- **Result:** Triggers site rebuild

### Continuous Integration
- **Trigger:** Pull requests and pushes to main
- **Tests:** Frontend (TypeScript, ESLint), Backend (pytest, flake8)
- **Security:** npm audit, safety check, Trivy scan

## 🧪 Testing

```bash
# Frontend tests
npm run lint
npm run build  # Type checking

# Backend tests
cd pipeline
pytest -v
flake8 .
black --check .
```

## 🛡️ Quality Assurance

### Non-Partisan Analysis
- Automated bias detection in `pipeline/auditing/bias_audit.py`
- Checks for partisan keywords, opinion language, and emotional content
- Bias score must be < 30 to pass

### Data Provenance
- Complete lineage tracking for all analyses
- Source citations for every claim
- Transparent methodology

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](.github/PULL_REQUEST_TEMPLATE.md).

**Areas we need help:**
- Frontend development (React/Next.js)
- Python pipeline optimization
- Prompt engineering for Claude
- Documentation improvements
- Testing and QA

## 📋 Features

- ✅ Daily automated bill analysis
- ✅ RAG-based AI summarization
- ✅ Bias detection and auditing
- ✅ Complete data provenance
- ✅ Git-based version control
- ✅ Mobile-responsive design
- ✅ Cloudflare Pages hosting
- 🚧 Interactive bill comparison (coming soon)
- 🚧 Representative profiles (coming soon)
- 🚧 Email notifications (coming soon)

## 📊 Tech Stack

**Frontend:**
- Next.js 14+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Cloudflare Pages

**Backend:**
- Python 3.10+
- Anthropic Claude API
- ChromaDB (vector database)
- Congress.gov API v3

**CI/CD:**
- GitHub Actions
- Dependabot
- Automated testing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Analysis Content:** CC BY 4.0

## 🔒 Privacy & Security

- No user tracking or analytics
- No cookies
- Open source for transparency
- Security scans on every PR
- Automated dependency updates

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/openuspolitics/openuspolitics.org/issues)
- **Discussions:** [GitHub Discussions](https://github.com/openuspolitics/openuspolitics.org/discussions)
- **Security:** [Report a vulnerability](https://github.com/openuspolitics/openuspolitics.org/security/advisories/new)

## 🙏 Acknowledgments

- Congress.gov for providing the API
- Anthropic for Claude AI
- Cloudflare for hosting
- Open source community

---

**Made with ❤️ for democracy and transparency**

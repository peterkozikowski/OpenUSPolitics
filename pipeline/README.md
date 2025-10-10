# OpenUSPolitics.org ETL Pipeline

Python-based ETL pipeline for analyzing US Congressional bills using RAG (Retrieval-Augmented Generation) and Claude AI.

## Overview

This pipeline:
1. **Fetches** recent bills from Congress.gov API
2. **Processes** bill text (parsing, chunking, embedding)
3. **Analyzes** bills using Claude with RAG
4. **Audits** analyses for political bias
5. **Stores** results in JSON with git version control
6. **Tracks** complete data provenance

## Architecture

```
pipeline/
├── main.py                 # Orchestrator script
├── config.py               # Configuration management
├── fetchers/              # Data fetching
│   └── congress_api.py    # Congress.gov API client
├── processors/            # Data processing
│   ├── parser.py          # Bill text parser
│   ├── chunker.py         # Document chunker
│   └── embedder.py        # Vector embeddings
├── analyzers/             # AI analysis
│   ├── claude_client.py   # Claude API client
│   ├── rag_engine.py      # RAG implementation
│   └── prompts.py         # Prompt templates
├── tracers/               # Provenance tracking
│   └── provenance.py      # Data lineage tracker
├── storage/               # Data persistence
│   └── git_store.py       # Git-based storage
├── auditing/              # Quality control
│   └── bias_audit.py      # Bias detection
└── tests/                 # Unit tests
    └── test_congress_api.py
```

## Setup

### 1. Install Dependencies

```bash
cd pipeline
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required API keys:
- **CONGRESS_API_KEY**: Get from [Congress.gov API](https://api.congress.gov/sign-up/)
- **ANTHROPIC_API_KEY**: Get from [Anthropic Console](https://console.anthropic.com/)

### 3. Initialize Git (Optional)

```bash
# Initialize git for version control of analyses
cd data
git init
git add .gitkeep
git commit -m "Initialize data repository"
```

## Usage

### Basic Usage

```bash
# Process 10 bills (default)
python main.py

# Process 25 bills
python main.py --bills 25

# Verbose logging
python main.py --verbose
```

### CLI Options

```
Options:
  --bills, -b    Number of bills to process (default: 10)
  --verbose, -v  Enable verbose (DEBUG) logging
  --help, -h     Show help message
```

### Module Usage

```python
# Fetch bills
from fetchers import fetch_recent_bills
bills = fetch_recent_bills(limit=5)

# Parse bill text
from processors import parse_bill_text
text = parse_bill_text(url="https://example.com/bill.pdf")

# Chunk document
from processors import chunk_document
chunks = chunk_document(text, chunk_size=1500, overlap=300)

# Embed and analyze
from processors.embedder import BillEmbedder
from analyzers import RAGEngine

embedder = BillEmbedder()
rag = RAGEngine(embedder=embedder)

embedder.embed_chunks(chunks, "H.R. 1234")
analysis = rag.analyze_bill("H.R. 1234", "Bill Title")
```

## Configuration

Edit `config.py` or `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `BILLS_FETCH_LIMIT` | Number of bills to fetch | 10 |
| `CHUNK_SIZE` | Characters per chunk | 1500 |
| `CHUNK_OVERLAP` | Overlap between chunks | 300 |
| `CLAUDE_MODEL` | Claude model to use | claude-3-5-sonnet-20241022 |
| `GIT_AUTO_COMMIT` | Auto-commit to git | true |
| `LOG_LEVEL` | Logging level | INFO |

## Output

### Data Directory Structure

```
data/
├── bills/                  # Bill analyses (JSON)
│   ├── HR_1234.json
│   ├── S_567.json
│   └── ...
├── metadata.json          # Index of all bills
├── provenance.json        # Complete data lineage
└── chromadb/              # Vector database
```

### Bill Analysis JSON

```json
{
  "bill_number": "H.R. 1234",
  "title": "Example Bill Act of 2024",
  "sponsor": "Rep. Jane Doe",
  "introduced_date": "2024-01-15",
  "status": "Referred to Committee",
  "analysis": "This bill provides...",
  "chunks_count": 25,
  "model": "claude-3-5-sonnet-20241022",
  "tokens": {
    "input": 5000,
    "output": 500
  },
  "bias_audit": {
    "score": 12,
    "passed": true,
    "summary": "Good: Minor issues detected"
  },
  "_metadata": {
    "bill_number": "H.R. 1234",
    "saved_at": "2024-01-20T12:00:00Z",
    "version": 1
  }
}
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_congress_api.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Features

### 1. Data Fetching
- Congress.gov API v3 integration
- Automatic rate limiting
- Retry logic with exponential backoff
- Support for HTML and PDF formats

### 2. Text Processing
- Bill text parsing and cleaning
- Section-aware chunking
- Overlap for context preservation
- Vector embeddings with ChromaDB

### 3. AI Analysis
- RAG-based analysis with Claude
- Non-partisan prompt engineering
- Citation of source sections
- Token usage tracking

### 4. Quality Control
- Automated bias detection
- Partisan language flagging
- Opinion indicator detection
- Balance checking

### 5. Data Management
- JSON storage with git versioning
- Complete provenance tracking
- Metadata indexing
- Automatic commits

## Extending the Pipeline

### Add Custom Prompts

Edit `analyzers/prompts.py`:

```python
CUSTOM_PROMPT = """Your custom prompt here..."""

def format_custom_prompt(bill_number, context):
    return CUSTOM_PROMPT.format(
        bill_number=bill_number,
        context=context
    )
```

### Add Custom Bias Checks

Edit `auditing/bias_audit.py`:

```python
def _check_custom_bias(self, text):
    # Your custom bias detection logic
    issues = []
    # ...
    return issues
```

### Add Custom Storage

Create new module in `storage/`:

```python
def save_to_database(bill_number, data):
    # Your custom storage logic
    pass
```

## Troubleshooting

### API Key Errors
- Verify keys in `.env` file
- Check key permissions
- Ensure `.env` is loaded (not `.env.example`)

### Rate Limiting
- Adjust `CONGRESS_API_RATE_LIMIT` in `.env`
- Reduce `BILLS_FETCH_LIMIT`
- Increase `RETRY_BACKOFF_FACTOR`

### Memory Issues
- Reduce `CHUNK_SIZE`
- Process fewer bills at once
- Use persistent ChromaDB storage

### Git Commit Failures
- Initialize git in data directory
- Set `GIT_AUTO_COMMIT=false` to disable
- Check git configuration

## Development

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Include error handling

### Adding Tests
```python
import pytest
from your_module import your_function

def test_your_function():
    result = your_function(input_data)
    assert result == expected_output
```

## License

[Add License Information]

## Contributing

[Add Contributing Guidelines]

## Support

For issues and questions:
- GitHub Issues: [Repository URL]
- Documentation: [Docs URL]
- Email: [Contact Email]

# DealerFlow Lead Generator - Complete Guide

## Table of Contents
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)

---

## Quick Start

### Prerequisites

- **macOS/Linux/Windows**
- **Python 3.9+**
- **Git**

### Installation (3 Steps)

#### 1. Install Ollama (Local LLM)

**macOS:**
```bash
brew install ollama
ollama pull llama3.1:8b
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

**Windows:**
Download from https://ollama.com/download

Start Ollama:
```bash
ollama serve
```

#### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd EaseVerticalAI
./setup.sh
```

This will:
- Create virtual environment
- Install Python dependencies
- Create `.env` file
- Initialize company context

#### 3. Configure Tavily API Key

Get your free API key: https://tavily.com (1,000 searches/month free)

Add to `.env`:
```bash
TAVILY_API_KEY=tvly-your-key-here
```

### Verify Setup

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python test_setup.py
```

All tests should pass ✅

### Run the App

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## Architecture

### Multi-Agent System

```
User Input (Natural Language)
    ↓
┌─────────────────────────┐
│ Intent Classifier Agent │ → Determines: Customer, Partner, or Both
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Research Agent          │ → Generates search queries, discovers companies
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Enrichment Agent        │ → Gathers company details (website, location, size)
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Scoring Agent           │ → Evaluates fit, generates rationale
└─────────────────────────┘
    ↓
Top 10 Results
```

### Agent Responsibilities

**1. Intent Classifier** ([agents/intent_classifier.py](../agents/intent_classifier.py))
- Classifies user intent: customer, partner, both, or unclear
- Uses structured JSON output
- Tracks confidence and reasoning

**2. Research Agent** ([agents/research_agent.py](../agents/research_agent.py))
- Generates 6-8 targeted search queries
- Executes Tavily AI searches
- Extracts company names
- Filters competitors and duplicates
- Returns ~30 candidate companies

**3. Enrichment Agent** ([agents/enrichment_agent.py](../agents/enrichment_agent.py))
- Searches for company information
- Extracts: website, HQ, locations, size, description
- Uses LLM to structure data

**4. Scoring Agent** ([agents/scoring_agent.py](../agents/scoring_agent.py))
- Evaluates company fit (0-10 score)
- Generates rationale
- Ranks companies
- Returns top 10

**5. Orchestrator** ([orchestrator.py](../orchestrator.py))
- Coordinates agent workflow
- Manages caching
- Returns structured results

### Technology Stack

**LLM:**
- Ollama (local) - Llama 3.1 (8B) or Mistral 7B
- HuggingFace (alternative)

**Search:**
- Tavily AI (AI-optimized search for LLMs)

**UI:**
- Streamlit (web interface)

**Data:**
- JSON caching for repeatability
- Prompt tracing for debugging

---

## Configuration

### Environment Variables

Edit `.env` file:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Search API
TAVILY_API_KEY=your_tavily_key_here

# Application Settings
LOG_LEVEL=INFO
CACHE_RESULTS=true
MAX_COMPANIES_TO_ANALYZE=30
```

### Company Profile

Edit `data/axlewave_context/company_context.json` to customize:
- Company information
- Product details
- Ideal customer profile
- Partner criteria

---

## Usage

### Natural Language Queries

**Find customers:**
```
"Find me 10 automotive dealerships that would buy DealerFlow Cloud"
"Show me large dealer groups in California"
```

**Find partners:**
```
"Find technology partners for vehicle history and valuation"
"Show me companies that offer CRM for dealerships"
```

**Find both:**
```
"Find me both customers and technology partners"
```

### Predefined Queries

Click buttons in the UI:
- Top 10 Potential Customers
- Top 10 Technology Partners
- Both Customers and Partners

### Results

Results are displayed with:
- Company Name
- Website
- Headquarters & Locations
- Size (Small/Medium/Large)
- Fit Score (0-10)
- Rationale
- Key Strengths
- Potential Objections

Results are cached in `data/results_cache/`

---

## Development

### Project Structure

```
EaseVerticalAI/
├── agents/                     # AI agents
│   ├── intent_classifier.py
│   ├── research_agent.py
│   ├── enrichment_agent.py
│   └── scoring_agent.py
├── prompts/                    # LLM prompts
│   ├── intent_classifier.txt
│   ├── partner_discovery.txt
│   ├── partner_scoring.txt
│   ├── customer_discovery.txt
│   └── customer_scoring.txt
├── utils/                      # Utilities
│   ├── llm_client.py          # LLM interface
│   ├── search_client.py       # Tavily search
│   └── prompt_tracer.py       # Prompt logging
├── data/
│   ├── logs/                  # Application logs
│   ├── prompt_logs/           # LLM prompt traces
│   ├── results_cache/         # Cached results
│   └── axlewave_context/      # Company context
├── config/
│   └── settings.py            # Configuration
├── orchestrator.py            # Main orchestrator
├── app.py                     # Streamlit UI
└── test_setup.py             # Setup verification
```

### Logs

**Application logs:** `data/logs/lead_generator.log`
**Prompt traces:** `data/prompt_logs/session_*.jsonl`

View prompt traces:
```python
from utils.prompt_tracer import prompt_tracer
report = prompt_tracer.generate_report()
print(report)
```

### Testing

Run setup verification:
```bash
python test_setup.py
```

Test individual agents:
```bash
python -m agents.intent_classifier
python -m agents.research_agent
```

### Performance

**Typical execution time:**
- Intent classification: 1-2 seconds
- Research (30 companies): 30-60 seconds
- Enrichment (30 companies): 60-90 seconds
- Scoring (30 companies): 30-45 seconds
- **Total: 2-3 minutes for 10 results**

**Optimization:**
- Results are cached
- Parallel search execution
- Smart filtering reduces enrichment calls by 40%

### Customization

**Modify prompts:** Edit files in `prompts/` directory

**Change LLM model:**
```bash
ollama pull mistral:7b
# Update .env: OLLAMA_MODEL=mistral:7b
```

**Adjust scoring:** Edit `prompts/partner_scoring.txt` or `prompts/customer_scoring.txt`

**Add filters:** Modify `agents/research_agent.py` `_should_include_company()`

---

## Troubleshooting

### Ollama Not Running
```bash
ollama serve
# In new terminal:
ollama list  # Should show llama3.1:8b
```

### Tavily API Errors
- Check API key in `.env`
- Verify quota: https://tavily.com/dashboard
- Free tier: 1,000 searches/month

### Poor Results Quality
1. Check `data/logs/lead_generator.log` for errors
2. Review prompt traces in `data/prompt_logs/`
3. Adjust prompts in `prompts/` directory
4. Increase `MAX_COMPANIES_TO_ANALYZE` in `.env`

### Performance Issues
- Use faster model: `ollama pull llama3.1:8b` (vs mixtral)
- Reduce `MAX_COMPANIES_TO_ANALYZE` in `.env`
- Check Ollama is using GPU: `ollama ps`

---

## Tips

**GPU helps:** Ollama will automatically use GPU if available

**Cached results:** Delete `data/results_cache/` to regenerate

**Prompt engineering:** Study `data/prompt_logs/` to optimize prompts

**Model selection:**
- `llama3.1:8b` - Fast, good quality (recommended)
- `mistral:7b` - Alternative
- `mixtral:8x7b` - Slower but higher quality

---

## Need Help?

- Check logs: `data/logs/lead_generator.log`
- Review prompts: `prompts/` directory
- Check cached results: `data/results_cache/`
- Verify setup: `python test_setup.py`

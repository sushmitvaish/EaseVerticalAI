# DealerFlow Cloud - AI Lead Generator

An AI-powered B2B lead generation system that discovers potential customers and technology partners for AxleWave Technologies' DealerFlow Cloud platform.

## 🎯 Overview

This prototype uses **open-source LLMs** (Llama 3.1 / Mistral 7B) and multi-agent architecture to intelligently discover and evaluate:

- **Top 10 Potential Customers**: Automotive dealerships likely to buy DealerFlow Cloud
- **Top 10 Potential Partners**: Technology companies that could integrate with the platform

### Key Features

✅ **Natural Language Interface** - Specify requirements in plain English
✅ **Multi-Agent System** - Specialized AI agents for different tasks
✅ **Open-Source LLMs** - Uses Llama/Mistral via Ollama or HuggingFace
✅ **Free Search APIs** - DuckDuckGo (no API key needed)
✅ **Prompt Tracing** - Track and optimize LLM prompts
✅ **Repeatable Results** - Deterministic prompts and result caching

## 🏗️ Architecture

### Multi-Agent System

```
User Input (Natural Language)
    ↓
┌─────────────────────────┐
│ Intent Classifier Agent │ → Determines: Customer, Partner, or Both
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Orchestrator            │ → Coordinates workflow
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

### Technology Stack

**LLM & AI:**
- **Ollama** (local deployment) or **HuggingFace** API
- Models: Llama 3.1 (8B), Mistral 7B
- **LangChain** for agent orchestration

**Search:**
- **DuckDuckGo Search** (free, no API key)
- Alternatives: Tavily AI, Google Custom Search, Serper

**Backend:**
- Python 3.9+
- FastAPI (API layer)
- Pydantic (data validation)

**Frontend:**
- Streamlit (natural language UI)

**Data & Logging:**
- JSON-based caching
- Prompt tracing with custom logger
- LangFuse integration (optional)

## 📋 Installation

### Prerequisites

1. **Python 3.9+**
2. **Ollama** (recommended) or HuggingFace account

### Step 1: Install Ollama (Local LLM)

**macOS:**
```bash
brew install ollama
ollama pull llama3.1:8b
# OR
ollama pull mistral:7b
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b
```

**Windows:**
Download from [https://ollama.com](https://ollama.com)

### Step 2: Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd EaseVerticalAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and configure:
# - LLM provider (ollama or huggingface)
# - Search provider (duckduckgo, tavily, google, or serper)
# - API keys (if using paid services)
```

**Minimal .env for free tier:**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

SEARCH_PROVIDER=duckduckgo
CACHE_RESULTS=true
```

### Step 4: Initialize Company Context

```bash
python -c "from utils.document_processor import doc_processor; doc_processor.save_context()"
```

## 🚀 Usage

### Option 1: Streamlit UI (Recommended)

```bash
streamlit run app.py
```

Then:
1. Open browser to `http://localhost:8501`
2. Enter your request in natural language:
   - "Find me potential customers"
   - "Who could we partner with?"
   - "Generate both lists"
3. Click "Generate Leads"
4. View and download results

### Option 2: Python API

```python
from orchestrator import orchestrator

# Generate customer leads
results = orchestrator.generate_leads(
    user_input="Find automotive dealerships that need DMS software",
    discovery_type="customer"  # or "partner" or "both"
)

# Access results
customers = results['results']['customers']
for company in customers:
    print(f"{company['company_name']}: {company['fit_score']}/10")
    print(f"Rationale: {company['rationale']}\n")
```

### Option 3: Command Line

```bash
python -m orchestrator "Find me potential customers"
```

## 📊 Output Format

Each discovered company includes:

```json
{
  "company_name": "AutoNation Inc.",
  "website": "https://www.autonation.com",
  "headquarters": "Fort Lauderdale, Florida",
  "locations": ["Nationwide - 300+ locations"],
  "size": "Large",
  "fit_score": 9.5,
  "rationale": "Largest automotive retailer in US with 300+ dealerships...",
  "recommended": true,
  "key_strengths": [
    "Multi-location dealer group",
    "Modern technology focus"
  ]
}
```

## 🧪 Testing

```bash
# Run basic test
python test_workflow.py

# Test individual agents
python -m agents.intent_classifier
python -m agents.research_agent
```

## 📁 Project Structure

```
EaseVerticalAI/
├── agents/                      # AI Agent implementations
│   ├── intent_classifier.py    # Classifies user intent
│   ├── research_agent.py        # Discovers companies via search
│   ├── enrichment_agent.py      # Enriches company details
│   └── scoring_agent.py         # Scores and ranks companies
├── utils/                       # Utility modules
│   ├── llm_client.py           # Open-source LLM client
│   ├── search_client.py        # Multi-provider search client
│   ├── document_processor.py   # Process AxleWave docs
│   └── prompt_tracer.py        # Prompt logging & tracing
├── prompts/                     # LLM prompt templates
│   ├── intent_classifier.txt
│   ├── customer_discovery.txt
│   ├── partner_discovery.txt
│   ├── company_extraction.txt
│   ├── company_enrichment.txt
│   ├── customer_scoring.txt
│   └── partner_scoring.txt
├── config/                      # Configuration
│   └── settings.py             # App settings
├── data/                        # Data storage
│   ├── axlewave_context/       # Company context
│   ├── results_cache/          # Cached results
│   └── prompt_logs/            # Prompt traces
├── orchestrator.py              # Main agent coordinator
├── app.py                       # Streamlit UI
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
└── README.md                    # This file
```

## 🔧 Configuration

### LLM Providers

**Ollama (Local - Recommended):**
```bash
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b  # or mistral:7b, mixtral:8x7b
```

**HuggingFace (Cloud):**
```bash
LLM_PROVIDER=huggingface
HUGGINGFACE_API_TOKEN=your_token
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Search Providers

**DuckDuckGo (Free, No API Key):**
```bash
SEARCH_PROVIDER=duckduckgo
```

**Tavily (1000 free requests/month):**
```bash
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_key
```

**Google Custom Search (100 free/day):**
```bash
SEARCH_PROVIDER=google
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_cse_id
```

## 📈 Performance

**Typical Execution Times:**
- Intent Classification: 2-5 seconds
- Research (discovering 30 companies): 30-60 seconds
- Enrichment (30 companies): 60-120 seconds
- Scoring (30 companies): 60-90 seconds

**Total: ~3-5 minutes** for complete workflow (both customers and partners)

**Optimizations:**
- Result caching for repeated queries
- Parallel search execution
- Temperature=0 for deterministic outputs

## 🎓 Prompt Engineering

### Strategies Used

1. **Structured Output**: JSON mode for consistent responses
2. **Few-Shot Learning**: Examples in prompts for better results
3. **Chain of Thought**: LLM explains reasoning
4. **Prompt Templates**: Reusable, documented prompts
5. **Tracing**: Log all prompts for optimization

### View Prompt Traces

```python
from utils.prompt_tracer import prompt_tracer
report = prompt_tracer.generate_report()
print(report)
```

## 🚢 Deployment Considerations

### For Production:

**Security:**
- [ ] Environment variable management (AWS Secrets Manager, etc.)
- [ ] API authentication and rate limiting
- [ ] Input validation and sanitization
- [ ] HTTPS only

**Scalability:**
- [ ] Horizontal scaling with load balancer
- [ ] Redis for distributed caching
- [ ] Message queue for async processing (Celery + RabbitMQ)
- [ ] Database for persistent storage (PostgreSQL)

**Performance:**
- [ ] GPU acceleration for local LLMs
- [ ] CDN for static assets
- [ ] Search result caching
- [ ] Batch processing for multiple requests

**Monitoring:**
- [ ] Application logging (ELK stack)
- [ ] Performance metrics (Prometheus + Grafana)
- [ ] Error tracking (Sentry)
- [ ] LLM cost tracking

**AI Enhancements:**
- [ ] Fine-tune LLM on domain data
- [ ] Implement retrieval-augmented generation (RAG)
- [ ] Add feedback loop for continuous improvement
- [ ] A/B test different prompts

## 📝 License

This project is the property of Ease Vertical AI, Inc. © 2025

## 🤝 Contributing

This is a take-home assignment submission. Not accepting external contributions.

## 📧 Contact

For questions: engage@easeverticalai.com

---

**Built using Open-Source LLMs**

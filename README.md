# DealerFlow Cloud - AI Lead Generator

An AI-powered B2B lead generation system that discovers potential customers and technology partners for automotive dealership management systems.

## 🎯 What It Does

Uses **open-source LLMs** (Mistral 7B / Llama 3.1) and multi-agent architecture to intelligently discover and evaluate:

- **Top 10 Potential Customers**: Automotive dealerships likely to buy DealerFlow Cloud
- **Top 10 Potential Partners**: Technology companies that could integrate with the platform

## ✨ Key Features

✅ **Natural Language Interface** - Specify requirements in plain English
✅ **Multi-Agent System** - 5 specialized AI agents working together
✅ **Open-Source LLMs** - Mistral 7B / Llama 3.1 via Ollama
✅ **AI-Optimized Search** - Tavily API (1,000 free searches/month)
✅ **Prompt Tracing** - Track and optimize LLM interactions
✅ **Smart Filtering** - Parent/subsidiary detection, competitor exclusion
✅ **Repeatable Results** - Deterministic prompts and result caching

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Ollama (local LLM runtime)

### Installation

```bash
# 1. Install Ollama
brew install ollama  # macOS
ollama pull mistral:7b

# To run if already installed
ollama serve

# 2. Clone and setup
git clone <your-repo-url>
cd EaseVerticalAI
./setup.sh

# 3. Add Tavily API key to .env
TAVILY_API_KEY=your_key_here  # Get free key at https://tavily.com

# 4. Run the app
streamlit run app.py
```

Open browser to `http://localhost:8501`

**See [Complete Guide](docs/GUIDE.md) for detailed setup instructions**

## 🏗️ Architecture

### Multi-Agent System

```
User Input (Natural Language)
    ↓
┌─────────────────────────┐
│ Intent Classifier Agent │ → Customer / Partner / Both?
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Research Agent          │ → Generate queries, search, filter
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Enrichment Agent        │ → Gather company details
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Scoring Agent           │ → Evaluate fit, rank results
└─────────────────────────┘
    ↓
Top 10 Results (JSON)
```

### Technology Stack

- **LLM**: Ollama (Mistral 7B / Llama 3.1 8B)
- **Search**: Tavily AI (AI-optimized for LLMs)
- **UI**: Streamlit
- **Language**: Python 3.9+
- **Caching**: JSON-based results cache

See data/results_cache/ for complete results.

## 📁 Project Structure

```
EaseVerticalAI/
├── agents/                     # AI agents
│   ├── intent_classifier.py   # Classify user intent
│   ├── research_agent.py      # Discover companies
│   ├── enrichment_agent.py    # Gather details
│   └── scoring_agent.py       # Evaluate & rank
├── prompts/                    # LLM prompts
│   ├── partner_discovery.txt
│   ├── partner_scoring.txt
│   ├── customer_discovery.txt
│   └── customer_scoring.txt
├── utils/
│   ├── llm_client.py          # Ollama interface
│   ├── search_client.py       # Tavily search
│   └── prompt_tracer.py       # Prompt logging
├── data/
│   ├── logs/                  # Application logs
│   ├── prompt_logs/           # LLM traces
│   ├── results_cache/         # Cached results
│   └── axlewave_context/      # Company context
├── docs/
│   └── GUIDE.md              # Complete guide
├── orchestrator.py            # Main orchestrator
├── app.py                     # Streamlit UI
└── README.md                  # This file
```

## 🎮 Usage

### Natural Language Queries

```
"Find me 10 automotive dealerships that would buy DealerFlow Cloud"
"Show me technology partners for vehicle history and valuation"
"Find me both customers and partners"
```

### Predefined Queries

Use buttons in the Streamlit UI:
- **Top 10 Potential Customers** - Find dealer groups
- **Top 10 Technology Partners** - Find integration partners
- **Both Customers and Partners** - Combined search

## 🔧 Configuration

Edit `.env` file:

```bash
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# Search
TAVILY_API_KEY=your_key_here

# Settings
LOG_LEVEL=INFO
CACHE_RESULTS=true
MAX_COMPANIES_TO_ANALYZE=30
```

Customize company profile: `data/axlewave_context/company_context.json`

## 🎯 Key Features Explained

### Smart Filtering
- **Parent/subsidiary detection**: "AutoNation Inc." filters out "AutoNation Honda Chandler"
- **Fuzzy duplicate detection**: "Lithia Motors" and "Lithia & Driveway" recognized as same company
- **Competitor exclusion**: 16 DMS competitors filtered (CDK Global, Reynolds & Reynolds, etc.)

### Prompt Tracing
All LLM interactions logged to `data/prompt_logs/session_*.jsonl`:
```python
from utils.prompt_tracer import prompt_tracer
report = prompt_tracer.generate_report()
```

### Results Caching
Results saved to `data/results_cache/`:
- `customer_YYYYMMDD_HHMMSS.json`
- `partner_YYYYMMDD_HHMMSS.json`

## 📈 Performance

**Typical execution time:**
- Intent classification: 1-2 seconds
- Research (30 companies): 30-60 seconds
- Enrichment (30 companies): 60-90 seconds
- Scoring (30 companies): 30-45 seconds
- **Total: ~2-3 minutes for 10 results**

**Optimizations:**
- Results caching
- Parallel search execution
- Early filtering (40% fewer enrichment calls)
- Smart duplicate detection

## 📚 Documentation

- **[Complete Guide](docs/GUIDE.md)** - Setup, architecture, usage, development
- **[Example Results](data/results_cache/)** - Customer & partner results

## 🧪 Testing

Verify setup:
```bash
python test_setup.py
```

Test individual agents:
```bash
python -m agents.research_agent
python -m agents.scoring_agent
```

## 🐛 Troubleshooting

**Ollama not running:**
```bash
ollama serve
ollama list  # Should show mistral:7b
```

**Tavily API errors:**
- Check API key in `.env`
- Verify quota at https://tavily.com/dashboard
- Free tier: 1,000 searches/month

**Poor results:**
1. Check logs: `data/logs/lead_generator.log`
2. Review prompt traces: `data/prompt_logs/`
3. Adjust prompts in `prompts/` directory

See [Complete Guide](docs/GUIDE.md) for detailed troubleshooting.

## 🎓 How It Works

1. **User input** → Intent Classifier determines customer/partner/both
2. **Research Agent** → Generates 6-8 search queries, executes Tavily searches
3. **Smart filtering** → Removes competitors, duplicates, subsidiaries
4. **Enrichment Agent** → Gathers company details (website, HQ, size)
5. **Scoring Agent** → Evaluates fit (0-10), generates rationale
6. **Top 10 results** → Cached and displayed

## 🚀 Next Steps

After installation:
1. Run predefined queries to see results
2. Explore cached results in `data/results_cache/`
3. Review prompt traces in `data/prompt_logs/`
4. Customize prompts in `prompts/` directory
5. Edit company profile in `data/axlewave_context/`

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a prototype/assignment project. For questions or improvements, please open an issue.

---

**Built with:** Ollama (Mistral 7B) • Tavily AI • Streamlit • Python 3.9+

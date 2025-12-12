# Quick Start Guide

Get up and running with DealerFlow Lead Generator in 5 minutes!

## Prerequisites

- **macOS** (Linux/Windows also supported)
- **Python 3.9+**
- **Git**

## Installation (3 steps)

### 1. Install Ollama (Local LLM)

```bash
brew install ollama
ollama pull llama3.1:8b
```

Start Ollama in background:
```bash
ollama serve
```

### 2. Clone and Setup

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

### 3. Verify Setup

```bash
source venv/bin/activate
python test_setup.py
```

You should see all tests passing ✅

## Running the App

```bash
streamlit run app.py
```

Open browser to [http://localhost:8501](http://localhost:8501)

## First Run

1. In the UI, enter: **"Find me potential customers"**
2. Click **"Generate Leads"**
3. Wait 3-5 minutes for AI agents to complete
4. View your top 10 automotive dealerships!

## Example Queries

Try these in the natural language input:

- "Find potential customers for our dealership management system"
- "Who could we partner with to enhance our platform?"
- "Generate both customer and partner lists"
- "Discover automotive dealerships in North America"

## Troubleshooting

### Ollama Connection Error

```bash
# Make sure Ollama is running
ollama serve

# Verify model is downloaded
ollama list
```

### Import Errors

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Search Not Working

By default, we use DuckDuckGo (free, no API key). If you have issues:

1. Try a different search provider in `.env`:
   ```
   SEARCH_PROVIDER=duckduckgo
   ```

2. Or get free API keys:
   - Tavily: https://tavily.com (1000 free/month)
   - Google: https://console.cloud.google.com (100 free/day)

## What Happens When You Run It?

1. **Intent Classifier Agent**: Determines if you want customers or partners
2. **Research Agent**: Generates search queries and discovers ~30 companies
3. **Enrichment Agent**: Fetches website, location, size for each company
4. **Scoring Agent**: Evaluates fit and generates rationale
5. **Results**: Top 10 companies ranked by fit score

## Performance Tips

- **First run is slow** (~3-5 min) - agents are doing deep research
- **Results are cached** - second run for same query is instant
- **Use specific queries** - More specific = better results
- **GPU helps** - If you have a GPU, Ollama will use it automatically

## Next Steps

- Check [README.md](README.md) for detailed documentation
- Explore prompt templates in `prompts/` directory
- Review cached results in `data/results_cache/`
- Check logs in `lead_generator.log`

## Need Help?

Common issues:
1. Ollama not running → `ollama serve`
2. Model not found → `ollama pull llama3.1:8b`
3. Python errors → Check you're in venv: `source venv/bin/activate`

---

**Ready to generate some leads?** 🚀

```bash
streamlit run app.py
```

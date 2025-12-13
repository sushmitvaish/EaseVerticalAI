# Search API Setup Guide

This guide will help you set up real web search for the prototype (to replace the fallback database).

## 🎯 Quick Recommendation

**For this prototype, use Serper API** - it's the easiest and most generous.

---

## Option 1: Serper API (RECOMMENDED) ⭐

**Best for:** Quick prototype setup, generous free tier

### Setup Steps (1 minute):

1. **Sign up**: Go to https://serper.dev
2. **Get API key**:
   - Click "API Key" in dashboard
   - Copy your key (starts with something like `a1b2c3...`)
3. **Update .env file**:
   ```bash
   SEARCH_PROVIDER=serper
   SERPER_API_KEY=paste_your_key_here
   ```
4. **Test it**:
   ```bash
   source venv/bin/activate
   python -c "from utils.search_client import search_client; print(search_client.search('automotive dealerships', max_results=3))"
   ```

### Pricing:
- **Free tier**: $50 credit = 20,000 searches
- **Cost per search**: $0.0025 (after free tier)
- **Your prototype usage**: ~500 searches = **FREE**

---

## Option 2: Google Custom Search API

**Best for:** Maximum search quality (it's Google!)

### Setup Steps (5 minutes):

#### Step 1: Get API Key
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Go to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "API Key"
5. Copy your API key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXX`)

#### Step 2: Enable Custom Search API
1. Go to "APIs & Services" → "Library"
2. Search for "Custom Search API"
3. Click "Enable"

#### Step 3: Create Custom Search Engine
1. Go to https://programmablesearchengine.google.com/
2. Click "Add" or "Create new search engine"
3. **Important**: Select "Search the entire web" (not specific sites)
4. Create the search engine
5. Click on it, go to "Setup" → copy the **Search engine ID** (looks like: `a1b2c3d4e5f6g7h8i`)

#### Step 4: Update .env
```bash
SEARCH_PROVIDER=google
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i
```

### Pricing:
- **Free tier**: 100 searches/day (3,000/month)
- **Cost per search**: $5 per 1,000 queries (after free tier)
- **Your prototype usage**: ~500 searches = **FREE**

---

## Option 3: Tavily AI Search

**Best for:** LLM-optimized results, AI applications

### Setup Steps (2 minutes):

1. **Sign up**: Go to https://tavily.com
2. **Get API key**:
   - Dashboard → API Keys
   - Copy your key (starts with `tvly-`)
3. **Install package** (if not already installed):
   ```bash
   pip install tavily-python
   ```
4. **Update .env**:
   ```bash
   SEARCH_PROVIDER=tavily
   TAVILY_API_KEY=tvly-XXXXXXXXXXXX
   ```

### Pricing:
- **Free tier**: 1,000 searches/month
- **Cost per search**: $0.001 (after free tier)
- **Your prototype usage**: ~500 searches = **FREE**

---

## Testing Your Search Setup

After setting up any provider, test it:

```bash
# Activate virtual environment
cd "/Users/sushmitvaish/Desktop/CMU Documents/Job Search Documents/EaseVerticalAI"
source venv/bin/activate

# Quick test
python -c "
from utils.search_client import search_client
results = search_client.search('automotive dealerships North America', max_results=5)
print(f'✅ Found {len(results)} results')
for r in results[:3]:
    print(f'  - {r.title}: {r.url}')
"
```

**Expected output:**
```
✅ Found 5 results
  - AutoNation: https://www.autonation.com
  - Lithia Motors: https://www.lithia.com
  - Group 1 Automotive: https://www.group1auto.com
```

---

## Running the Full Prototype

Once search is working:

```bash
# Clear old cached results
rm -rf data/results_cache/*.json

# Run the application
streamlit run app.py
```

Now when you generate leads, you'll get:
- ✅ **Real-time web search results**
- ✅ **Fresh company data**
- ✅ **Ability to discover new companies**
- ✅ **Current information (not just my training data)**

---

## Troubleshooting

### "Search provider not found"
- Check that `SEARCH_PROVIDER` in .env matches: `serper`, `google`, or `tavily`
- Make sure there are no typos

### "API key invalid"
- Verify you copied the entire key (no spaces)
- Check the key is active in the provider's dashboard
- For Google: Make sure Custom Search API is enabled

### "Rate limit exceeded"
- Google: You've used 100 searches today (wait until tomorrow or upgrade)
- Serper: You've used all $50 credit (upgrade account)
- Tavily: You've used 1,000 searches this month (wait or upgrade)

### Still seeing fallback results
- Check logs: `tail -50 lead_generator.log`
- Look for "Falling back to synthetic search results" - this means API call failed
- Verify .env file is loaded: restart the application after changing .env

---

## Cost Comparison for Your Prototype

| Provider | Free Tier | Enough for Prototype? | Cost if Exceeded |
|----------|-----------|----------------------|------------------|
| **Serper** | 20,000 searches | ✅ Yes (40x more than needed) | $2.50/1K |
| **Google** | 3,000/month | ✅ Yes (6x more than needed) | $5/1K |
| **Tavily** | 1,000/month | ✅ Yes (2x more than needed) | $1/1K |

**Recommendation**: Start with **Serper** for maximum flexibility during development.

---

## What Changes When You Enable Real Search?

**Before (Fallback Database):**
- ❌ Same 25 companies every time
- ❌ Limited to my training data
- ❌ No discovery of new companies
- ✅ Always works (no API failures)

**After (Real Search):**
- ✅ Discovers companies from live web
- ✅ Fresh, current information
- ✅ Can find 100+ unique companies
- ✅ Gets latest news, acquisitions, etc.
- ⚠️ Depends on API availability
- ⚠️ May cost money if you exceed free tier

Both approaches will work for your assignment, but real search gives you a production-quality demo!

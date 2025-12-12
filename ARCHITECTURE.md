# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Streamlit Web App)                        │
│                                                                 │
│  Natural Language Input: "Find me potential customers"         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                             │
│                   (orchestrator.py)                             │
│                                                                 │
│  • Coordinates agent workflow                                  │
│  • Manages state and caching                                   │
│  • Returns structured results                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌────────┐          ┌────────────┐        ┌───────────┐
   │Intent  │          │ Research   │        │Enrichment │
   │Classify│──────────▶│ Agent      │───────▶│ Agent     │
   │Agent   │          │            │        │           │
   └────────┘          └────────────┘        └───────────┘
                              │                     │
                              ▼                     ▼
                       ┌──────────────┐      ┌──────────┐
                       │ Web Search   │      │ Company  │
                       │ API          │      │ Info     │
                       └──────────────┘      └──────────┘
                                                   │
                                                   ▼
                                            ┌──────────┐
                                            │ Scoring  │
                                            │ Agent    │
                                            └──────────┘
                                                   │
                                                   ▼
                                            ┌──────────┐
                                            │ Top 10   │
                                            │ Results  │
                                            └──────────┘
```

## Agent Communication Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Agent Workflow                            │
└──────────────────────────────────────────────────────────────┘

1. Intent Classifier Agent
   Input:  "Find me potential customers"
   Output: {"intent": "customer", "confidence": 0.95}
           │
           ▼
2. Research Agent
   Input:  intent="customer", company_profile
   LLM:    Generate search queries
   Search: Execute 8-10 queries via DuckDuckGo
   LLM:    Extract company names from results
   Output: ["AutoNation", "Lithia Motors", ...]  (30 companies)
           │
           ▼
3. Enrichment Agent (Parallel Processing)
   Input:  company_names = ["AutoNation", "Lithia Motors", ...]

   For each company:
     Search: "{company} headquarters website location"
     LLM:    Extract structured data

   Output: {
             "AutoNation": CompanyInfo(
               website="https://autonation.com",
               headquarters="Fort Lauderdale, FL",
               size="Large",
               ...
             ),
             ...
           }
           │
           ▼
4. Scoring Agent
   Input:  enriched_companies, discovery_type="customer"

   For each company:
     LLM: Evaluate fit against AxleWave profile
     LLM: Generate rationale

   Sort by fit_score
   Output: Top 10 companies with scores and rationales
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  • Streamlit Web UI (app.py)                                   │
│  • Natural language input                                      │
│  • Result visualization and download                           │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                             │
│  • Orchestrator (orchestrator.py)                              │
│  • Multi-agent coordination                                    │
│  • Workflow management                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT LAYER                                 │
│  • Intent Classifier Agent                                     │
│  • Research Agent                                              │
│  • Enrichment Agent                                            │
│  • Scoring Agent                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                │
│  • LLM Client (Ollama / HuggingFace)                          │
│  • Search Client (DuckDuckGo / Tavily / Google)               │
│  • Document Processor                                          │
│  • Prompt Tracer                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                            │
│  • Open-Source LLMs (Llama 3.1, Mistral 7B)                   │
│  • Web Search APIs                                             │
│  • JSON File Storage (caching, context)                        │
│  • Logging & Monitoring                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Input
    │
    ▼
[Intent Classification]
    │
    ▼
┌─────────────────┐
│ Company Profile │◀──── AxleWave Docs (data/axlewave_context/)
│ (Context)       │
└─────────────────┘
    │
    ▼
┌────────────────────────────┐
│ Generate Search Queries    │
│ (LLM)                      │
└────────────────────────────┘
    │
    ▼
┌────────────────────────────┐
│ Execute Web Searches       │
│ (Search API)               │
└────────────────────────────┘
    │
    ▼
┌────────────────────────────┐
│ Extract Company Names      │
│ (LLM)                      │
└────────────────────────────┘
    │
    ▼
┌────────────────────────────┐
│ Enrich Each Company        │
│ (Search + LLM)             │
└────────────────────────────┘
    │
    ▼
┌────────────────────────────┐
│ Score & Rank Companies     │
│ (LLM)                      │
└────────────────────────────┘
    │
    ▼
┌────────────────────────────┐
│ Cache Results              │◀──── data/results_cache/
└────────────────────────────┘
    │
    ▼
Top 10 Results (JSON)
    │
    ▼
Display in UI
```

## LLM Integration Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    LLM Client (utils/llm_client.py)         │
└──────────────────────────────────────────────────────────────┘
                    │
      ┌─────────────┴─────────────┐
      ▼                           ▼
┌─────────────┐           ┌──────────────┐
│   Ollama    │           │ HuggingFace  │
│  (Local)    │           │  (Cloud API) │
└─────────────┘           └──────────────┘
      │                           │
      ▼                           ▼
┌─────────────┐           ┌──────────────┐
│ Llama 3.1   │           │ Mistral 7B   │
│ Mistral 7B  │           │ via HF API   │
│ Mixtral     │           └──────────────┘
└─────────────┘

Features:
• Unified interface for both providers
• JSON mode for structured outputs
• Retry logic for reliability
• Temperature control for determinism
• Prompt tracing for optimization
```

## Search Integration Architecture

```
┌──────────────────────────────────────────────────────────────┐
│               Search Client (utils/search_client.py)        │
└──────────────────────────────────────────────────────────────┘
                    │
      ┌─────────────┼─────────────┬─────────────┐
      ▼             ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│DuckDuckGo│  │  Tavily  │  │  Google  │  │  Serper  │
│  (Free)  │  │ (1K/mo)  │  │(100/day) │  │(2.5K/mo) │
└──────────┘  └──────────┘  └──────────┘  └──────────┘

Features:
• Multi-provider support
• Automatic fallback
• Result normalization
• Rate limit handling
• Batch search capability
```

## Caching & Storage Architecture

```
data/
├── axlewave_context/
│   └── company_context.json       ← Company profile & product info
│
├── results_cache/
│   ├── customer_20241211_143022.json
│   ├── partner_20241211_143530.json
│   └── both_20241211_144105.json
│
└── prompt_logs/
    └── session_20241211_143000.jsonl  ← All prompts & responses

Cache Strategy:
• Results cached by (intent + timestamp)
• Prompt logs in JSONL for analysis
• Company context loaded once at startup
```

## Deployment Architecture (Production)

```
┌──────────────────────────────────────────────────────────────┐
│                       Load Balancer                          │
│                    (AWS ALB / Nginx)                         │
└──────────────────────────────────────────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ App      │  │ App      │  │ App      │
│Instance 1│  │Instance 2│  │Instance 3│
└──────────┘  └──────────┘  └──────────┘
      │             │             │
      └─────────────┼─────────────┘
                    ▼
      ┌─────────────────────────────┐
      │     Redis Cache              │
      │  (Distributed caching)       │
      └─────────────────────────────┘
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│PostgreSQL│  │ Ollama   │  │  S3      │
│(Results) │  │(LLM GPU) │  │(Exports) │
└──────────┘  └──────────┘  └──────────┘
```

## Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
└──────────────────────────────────────────────────────────────┘

Layer 1: Network
• HTTPS only (TLS 1.3)
• API rate limiting
• DDoS protection

Layer 2: Application
• Input validation (Pydantic)
• No SQL injection (no DB yet)
• XSS prevention (Streamlit handles this)
• Environment variables for secrets

Layer 3: Data
• No PII storage
• Results cached locally
• Optional encryption at rest
• Audit logging

Layer 4: LLM
• Local Ollama = no data leaves system
• HuggingFace = encrypted transit
• Prompt sanitization
```

## Scalability Considerations

### Horizontal Scaling
```
Current (Single Instance):
• 1 request at a time
• 3-5 min per request
• ~12-20 requests/hour

Scaled (Multiple Instances):
• N parallel requests
• Load balanced
• Redis for shared cache
• ~12-20 requests/hour × N instances
```

### Optimization Opportunities

1. **Parallel Enrichment**
   - Currently sequential
   - Can parallelize 30 company enrichments
   - Reduce 60-120s → 15-30s

2. **Batch LLM Calls**
   - Group similar prompts
   - Single LLM call for multiple companies
   - Reduce API calls by 70%

3. **Smarter Caching**
   - Cache individual company data
   - Reuse across different queries
   - 80% cache hit rate possible

4. **Pre-computed Results**
   - Daily batch processing
   - Top customers/partners always ready
   - Real-time = instant response

## Monitoring & Observability

```
┌──────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
└──────────────────────────────────────────────────────────────┘

Logs:
• Application logs → lead_generator.log
• Prompt traces → data/prompt_logs/
• Aggregation → ELK Stack (production)

Metrics:
• Request latency
• Agent execution time
• LLM token usage
• Search API calls
• Cache hit rate
• Error rate

Alerting:
• LLM connection failures
• Search API errors
• High latency (>10min)
• Low quality results (<5 companies)
```

## Cost Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Cost Breakdown                            │
└──────────────────────────────────────────────────────────────┘

Development (Current):
• LLM: $0 (Ollama local)
• Search: $0 (DuckDuckGo)
• Storage: $0 (local disk)
• Total: $0/month

Production (1000 queries/day):
• LLM: $500-1000/mo (GPU server) or $100-500/mo (API)
• Search: $100-200/mo (Tavily/Serper volume)
• Hosting: $200-500/mo (AWS/GCP)
• Storage: $50-100/mo (PostgreSQL + Redis)
• Monitoring: $50-100/mo (Datadog/New Relic)
• Total: ~$1000-2400/month

Per-Request Cost:
• 1000 queries/day = 30K/month
• $1500/month ÷ 30K = $0.05 per query
• Acceptable for B2B lead gen ($1-5 per lead industry standard)
```

## Future Architecture Enhancements

### Phase 1: Performance
- Parallel agent execution
- Result streaming (show partial results)
- GPU acceleration
- CDN for static assets

### Phase 2: Intelligence
- RAG for company knowledge base
- Fine-tuned LLM on automotive data
- Feedback loop for improvement
- A/B testing framework

### Phase 3: Scale
- Microservices architecture
- Message queue (RabbitMQ)
- Multiple LLM backends
- Global CDN

### Phase 4: Features
- Real-time company monitoring
- CRM integration (Salesforce, HubSpot)
- Email campaigns
- White-label solution

---

This architecture is designed to be:
✅ **Simple** - Easy to understand and maintain
✅ **Scalable** - Can grow from prototype to production
✅ **Resilient** - Error handling and retries built-in
✅ **Observable** - Comprehensive logging and tracing
✅ **Cost-Effective** - Optimize for price-to-performance

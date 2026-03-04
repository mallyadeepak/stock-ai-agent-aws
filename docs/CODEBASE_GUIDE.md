# Stock AI Agent - Comprehensive Codebase Guide

A detailed walkthrough of the Stock AI Agent codebase using real-world analogies and visual diagrams.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [File-by-File Explanation](#file-by-file-explanation)
- [Complete Request Flow](#complete-request-flow)
- [Key Patterns](#key-patterns)
- [Testing](#testing)

---

## Overview

The Stock AI Agent is an intelligent stock market assistant that combines AWS Bedrock's language models with real-time financial data from Yahoo Finance. Think of it as having a knowledgeable financial advisor who can instantly analyze stocks, compare companies, and provide data-driven insights - all through natural conversation.

### Real-World Analogy: Financial Advisory Firm

```
╔══════════════════════════════════════════════════════════╗
║           STOCK AI AGENT = FINANCIAL ADVISORY FIRM       ║
╚══════════════════════════════════════════════════════════╝

config.py       = Company Policy Manual
agent.py        = Project Manager / Coordinator
sector_tools.py = Industry Research Department
stock_tools.py  = Data Analysis Team
analysis_tools.py = Senior Analysts
main.py         = Direct Phone Line (Local Office)
handler.py      = Reception Desk (Public Office)
```

---

## Architecture

### High-Level System Flow

```
USER QUERY: "What are the best tech stocks under $200?"
                              |
                              v
┌─────────────────────────────────────────────────────────────────────────┐
│                       ENTRY POINTS                                       │
│  ┌───────────────┐         OR          ┌──────────────────┐            │
│  │  main.py      │                     │  Lambda Handler  │            │
│  │  (Local CLI)  │                     │  (AWS Hosted)    │            │
│  └───────┬───────┘                     └────────┬─────────┘            │
└──────────┼──────────────────────────────────────┼──────────────────────┘
           │                                       │
           └───────────────┬───────────────────────┘
                           v
┌─────────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATOR                                  │
│  ┌───────────────────────────────────────────────────────────┐          │
│  │  agent.py - create_stock_agent()                          │          │
│  │  • Takes user query                                       │          │
│  │  • Decides which tools to use                             │          │
│  │  • Coordinates multiple tool calls                        │          │
│  │  • Synthesizes final answer                               │          │
│  └─────────────────────┬─────────────────────────────────────┘          │
└────────────────────────┼────────────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            v            v            v
    ┌───────────┐  ┌────────┐  ┌──────────┐
    │  Bedrock  │  │ Tools  │  │  Config  │
    │  (Brain)  │  │ (Hands)│  │ (Rules)  │
    └───────────┘  └────────┘  └──────────┘
                       │
        ┌──────────────┼──────────────┐
        v              v              v
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Sector Tools │ │Stock Tools  │ │Analysis Tools│
│             │ │             │ │             │
│ Find stocks │ │ Get prices  │ │ Get news    │
│ by industry │ │ & metrics   │ │ & ratings   │
└─────────────┘ └─────────────┘ └─────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       v
              ┌─────────────────┐
              │ Yahoo Finance   │
              │ (Data Source)   │
              └─────────────────┘
```

### Tool Catalog

```
┌───────────────────────────────────────────────────────────────────┐
│                      STOCK AGENT TOOLS (10 Total)                 │
├─────────────────────┬───────────────────┬─────────────────────────┤
│   SECTOR TOOLS (3)  │  STOCK TOOLS (4)  │   ANALYSIS TOOLS (3)    │
├─────────────────────┼───────────────────┼─────────────────────────┤
│ get_stocks_by_sector│ get_stock_quote   │ get_analyst_recommenda- │
│                     │                   │ tions                   │
│ get_stocks_by_      │ get_stock_metrics │                         │
│ industry            │                   │ get_stock_news          │
│                     │ compare_stocks    │                         │
│ list_industries_in_ │                   │ analyze_stock_value     │
│ sector              │ get_stock_history │                         │
└─────────────────────┴───────────────────┴─────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Yahoo Finance  │
                    │    (yfinance)   │
                    └─────────────────┘
```

---

## File-by-File Explanation

### config.py - The Control Panel

**Location:** `/src/stock_agent/config.py`

**Analogy:** Think of this as the job description and training manual for a financial advisor. It tells them what services they offer, how to behave with clients, and what resources they have available.

**What it contains:**
- AWS and Bedrock settings (region, model ID)
- Model parameters (max_tokens, temperature)
- The system prompt that defines the agent's personality

```
┌─────────────────────────────────────────────────────────┐
│                    AgentConfig                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  AWS Settings                                   │   │
│  │  • aws_region = "us-east-1"                     │   │
│  │  • model_id = "us.amazon.nova-pro-v1:0"         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Model Parameters                               │   │
│  │  • max_tokens = 4096 (response length)          │   │
│  │  • temperature = 0.7 (creativity level)         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  System Prompt (Agent's Instructions)           │   │
│  │  • What tools are available                     │   │
│  │  • How to help users                            │   │
│  │  • Response guidelines                          │   │
│  │  • Disclaimers to include                       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

### agent.py - The Brain Coordinator

**Location:** `/src/stock_agent/agent.py`

**Analogy:** Imagine a restaurant expediter who reads orders, decides which chefs need to cook which dishes, coordinates timing, and ensures everything comes together for the final plate.

**Key functions:**
- `create_stock_agent()` - Factory that builds the agent
- `run_query()` - Sends question, gets answer
- `get_agent_info()` - Returns configuration details

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  create_stock_agent()                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. Load Configuration                                  │   │
│  │  2. Create BedrockModel connection                      │   │
│  │  3. Register 10 tools                                   │   │
│  │  4. Return Agent instance                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  run_query(agent, "Compare AAPL and GOOGL")                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Agent Reasoning Loop:                                  │   │
│  │                                                         │   │
│  │  Query → LLM → Tool Selection → Tool Execution →       │   │
│  │  Results → LLM → More Tools? → Final Response          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

### stock_tools.py - The Data Terminal

**Location:** `/src/stock_agent/tools/stock_tools.py`

**Analogy:** Think of Bloomberg terminals on a trading floor. Traders type in stock symbols and get instant data. These functions do the same programmatically.

**Tools provided:**
| Tool | Input | Output |
|------|-------|--------|
| `get_stock_quote` | Symbol (e.g., "AAPL") | Price, volume, market cap, 52-week range |
| `get_stock_metrics` | Symbol | P/E ratio, EPS, margins, dividends |
| `compare_stocks` | List of symbols | Side-by-side comparison |
| `get_stock_history` | Symbol + period | Historical OHLCV data |

```
get_stock_quote("AAPL")
│
├─1. Create yfinance Ticker
│   ticker = yf.Ticker("AAPL")
│
├─2. Fetch info dictionary
│   info = ticker.info
│
├─3. Extract relevant fields
│   current_price, market_cap, etc.
│
├─4. Calculate derived metrics
│   change = current_price - previous_close
│
└─5. Return clean dictionary
    {symbol, name, price, change, market_cap, ...}
```

---

### sector_tools.py - The Research Department

**Location:** `/src/stock_agent/tools/sector_tools.py`

**Analogy:** Imagine walking into a bookstore and saying "Show me sci-fi books." The clerk guides you to the sci-fi section. These tools do the same for stocks.

**Market structure:**
```
┌─────────────────────────────────────────────────────────┐
│  SECTORS (11 major categories)                          │
├─────────────────────────────────────────────────────────┤
│  Technology                                             │
│  ├─ Industries: Software, Semiconductors, Hardware...   │
│  └─ Top Stocks: AAPL, MSFT, NVDA, GOOGL, META...       │
│                                                         │
│  Healthcare                                             │
│  ├─ Industries: Biotechnology, Drug Manufacturers...   │
│  └─ Top Stocks: UNH, JNJ, LLY, PFE, ABBV...            │
│                                                         │
│  Financial, Energy, Consumer, Industrials...           │
└─────────────────────────────────────────────────────────┘
```

---

### analysis_tools.py - The Senior Analysts

**Location:** `/src/stock_agent/tools/analysis_tools.py`

**Analogy:** The difference between a financial newspaper and a financial analyst. The newspaper reports "Stock XYZ is at $50." The analyst reports "Stock XYZ is at $50, which is 20% below analyst targets, has strong fundamentals, and recent news suggests a buying opportunity."

**Valuation Analysis Logic:**
```
analyze_stock_value("AAPL")
│
├─ Fetch metrics: P/E, PEG, 52-week position, etc.
│
├─ Evaluate each factor:
│  ├─ P/E < 15 → POSITIVE
│  ├─ PEG < 1 → POSITIVE (undervalued for growth)
│  ├─ Near 52-week low → POSITIVE (potential upside)
│  └─ Strong margins → POSITIVE
│
├─ Aggregate signals:
│  if positive >= negative + 2 → BULLISH
│  elif negative >= positive + 2 → BEARISH
│  else → NEUTRAL
│
└─ Return verdict with reasoning
```

---

### handler.py - The Reception Desk

**Location:** `/lambda/handler.py`

**Analogy:** Think of a restaurant. The agent is the kitchen, and the Lambda handler is the waiter. The waiter takes orders (HTTP requests), passes them to the kitchen (agent), and brings back the prepared food (responses).

```
┌──────────────────────────────────────────────────────────────┐
│                  AWS LAMBDA FUNCTION                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  COLD START (First request)                                  │
│  • Lambda container initializes                              │
│  • Creates agent connection to Bedrock (2-3 seconds)         │
│                                                              │
│  WARM START (Subsequent requests)                            │
│  • Reuses cached agent (<100ms)                              │
│  • Much faster!                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Singleton Pattern:**
```python
_agent = None  # Module-level variable

def get_agent():
    global _agent
    if _agent is None:
        _agent = create_stock_agent()  # Only runs once
    return _agent  # Returns cached agent
```

---

## Complete Request Flow

```
USER QUERY: "What are the best semiconductor stocks?"

STEP 1: Entry Point
───────────────────
User sends request via API Gateway
→ Lambda handler.py receives event

STEP 2: Agent Initialization
────────────────────────────
get_agent() called
→ Checks if _agent exists (singleton)
→ If not, creates new agent

STEP 3: Query Processing
────────────────────────
run_query(agent, "What are the best semiconductor...")
→ Agent sends to Bedrock with system prompt + tools

STEP 4: LLM Reasoning
─────────────────────
Bedrock Nova Pro thinks:
"I should use get_stocks_by_industry('Semiconductors')"
→ Returns tool call request

STEP 5: Tool Execution
──────────────────────
get_stocks_by_industry("Semiconductors", 10)
→ Fetches from Yahoo Finance
→ Returns: NVDA, AMD, INTC, etc.

STEP 6: Response Generation
───────────────────────────
LLM formats natural language response:
"Here are the best semiconductor stocks:
 1. NVIDIA (NVDA) - $695.30, $2.1T market cap..."

STEP 7: Return to User
──────────────────────
HTTP 200 with JSON response
```

---

## Key Patterns

### 1. Strands SDK Tool Pattern
```python
@tool
def get_stock_quote(symbol: str) -> dict[str, Any]:
    """Get the current stock quote..."""
    # Implementation
```
The `@tool` decorator tells the SDK "this function can be called by the AI."

### 2. Agent ReAct Loop
```
1. User asks question
2. LLM thinks: "I need to call tool X"
3. Agent executes tool X
4. LLM receives results
5. LLM: "Need tool Y" OR "Ready to answer"
6. Repeat until done
7. Generate final response
```

### 3. Lambda Singleton Pattern
```python
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = create_stock_agent()
    return _agent
```
Avoids recreating connections, saving time and money.

### 4. Graceful Error Handling
```python
# Success
return {"symbol": "AAPL", "price": 175.50, ...}

# Error
return {"error": "Stock symbol 'INVALID' not found"}
```
The agent understands both and responds appropriately.

---

## Testing

### Local Testing
```bash
# Interactive mode
python main.py

# Single query
python main.py -q "What are the top healthcare stocks?"

# Show configuration
python main.py --info
```

### API Testing
```bash
# Test deployed API
python test_api.py

# Custom query
python test_api.py "Compare AAPL and MSFT"

# Direct curl
curl -X POST https://YOUR_API_URL \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the price of TSLA?"}'
```

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/stock_agent
```

---

## Common Usage Patterns

### Pattern 1: Stock Discovery
```
User: "I want to invest in renewable energy"
Agent:
  1. list_industries_in_sector("energy")
  2. get_stocks_by_industry("Utilities - Renewable")
  → Returns: NEE, ENPH, SEDG, etc.
```

### Pattern 2: Deep Analysis
```
User: "Tell me about Tesla"
Agent:
  1. get_stock_quote("TSLA")
  2. get_stock_metrics("TSLA")
  3. analyze_stock_value("TSLA")
  4. get_analyst_recommendations("TSLA")
  → Synthesizes comprehensive analysis
```

### Pattern 3: Comparison
```
User: "Should I buy Apple or Microsoft?"
Agent:
  1. compare_stocks(["AAPL", "MSFT"])
  2. analyze_stock_value for each
  → Provides balanced comparison
```

---

## AWS Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS CLOUD                            │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   API Gateway    │────────▶│  Lambda Function │         │
│  │   (HTTP API)     │         │  (handler.py)    │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
│           │                            │                   │
│           v                            v                   │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  CloudWatch Logs │         │  Amazon Bedrock  │         │
│  │  (Monitoring)    │         │  (Nova Pro LLM)  │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| Resource | Name | Purpose |
|----------|------|---------|
| Lambda Function | `stock-ai-agent` | Runs the agent |
| Lambda Layer | `stock-agent-dependencies` | Python packages |
| API Gateway | `stock-ai-agent-api` | HTTP endpoint |
| IAM Role | `stock-agent-lambda-role` | Permissions |

---

*This documentation was generated using the codebase-explainer agent.*

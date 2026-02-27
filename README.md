# Stock AI Agent

An AI-powered stock analysis agent built with AWS Strands Agents SDK and Amazon Bedrock.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Stock AI Agent                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────────┐     ┌─────────────────────────────┐
│   Client     │     │   API Gateway    │     │      AWS Lambda             │
│              │────▶│   (HTTP API)     │────▶│                             │
│  curl/REST   │     │                  │     │  ┌─────────────────────┐    │
│  Python SDK  │     │  /POST           │     │  │   Lambda Handler    │    │
│  Web App     │     │                  │     │  │   (handler.py)      │    │
└──────────────┘     └──────────────────┘     │  └──────────┬──────────┘    │
                                              │             │               │
                                              │  ┌──────────▼──────────┐    │
                                              │  │   Stock Agent       │    │
                                              │  │   (Strands SDK)     │    │
                                              │  └──────────┬──────────┘    │
                                              │             │               │
                                              └─────────────┼───────────────┘
                                                            │
                     ┌──────────────────────────────────────┼───────────────┐
                     │                                      │               │
           ┌─────────▼─────────┐                 ┌──────────▼──────────┐    │
           │  Amazon Bedrock   │                 │    Stock Tools      │    │
           │                   │                 │                     │    │
           │  ┌─────────────┐  │                 │  ┌───────────────┐  │    │
           │  │ Nova Pro    │  │                 │  │ Sector Tools  │  │    │
           │  │ (LLM)       │  │                 │  ├───────────────┤  │    │
           │  └─────────────┘  │                 │  │ Stock Tools   │  │    │
           │                   │                 │  ├───────────────┤  │    │
           └───────────────────┘                 │  │ Analysis Tools│  │    │
                                                 │  └───────┬───────┘  │    │
                                                 └──────────┼──────────┘    │
                                                            │               │
                                                 ┌──────────▼──────────┐    │
                                                 │    Yahoo Finance    │    │
                                                 │    (yfinance API)   │    │
                                                 └─────────────────────┘    │
```

## Component Overview

### Core Components

| Component | Description |
|-----------|-------------|
| **API Gateway** | HTTP API endpoint for REST access |
| **Lambda Function** | Serverless compute running the agent |
| **Stock Agent** | Strands SDK agent with tool orchestration |
| **Amazon Bedrock** | LLM inference (Nova Pro model) |
| **Stock Tools** | Custom tools for stock data retrieval |

### Tool Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Stock Agent Tools                       │
├─────────────────────┬───────────────────┬───────────────────┤
│   Sector Tools      │   Stock Tools     │  Analysis Tools   │
├─────────────────────┼───────────────────┼───────────────────┤
│ get_stocks_by_sector│ get_stock_quote   │ get_analyst_recs  │
│ get_stocks_by_ind.  │ get_stock_metrics │ get_stock_news    │
│ list_industries     │ compare_stocks    │ analyze_stock_val │
│                     │ get_stock_history │                   │
└─────────────────────┴───────────────────┴───────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Yahoo Finance  │
                    │     (yfinance)  │
                    └─────────────────┘
```

## Project Structure

```
stock-ai-agent-aws/
├── src/
│   └── stock_agent/
│       ├── __init__.py
│       ├── agent.py          # Agent creation and configuration
│       ├── config.py         # Configuration settings
│       └── tools/
│           ├── sector_tools.py    # Sector/industry discovery
│           ├── stock_tools.py     # Stock quotes and metrics
│           └── analysis_tools.py  # Analyst recommendations
├── lambda/
│   ├── handler.py            # Lambda entry point
│   └── requirements.txt      # Lambda dependencies
├── tests/
│   ├── conftest.py           # Test fixtures
│   └── test_tools.py         # Unit tests
├── main.py                   # Local CLI
├── Dockerfile                # Container deployment
├── pyproject.toml            # Project configuration
└── requirements.txt          # Development dependencies
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
│                                                                  │
│  ┌────────────────┐    ┌────────────────┐    ┌───────────────┐  │
│  │   S3 Bucket    │    │  Lambda Layer  │    │    ECR        │  │
│  │ (deployment)   │───▶│ (dependencies) │    │ (optional)    │  │
│  └────────────────┘    └───────┬────────┘    └───────────────┘  │
│                                │                                 │
│                        ┌───────▼────────┐                       │
│  ┌─────────────┐       │    Lambda      │       ┌────────────┐  │
│  │ API Gateway │──────▶│   Function     │──────▶│  Bedrock   │  │
│  │  (HTTP)     │       │                │       │  (LLM)     │  │
│  └─────────────┘       └────────────────┘       └────────────┘  │
│        │                       │                                 │
│        │               ┌───────▼────────┐                       │
│        │               │   IAM Role     │                       │
│        │               │ (permissions)  │                       │
│        │               └────────────────┘                       │
│        │                                                        │
│  ┌─────▼─────┐                                                  │
│  │CloudWatch │                                                  │
│  │  Logs     │                                                  │
│  └───────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Stock Quotes**: Real-time price, volume, and market cap data
- **Stock Metrics**: P/E ratio, EPS, dividends, margins, and more
- **Stock Comparison**: Side-by-side comparison of multiple stocks
- **Sector Discovery**: Find top stocks by sector or industry
- **Analyst Recommendations**: Ratings, price targets, and sentiment
- **Stock News**: Recent news articles for any stock
- **Valuation Analysis**: Buy/hold/sell signals with reasoning

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run interactive mode
python main.py

# Run single query
python main.py -q "What are the top technology stocks?"
```

### API Usage

```bash
# Get stock quote
curl -X POST https://7rt87itzf9.execute-api.us-east-1.amazonaws.com \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the current price of AAPL?"}'

# Compare stocks
curl -X POST https://7rt87itzf9.execute-api.us-east-1.amazonaws.com \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Compare MSFT and GOOGL"}'

# Get sector recommendations
curl -X POST https://7rt87itzf9.execute-api.us-east-1.amazonaws.com \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the best healthcare stocks?"}'
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `AWS_REGION` | us-east-1 | AWS region for Bedrock |
| `BEDROCK_MODEL_ID` | us.amazon.nova-pro-v1:0 | Bedrock model to use |
| `AGENT_MAX_TOKENS` | 4096 | Maximum response tokens |
| `AGENT_TEMPERATURE` | 0.7 | Model temperature |

## Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/stock_agent
```

## AWS Resources

| Resource | Name | Purpose |
|----------|------|---------|
| Lambda Function | `stock-ai-agent` | Runs the agent |
| Lambda Layer | `stock-agent-dependencies` | Python dependencies |
| API Gateway | `stock-ai-agent-api` | HTTP endpoint |
| IAM Role | `stock-agent-lambda-role` | Permissions |
| S3 Bucket | `stock-agent-lambda-deploy-*` | Deployment artifacts |

## License

MIT

"""Stock AI Agent using AWS Strands Agents SDK with Bedrock."""

import logging
from typing import Any

from strands import Agent
from strands.models import BedrockModel

from stock_agent.config import AgentConfig
from stock_agent.tools.analysis_tools import (
    analyze_stock_value,
    get_analyst_recommendations,
    get_stock_news,
)
from stock_agent.tools.sector_tools import (
    get_stocks_by_industry,
    get_stocks_by_sector,
    list_industries_in_sector,
)
from stock_agent.tools.stock_tools import (
    compare_stocks,
    get_stock_history,
    get_stock_metrics,
    get_stock_quote,
)

logger = logging.getLogger(__name__)

# All available tools for the stock agent
STOCK_AGENT_TOOLS = [
    # Sector tools
    get_stocks_by_sector,
    get_stocks_by_industry,
    list_industries_in_sector,
    # Stock tools
    get_stock_quote,
    get_stock_metrics,
    compare_stocks,
    get_stock_history,
    # Analysis tools
    get_analyst_recommendations,
    get_stock_news,
    analyze_stock_value,
]


def create_stock_agent(config: AgentConfig | None = None) -> Agent:
    """Create and configure the Stock AI Agent.

    Args:
        config: Optional AgentConfig instance. If not provided, uses defaults.

    Returns:
        Configured Agent instance ready to process queries.
    """
    if config is None:
        config = AgentConfig()

    logger.info(f"Creating Stock Agent with model: {config.model_id}")

    # Create Bedrock model
    model = BedrockModel(
        model_id=config.model_id,
        region_name=config.aws_region,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
    )

    # Create and configure the agent
    agent = Agent(
        model=model,
        system_prompt=config.system_prompt,
        tools=STOCK_AGENT_TOOLS,
    )

    logger.info("Stock Agent created successfully")
    return agent


def run_query(agent: Agent, query: str) -> str:
    """Run a query against the stock agent and return the response.

    Args:
        agent: The configured stock agent
        query: User's question or request

    Returns:
        The agent's response as a string
    """
    logger.info(f"Processing query: {query[:100]}...")

    result = agent(query)

    # Extract the text response
    if hasattr(result, "message"):
        return str(result.message)
    return str(result)


def get_agent_info() -> dict[str, Any]:
    """Get information about the stock agent configuration.

    Returns:
        Dictionary with agent configuration details
    """
    config = AgentConfig()
    return {
        "model_id": config.model_id,
        "aws_region": config.aws_region,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "available_tools": [tool.__name__ for tool in STOCK_AGENT_TOOLS],
    }

"""AWS Lambda handler for the Stock AI Agent."""

import json
import logging
import os
import sys
from typing import Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from stock_agent.agent import create_stock_agent, run_query
from stock_agent.config import AgentConfig

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize agent outside handler for connection reuse
_agent = None


def get_agent():
    """Get or create the stock agent (singleton pattern for Lambda warm starts)."""
    global _agent
    if _agent is None:
        config = AgentConfig()
        _agent = create_stock_agent(config)
        logger.info("Stock Agent initialized")
    return _agent


def create_response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    """Create a properly formatted API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps(body),
    }


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler for API Gateway requests.

    Expected request body:
    {
        "prompt": "What are the top technology stocks?"
    }

    Returns:
    {
        "response": "Agent's response text",
        "request_id": "Lambda request ID"
    }
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return create_response(200, {"message": "OK"})

    try:
        # Parse request body
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)

        prompt = body.get("prompt")

        if not prompt:
            return create_response(400, {
                "error": "Missing required field: prompt",
                "usage": {"prompt": "Your question about stocks"},
            })

        # Get or create agent
        agent = get_agent()

        # Process the query
        logger.info(f"Processing prompt: {prompt[:100]}...")
        response = run_query(agent, prompt)

        return create_response(200, {
            "response": response,
            "request_id": context.aws_request_id if context else "local",
        })

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {e}")
        return create_response(400, {
            "error": "Invalid JSON in request body",
            "details": str(e),
        })

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return create_response(500, {
            "error": "Internal server error",
            "details": str(e),
            "request_id": context.aws_request_id if context else "local",
        })


def bedrock_agent_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handler for Bedrock AgentCore invocations.

    This handler is designed for integration with AWS Bedrock AgentCore,
    which has a different event format than API Gateway.

    Expected event format from AgentCore:
    {
        "inputText": "User's question",
        "sessionId": "session-123",
        "sessionAttributes": {}
    }
    """
    logger.info(f"Bedrock AgentCore event: {json.dumps(event)}")

    try:
        # Extract input text from AgentCore event
        input_text = event.get("inputText", "")

        if not input_text:
            return {
                "response": "Please provide a question about stocks.",
                "sessionAttributes": event.get("sessionAttributes", {}),
            }

        # Get or create agent
        agent = get_agent()

        # Process the query
        logger.info(f"Processing AgentCore input: {input_text[:100]}...")
        response = run_query(agent, input_text)

        return {
            "response": response,
            "sessionAttributes": event.get("sessionAttributes", {}),
        }

    except Exception as e:
        logger.error(f"Error in AgentCore handler: {e}", exc_info=True)
        return {
            "response": f"I encountered an error processing your request: {str(e)}",
            "sessionAttributes": event.get("sessionAttributes", {}),
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({"prompt": "What are the top 3 technology stocks?"}),
    }

    class MockContext:
        aws_request_id = "local-test-123"

    result = handler(test_event, MockContext())
    print(json.dumps(json.loads(result["body"]), indent=2))

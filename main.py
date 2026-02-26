#!/usr/bin/env python3
"""Local CLI for the Stock AI Agent."""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stock_agent.agent import create_stock_agent, get_agent_info, run_query
from stock_agent.config import AgentConfig


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)


def print_welcome() -> None:
    """Print welcome message and instructions."""
    print("\n" + "=" * 60)
    print("  Stock AI Agent - Powered by AWS Bedrock")
    print("=" * 60)
    print("\nI can help you with:")
    print("  - Finding stocks by sector or industry")
    print("  - Getting stock quotes and metrics")
    print("  - Comparing multiple stocks")
    print("  - Analyzing stock valuations")
    print("  - Viewing analyst recommendations")
    print("\nExample queries:")
    print('  "What are the top technology stocks?"')
    print('  "Recommend healthcare stocks with good dividends"')
    print('  "Compare AAPL, MSFT, and GOOGL"')
    print('  "What do analysts say about NVDA?"')
    print("\nType 'quit' or 'exit' to end the session.")
    print("Type 'info' to see agent configuration.")
    print("-" * 60 + "\n")


def run_single_query(query: str) -> None:
    """Run a single query and exit."""
    print(f"\nProcessing: {query}\n")
    config = AgentConfig()
    agent = create_stock_agent(config)
    response = run_query(agent, query)
    print(response)


def run_interactive() -> None:
    """Run interactive chat mode."""
    print_welcome()

    config = AgentConfig()
    print(f"Initializing agent with model: {config.model_id}")
    print("Please wait...\n")

    try:
        agent = create_stock_agent(config)
        print("Agent ready!\n")
    except Exception as e:
        print(f"\nError initializing agent: {e}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured")
        print("  2. Access to Bedrock in your AWS region")
        print("  3. The correct model ID in your configuration")
        sys.exit(1)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("\nGoodbye! Happy investing!")
                break

            if user_input.lower() == "info":
                info = get_agent_info()
                print("\nAgent Configuration:")
                for key, value in info.items():
                    if key == "available_tools":
                        print(f"  {key}:")
                        for tool in value:
                            print(f"    - {tool}")
                    else:
                        print(f"  {key}: {value}")
                continue

            if user_input.lower() == "help":
                print_welcome()
                continue

            print("\nAgent: ", end="", flush=True)
            response = run_query(agent, user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            print(f"\nError: {e}")
            print("Please try again with a different query.")


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Stock AI Agent - Get stock recommendations and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Start interactive mode
  %(prog)s -q "What are the top tech stocks?"
  %(prog)s --query "Compare AAPL and MSFT"
  %(prog)s --info                       # Show agent configuration
        """,
    )

    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Single query to run (non-interactive mode)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show agent configuration and exit",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.info:
        info = get_agent_info()
        print("\nStock AI Agent Configuration:")
        print("-" * 40)
        for key, value in info.items():
            if key == "available_tools":
                print(f"\n{key}:")
                for tool in value:
                    print(f"  - {tool}")
            else:
                print(f"{key}: {value}")
        return

    if args.query:
        run_single_query(args.query)
    else:
        run_interactive()


if __name__ == "__main__":
    main()

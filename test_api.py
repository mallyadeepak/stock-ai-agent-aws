#!/usr/bin/env python3
"""Test script for the deployed Stock AI Agent API."""

import json
import requests
import time

# API endpoint
API_URL = "https://7rt87itzf9.execute-api.us-east-1.amazonaws.com"


def test_api(prompt: str, description: str) -> dict:
    """Send a test request to the API."""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")
    print("-" * 60)

    start_time = time.time()

    try:
        response = requests.post(
            API_URL,
            json={"prompt": prompt},
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            print(f"Status: SUCCESS ({response.status_code})")
            print(f"Time: {elapsed:.2f}s")
            print(f"Request ID: {data.get('request_id', 'N/A')}")
            print("-" * 60)

            # Parse the response content
            response_text = data.get("response", "")
            if isinstance(response_text, str) and "content" in response_text:
                # Extract text from the response structure
                try:
                    parsed = eval(response_text)
                    if isinstance(parsed, dict) and "content" in parsed:
                        for item in parsed["content"]:
                            if "text" in item:
                                print("Response:")
                                print(item["text"][:500] + "..." if len(item["text"]) > 500 else item["text"])
                except:
                    print(f"Response: {response_text[:500]}...")
            else:
                print(f"Response: {response_text[:500]}...")

            return {"success": True, "time": elapsed, "data": data}
        else:
            print(f"Status: FAILED ({response.status_code})")
            print(f"Error: {response.text}")
            return {"success": False, "time": elapsed, "error": response.text}

    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"Status: TIMEOUT after {elapsed:.2f}s")
        return {"success": False, "time": elapsed, "error": "Timeout"}
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"Status: ERROR - {str(e)}")
        return {"success": False, "time": elapsed, "error": str(e)}


def run_all_tests():
    """Run all API tests."""
    print("\n" + "=" * 60)
    print("  Stock AI Agent API Tests")
    print("=" * 60)
    print(f"API Endpoint: {API_URL}")

    tests = [
        ("What is the current price of AAPL?", "Stock Quote"),
        ("Compare MSFT and GOOGL", "Stock Comparison"),
        ("What are the top 3 healthcare stocks?", "Sector Discovery"),
        ("What do analysts recommend for NVDA?", "Analyst Recommendations"),
        ("Get the stock metrics for TSLA", "Stock Metrics"),
    ]

    results = []

    for prompt, description in tests:
        result = test_api(prompt, description)
        results.append({
            "test": description,
            "success": result["success"],
            "time": result["time"]
        })

    # Print summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)

    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed

    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        print(f"  [{status}] {r['test']} ({r['time']:.2f}s)")

    print("-" * 60)
    print(f"  Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 60)

    return results


def test_single(prompt: str):
    """Run a single test with custom prompt."""
    return test_api(prompt, "Custom Query")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Run single test with provided prompt
        prompt = " ".join(sys.argv[1:])
        test_single(prompt)
    else:
        # Run all tests
        run_all_tests()

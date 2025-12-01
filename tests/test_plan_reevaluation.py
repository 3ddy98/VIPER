"""
Test plan reevaluation and adaptive execution
"""

import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.renderer import render_plan_update

def test_plan_update_rendering():
    """Test rendering of plan updates."""

    print("=" * 70)
    print("PLAN UPDATE RENDERING TEST")
    print("=" * 70)

    # Test 1: Plan with modified steps
    print("\n" + "=" * 70)
    print("TEST 1: Plan with modified steps")
    print("=" * 70)

    original_plan = {
        "name": "Data Analysis",
        "steps": [
            {
                "step_number": 1,
                "description": "Load data from CSV file",
                "tool": "FILE_EXPLORER__read_file",
                "arguments": '{"file_path": "data.csv"}'
            },
            {
                "step_number": 2,
                "description": "Process data with Python",
                "tool": "CODE_EXECUTION__execute",
                "arguments": '{"code": "process_data()"}'
            },
            {
                "step_number": 3,
                "description": "Save results to output file",
                "tool": "FILE_MANAGER__create_file",
                "arguments": '{"file_path": "output.txt", "content": "results"}'
            }
        ]
    }

    updated_plan = {
        "name": "Data Analysis",
        "steps": [
            {
                "step_number": 1,
                "description": "Load data from CSV file",
                "tool": "FILE_EXPLORER__read_file",
                "arguments": '{"file_path": "data.csv"}'
            },
            {
                "step_number": 2,
                "description": "Validate data format first",
                "tool": "DATA_VALIDATOR__validate",
                "arguments": '{"data": "csv_content"}'
            },
            {
                "step_number": 3,
                "description": "Process validated data with Python",
                "tool": "CODE_EXECUTION__execute",
                "arguments": '{"code": "process_data()"}'
            },
            {
                "step_number": 4,
                "description": "Save results to output file",
                "tool": "FILE_MANAGER__create_file",
                "arguments": '{"file_path": "output.txt", "content": "results"}'
            }
        ]
    }

    print("\nRendering plan update (added validation step):")
    render_plan_update(original_plan, updated_plan)

    print("\n✓ PASS: Plan update with added step rendered successfully\n")

    # Test 2: Plan with removed steps
    print("=" * 70)
    print("TEST 2: Plan with removed steps")
    print("=" * 70)

    recovery_plan = {
        "name": "Data Analysis - Recovery",
        "steps": [
            {
                "step_number": 1,
                "description": "Check if data file exists",
                "tool": "FILE_EXPLORER__list_directory",
                "arguments": '{"path": "."}'
            },
            {
                "step_number": 2,
                "description": "Create sample data file",
                "tool": "FILE_MANAGER__create_file",
                "arguments": '{"file_path": "data.csv", "content": "sample,data"}'
            }
        ]
    }

    print("\nRendering recovery plan (fewer steps):")
    render_plan_update(updated_plan, recovery_plan)

    print("\n✓ PASS: Recovery plan with removed steps rendered successfully\n")

    # Test 3: Completely different plan
    print("=" * 70)
    print("TEST 3: Completely different plan")
    print("=" * 70)

    alternative_plan = {
        "name": "Alternative Approach - Use Database",
        "steps": [
            {
                "step_number": 1,
                "description": "Connect to database",
                "tool": "DATABASE__connect",
                "arguments": '{"host": "localhost", "db": "analytics"}'
            },
            {
                "step_number": 2,
                "description": "Query data from table",
                "tool": "DATABASE__query",
                "arguments": '{"sql": "SELECT * FROM data"}'
            },
            {
                "step_number": 3,
                "description": "Process query results",
                "tool": "CODE_EXECUTION__execute",
                "arguments": '{"code": "process_results()"}'
            }
        ]
    }

    print("\nRendering alternative approach:")
    render_plan_update(original_plan, alternative_plan)

    print("\n✓ PASS: Alternative plan rendered successfully\n")

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\n✓ All plan update rendering tests passed!")
    print("\nTest coverage:")
    print("✓ Plan with added steps (validation)")
    print("✓ Plan with removed steps (recovery)")
    print("✓ Plan name change")
    print("✓ Completely different approach")


def test_decision_format():
    """Test the DECISION format parsing."""

    print("\n" + "=" * 70)
    print("DECISION FORMAT TEST")
    print("=" * 70)

    # Test examples of different decision formats
    decisions = [
        {
            "name": "CONTINUE decision",
            "response": """THOUGHT: The step executed successfully and returned the expected data. The remaining steps in the plan are still valid.
DECISION: CONTINUE
REASON: Data loaded successfully, proceeding with existing plan"""
        },
        {
            "name": "UPDATE_PLAN decision",
            "response": """THOUGHT: Step failed because file doesn't exist. Need to create it first.
DECISION: UPDATE_PLAN
REASON: File missing, adding step to create it
PLAN: Data Analysis - With File Creation
STEP: Create missing data file
TOOL: FILE_MANAGER__create_file
ARGS: {"file_path": "data.csv", "content": "sample,data"}
STEP: Load data from CSV file
TOOL: FILE_EXPLORER__read_file
ARGS: {"file_path": "data.csv"}"""
        },
        {
            "name": "COMPLETE decision",
            "response": """THOUGHT: The first step already returned all the information needed to answer the user's question.
DECISION: COMPLETE
REASON: User's question already answered from step 1 results"""
        },
        {
            "name": "ABORT decision",
            "response": """THOUGHT: The API endpoint is completely unavailable and there's no alternative data source.
DECISION: ABORT
REASON: API unavailable, no way to proceed"""
        }
    ]

    for decision in decisions:
        print(f"\n{decision['name']}:")
        print("-" * 70)
        print(decision['response'])
        print("-" * 70)

    print("\n✓ All decision formats documented\n")


if __name__ == "__main__":
    test_plan_update_rendering()
    test_decision_format()

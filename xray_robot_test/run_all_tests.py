#!/usr/bin/env python3
"""
Master script to run all test steps in sequence.
This automates the entire testing workflow.
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_path, script_name):
    """Run a Python script and handle output"""
    print("\n" + "=" * 80)
    print(f"🚀 Running: {script_name}")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent.parent,
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully")
            return True
        else:
            print(f"\n❌ {script_name} failed with exit code {result.returncode}")
            return False

    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("🧪 XRAY ROBOT FRAMEWORK IMPORT - FULL TEST SUITE")
    print("=" * 80)
    print("\nThis script will run all test steps in sequence:")
    print("  1. Authentication (get bearer token)")
    print("  2. Project inspection (analyze issue types and fields)")
    print("  3. Import testing (test different scenarios)")
    print("\n" + "=" * 80)

    scripts_dir = Path(__file__).parent / "scripts"

    # Define scripts to run
    test_steps = [
        (scripts_dir / "1_authenticate.py", "Step 1: Authentication"),
        (scripts_dir / "2_inspect_project.py", "Step 2: Project Inspection"),
        (scripts_dir / "3_test_import.py", "Step 3: Import Testing"),
    ]

    # Track results
    results = []

    # Run each script
    for script_path, script_name in test_steps:
        if not script_path.exists():
            print(f"\n❌ Script not found: {script_path}")
            results.append((script_name, False))
            continue

        success = run_script(script_path, script_name)
        results.append((script_name, success))

        # Stop if a critical step fails
        if not success and script_name in ["Step 1: Authentication"]:
            print(f"\n❌ Critical step failed: {script_name}")
            print(f"   Cannot continue without authentication.")
            break

    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)

    for step_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {step_name}")

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)

    print(f"\n📈 Overall: {success_count}/{total_count} steps completed successfully")

    print("\n" + "=" * 80)
    print("✅ Test Suite Execution Complete!")
    print("=" * 80)
    print(f"\n📁 Results saved in: {Path(__file__).parent / 'results'}")
    print(f"📋 Review 'import_test_results.json' for detailed findings")


if __name__ == "__main__":
    main()

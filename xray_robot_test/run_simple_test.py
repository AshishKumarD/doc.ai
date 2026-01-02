#!/usr/bin/env python3
"""
Simplified test script - Only tests Xray Cloud API (no Jira URL needed)
This is the quickest way to reproduce the import issue.
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
    print("🧪 XRAY ROBOT FRAMEWORK IMPORT - SIMPLE TEST")
    print("=" * 80)
    print("\n✨ This test uses ONLY Xray Cloud endpoints - NO Jira URL needed!")
    print("\nSteps:")
    print("  1. Authentication (Xray Cloud API)")
    print("  2. Import testing (test different scenarios)")
    print("\n⏭️  Skipping: Project inspection (not needed for reproduction)")
    print("\n" + "=" * 80)

    scripts_dir = Path(__file__).parent / "scripts"

    # Only run auth and import tests (skip inspection)
    test_steps = [
        (scripts_dir / "1_authenticate.py", "Step 1: Authentication"),
        (scripts_dir / "3_test_import.py", "Step 2: Import Testing"),
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

        # Stop if authentication fails
        if not success and script_name == "Step 1: Authentication":
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
    print("✅ Test Complete!")
    print("=" * 80)
    print(f"\n📁 Results saved in: {Path(__file__).parent / 'results'}")
    print(f"📋 Review 'import_test_results.json' for detailed findings")

    print("\n" + "=" * 80)
    print("📌 KEY FILES TO CHECK:")
    print("=" * 80)
    print(f"  1. results/import_test_results.json - Which scenarios passed/failed")
    print(f"  2. Console output above - Detailed error messages")
    print(f"\n💡 If you want project inspection, run: python scripts/2_inspect_project.py")


if __name__ == "__main__":
    main()

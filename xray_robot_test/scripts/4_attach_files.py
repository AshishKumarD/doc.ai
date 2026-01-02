#!/usr/bin/env python3
"""
Script to attach files to Xray Test Runs and test size limits.
Tests attachment of files smaller and larger than 10MB.
"""

import json
import requests
import sys
import base64
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def load_token():
    """Load saved authentication token"""
    token_path = Path(__file__).parent.parent / "results" / "auth_token.json"
    try:
        with open(token_path, 'r') as f:
            data = json.load(f)
            return data['token']
    except FileNotFoundError:
        print("❌ Token file not found. Please run 1_authenticate.py first.")
        sys.exit(1)


def format_file_size(size_bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_test_runs_from_issue(jira_url, token, issue_key):
    """Get test runs from a test execution issue using Xray GraphQL API"""
    print("\n" + "=" * 70)
    print(f"Fetching Test Runs from {issue_key}")
    print("=" * 70)

    # Use GraphQL to get test runs
    graphql_url = "https://xray.cloud.getxray.app/api/v2/graphql"

    # Try using getTestExecutions with a filter by jira key
    query = """
    query {
        getTestExecutions(jql: "key = %s", limit: 1) {
            results {
                issueId
                jira(fields: ["key"])
                testRuns(limit: 100) {
                    results {
                        id
                        status {
                            name
                        }
                        test {
                            issueId
                            jira(fields: ["key"])
                        }
                    }
                }
            }
        }
    }
    """ % issue_key

    print(f"\n📡 POST {graphql_url}")
    print(f"Query: Fetching test runs for {issue_key}")

    try:
        response = requests.post(
            graphql_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"query": query}
        )

        print(f"✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Debug: print full response
            print(f"\n🔍 GraphQL Response:")
            print(json.dumps(data, indent=2))

            if 'errors' in data:
                print(f"❌ GraphQL Errors: {data['errors']}")
                return None

            test_executions = data.get('data', {}).get('getTestExecutions', {}).get('results', [])
            if not test_executions or len(test_executions) == 0:
                print(f"❌ No test execution found for {issue_key}")
                return None

            test_execution = test_executions[0]
            test_runs = test_execution.get('testRuns', {}).get('results', [])

            if test_runs:
                print(f"\n📋 Found {len(test_runs)} test runs:")
                for i, tr in enumerate(test_runs, 1):
                    test_key = tr.get('test', {}).get('jira', {}).get('key', 'Unknown')
                    status = tr.get('status', {}).get('name', 'Unknown')
                    print(f"   {i}. Test Run ID: {tr['id']}")
                    print(f"      Test: {test_key}, Status: {status}")
            else:
                print(f"\n📭 No test runs found in this test execution")

            return test_runs
        else:
            print(f"❌ Failed to fetch test runs")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def attach_file_to_testrun(token, testrun_id, file_path):
    """Attach a file (evidence) to a Test Run using Xray Cloud GraphQL API"""
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    file_size = file_path.stat().st_size
    file_size_formatted = format_file_size(file_size)

    print("\n" + "=" * 70)
    print(f"Attaching File to Test Run {testrun_id}")
    print("=" * 70)
    print(f"\n📎 File: {file_path.name}")
    print(f"📏 Size: {file_size_formatted} ({file_size:,} bytes)")

    # Use Xray Cloud GraphQL API
    graphql_url = "https://xray.cloud.getxray.app/api/v2/graphql"
    print(f"\n📡 POST {graphql_url}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        # Read file and encode to base64
        print(f"⏳ Encoding file to base64...")
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')

        # Determine MIME type
        mime_type = "application/octet-stream"
        if file_path.suffix == '.png':
            mime_type = "image/png"
        elif file_path.suffix == '.jpg' or file_path.suffix == '.jpeg':
            mime_type = "image/jpeg"
        elif file_path.suffix == '.txt':
            mime_type = "text/plain"

        # Create GraphQL mutation
        mutation = """
        mutation {
            addEvidenceToTestRun(
                id: "%s",
                evidence: [
                    {
                        data: "%s",
                        filename: "%s",
                        mimeType: "%s"
                    }
                ]
            ) {
                addedEvidence
                warnings
            }
        }
        """ % (testrun_id, base64_data, file_path.name, mime_type)

        print(f"⏳ Uploading...")
        response = requests.post(
            graphql_url,
            headers=headers,
            json={"query": mutation},
            timeout=120  # 2 minute timeout for large files
        )

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            print(f"📋 Response:")
            print(json.dumps(response_data, indent=2))

            # Check for GraphQL errors
            if 'errors' in response_data:
                print(f"\n❌ FAILED - GraphQL Errors:")
                for error in response_data['errors']:
                    print(f"   - {error.get('message', error)}")
                return None

            # Success
            mutation_result = response_data.get('data', {}).get('addEvidenceToTestRun', {})
            added_evidence = mutation_result.get('addedEvidence', [])
            warnings = mutation_result.get('warnings', [])

            print(f"\n🎉 SUCCESS! File attached successfully")
            print(f"   - Added Evidence Count: {len(added_evidence)}")

            if warnings:
                print(f"\n⚠️  Warnings:")
                for warning in warnings:
                    print(f"   - {warning}")

            return response_data
        else:
            print(f"\n❌ FAILED to attach file")
            print(f"📋 Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 2 minutes")
        print(f"   File size: {file_size_formatted}")
        print(f"   This might indicate the file is too large or network issues")
        return None
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        return None


def main():
    """Main execution"""
    print("\n📎 Xray Test Run Attachment Upload Test Script")
    print("=" * 70)

    # Load config and token
    config = load_config()
    token = load_token()
    jira_url = config.get('jira_url', 'https://ashishkumard1098.atlassian.net')

    # Test issue key (Test Execution)
    issue_key = "XSP-69"

    print(f"\n🎯 Target Test Execution: {issue_key}")
    print(f"🔗 Jira URL: {jira_url}")

    # Get test runs from the test execution
    test_runs = get_test_runs_from_issue(jira_url, token, issue_key)

    if not test_runs or len(test_runs) == 0:
        print("\n❌ No test runs found. Cannot attach files.")
        print("💡 Make sure XSP-10 is a Test Execution issue with test runs.")
        sys.exit(1)

    # Use the first test run
    testrun_id = test_runs[0]['id']
    test_key = test_runs[0].get('test', {}).get('jira', {}).get('key', 'Unknown')
    print(f"\n✅ Using Test Run ID: {testrun_id} (Test: {test_key})")

    # Define test files
    base_path = Path(__file__).parent.parent
    test_files = [
        {
            "path": base_path / "test_file_small.bin",
            "description": "Small binary file (< 10MB, 5MB)"
        },
        {
            "path": base_path / "test_file_large.bin",
            "description": "Large binary file (> 10MB, 15MB)"
        }
    ]

    # Track results
    results = []

    # Test each file
    for i, test_file in enumerate(test_files, 1):
        file_path = test_file["path"]
        description = test_file["description"]

        print(f"\n{'='*70}")
        print(f"TEST {i}/2: {description}")
        print(f"{'='*70}")

        result = attach_file_to_testrun(token, testrun_id, file_path)

        results.append({
            "file": str(file_path),
            "description": description,
            "success": result is not None,
            "result": result
        })

        # Small delay between uploads
        if i < len(test_files):
            import time
            time.sleep(2)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for i, result in enumerate(results, 1):
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"\n{i}. {result['description']}")
        print(f"   File: {Path(result['file']).name}")
        print(f"   Status: {status}")

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "attachment_test_results.json"
    with open(output_path, 'w') as f:
        json.dump({
            "issue_key": issue_key,
            "testrun_id": testrun_id,
            "tests": results
        }, f, indent=2)

    print(f"\n💾 Results saved to: {output_path}")

    print("\n" + "=" * 70)
    print("✅ Attachment Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

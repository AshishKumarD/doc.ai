#!/usr/bin/env python3
"""
Script to test Robot Framework import with different info.json configurations.
This will help reproduce and diagnose the testPlanKey field error.
"""

import json
import requests
import sys
import time
from pathlib import Path
from datetime import datetime

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


def test_simple_endpoint(token, base_url, robot_xml_path, project_key, test_plan_key):
    """Test the simple endpoint that works (for comparison)"""
    print("\n" + "=" * 70)
    print("TEST 0: Simple Endpoint (User's Working Method)")
    print("=" * 70)

    endpoint = f"{base_url}/import/execution/robot"
    params = {
        "projectKey": project_key,
        "testPlanKey": test_plan_key
    }

    print(f"\n📡 POST {endpoint}")
    print(f"📦 Params: {params}")
    print(f"📄 XML File: {robot_xml_path.name}")

    with open(robot_xml_path, 'rb') as f:
        xml_content = f.read()

    try:
        response = requests.post(
            endpoint,
            params=params,
            files={'file': ('output.xml', xml_content, 'application/xml')},
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCESS!")
            print(f"   - Test Execution Created: {result.get('key')}")
            print(f"   - ID: {result.get('id')}")
            print(f"   - Self: {result.get('self')}")
            return True, result
        else:
            print(f"❌ FAILED!")
            print(f"Response: {response.text}")
            return False, response.text

    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)


def test_multipart_import(token, base_url, robot_xml_path, info_json_path, scenario_name):
    """Test multipart import with a specific info.json configuration"""
    print("\n" + "=" * 70)
    print(f"TEST: {scenario_name}")
    print("=" * 70)

    endpoint = f"{base_url}/import/execution/robot/multipart"

    print(f"\n📡 POST {endpoint}")
    print(f"📄 XML File: {robot_xml_path.name}")
    print(f"📄 Info JSON: {info_json_path.name}")

    # Load and display info.json
    with open(info_json_path, 'r') as f:
        info_data = json.load(f)

    print(f"\n📋 Info JSON Content:")
    print(json.dumps(info_data, indent=2))

    # Prepare files for multipart upload
    with open(robot_xml_path, 'rb') as xml_file:
        xml_content = xml_file.read()

    with open(info_json_path, 'r') as info_file:
        info_content = info_file.read()

    files = {
        'results': ('output.xml', xml_content, 'application/xml'),
        'info': ('info.json', info_content, 'application/json')
    }

    try:
        response = requests.post(
            endpoint,
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCESS!")
            print(f"   - Test Execution Created: {result.get('key')}")
            print(f"   - ID: {result.get('id')}")
            print(f"   - Self: {result.get('self')}")
            return True, result
        else:
            print(f"❌ FAILED!")
            print(f"Response Body:")
            print(response.text)

            # Try to parse error
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"\n🔍 Error Details:")
                    print(f"   {error_data['error']}")
            except:
                pass

            return False, response.text

    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)


def update_project_id_in_scenario4(config):
    """Update scenario 4 template with actual project ID"""
    scenario4_path = Path(__file__).parent.parent / "templates" / "info_scenario4_project_id.json"

    # Load project info to get ID
    project_info_path = Path(__file__).parent.parent / "results" / "project_info.json"

    if project_info_path.exists():
        with open(project_info_path, 'r') as f:
            project_info = json.load(f)
            project_id = project_info.get('id')

        if project_id:
            with open(scenario4_path, 'r') as f:
                scenario4_data = json.load(f)

            scenario4_data['fields']['project']['id'] = project_id

            with open(scenario4_path, 'w') as f:
                json.dump(scenario4_data, f, indent=2)

            print(f"✅ Updated Scenario 4 with Project ID: {project_id}")
    else:
        print(f"⚠️  Project info not found. Run 2_inspect_project.py first for Scenario 4.")


def main():
    """Main execution"""
    print("\n🧪 Xray Robot Framework Import Test Suite")
    print("=" * 70)
    print(f"📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load config and token
    config = load_config()
    token = load_token()
    base_url = config['xray_cloud']['base_url']
    project_key = config['test_config']['project_key']
    test_plan_key = config['test_config']['test_plan_key']

    # File paths
    robot_xml_path = Path(__file__).parent.parent / "templates" / "sample_robot_output.xml"
    templates_dir = Path(__file__).parent.parent / "templates"

    # Update Scenario 4 with actual project ID
    update_project_id_in_scenario4(config)

    # Test scenarios
    scenarios = [
        ("Scenario 1: testPlanKey as Array (Expected to Fail)", "info_scenario1_array_testplan.json"),
        ("Scenario 2: xrayFields with String testPlanKey", "info_scenario2_xrayfields_string.json"),
        ("Scenario 3: Issue Type Name Instead of ID", "info_scenario3_issuetype_name.json"),
        ("Scenario 4: Project ID + xrayFields", "info_scenario4_project_id.json"),
        ("Scenario 5: No testPlanKey (Control Test)", "info_scenario5_no_testplan.json"),
    ]

    # Results tracking
    results = []

    # Test simple endpoint first (the one that works)
    print("\n" + "=" * 70)
    print("PHASE 0: Testing Simple Endpoint (Baseline)")
    print("=" * 70)

    success, result = test_simple_endpoint(
        token, base_url, robot_xml_path, project_key, test_plan_key
    )
    results.append(("Simple Endpoint (Working Method)", success, result))

    time.sleep(2)  # Wait between requests

    # Test multipart endpoint with different scenarios
    print("\n" + "=" * 70)
    print("PHASE 1: Testing Multipart Endpoint with Different Configurations")
    print("=" * 70)

    for scenario_name, info_json_file in scenarios:
        info_json_path = templates_dir / info_json_file

        if not info_json_path.exists():
            print(f"\n⚠️  Skipping: {info_json_path.name} not found")
            continue

        success, result = test_multipart_import(
            token, base_url, robot_xml_path, info_json_path, scenario_name
        )
        results.append((scenario_name, success, result))

        time.sleep(2)  # Wait between requests

    # Summary Report
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    for i, (name, success, result) in enumerate(results, 1):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{i}. {name}")
        print(f"   Status: {status}")
        if success and isinstance(result, dict):
            print(f"   Created: {result.get('key')}")
        elif not success:
            # Show first 100 chars of error
            error_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            print(f"   Error: {error_preview}")

    print(f"\n" + "=" * 70)
    print(f"📈 Overall: {success_count}/{total_count} tests passed")
    print("=" * 70)

    # Save results
    results_output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total_count,
            "passed": success_count,
            "failed": total_count - success_count
        },
        "tests": [
            {
                "name": name,
                "success": success,
                "result": result if isinstance(result, dict) else str(result)
            }
            for name, success, result in results
        ]
    }

    output_path = Path(__file__).parent.parent / "results" / "import_test_results.json"
    with open(output_path, 'w') as f:
        json.dump(results_output, f, indent=2)

    print(f"\n💾 Detailed results saved to: {output_path}")

    print("\n" + "=" * 70)
    print("✅ Test Suite Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

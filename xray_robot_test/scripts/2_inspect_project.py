#!/usr/bin/env python3
"""
Script to inspect Jira project and get issue type details.
Helps identify the correct Test Execution issue type ID and configuration.
"""

import json
import requests
import sys
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


def get_jira_url():
    """Prompt user for Jira instance URL"""
    print("\n" + "=" * 70)
    print("Jira Instance Configuration")
    print("=" * 70)
    print("\n📝 Please enter your Jira instance URL")
    print("   Example: https://your-domain.atlassian.net")

    jira_url = input("\n🔗 Jira URL: ").strip()

    # Clean up URL
    if jira_url.endswith('/'):
        jira_url = jira_url[:-1]

    if not jira_url.startswith('http'):
        jira_url = f"https://{jira_url}"

    print(f"\n✅ Using: {jira_url}")
    return jira_url


def get_project_info(jira_url, token, project_key):
    """Get project information"""
    print("\n" + "=" * 70)
    print(f"STEP 1: Fetching Project Info for '{project_key}'")
    print("=" * 70)

    endpoint = f"{jira_url}/rest/api/2/project/{project_key}"
    print(f"\n📡 GET {endpoint}")

    try:
        response = requests.get(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        print(f"✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            project_data = response.json()
            print(f"\n📊 Project Details:")
            print(f"   - Name: {project_data.get('name')}")
            print(f"   - Key: {project_data.get('key')}")
            print(f"   - ID: {project_data.get('id')}")
            print(f"   - Type: {project_data.get('projectTypeKey')}")

            # List issue types
            if 'issueTypes' in project_data:
                print(f"\n📋 Issue Types in Project:")
                for issue_type in project_data['issueTypes']:
                    icon = "🧪" if "Test" in issue_type['name'] else "📄"
                    print(f"   {icon} {issue_type['name']}")
                    print(f"      - ID: {issue_type['id']}")
                    print(f"      - Subtask: {issue_type.get('subtask', False)}")
                    print()

            return project_data
        else:
            print(f"❌ Failed to get project info")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_create_meta(jira_url, token, project_key):
    """Get create metadata to see which fields are available"""
    print("\n" + "=" * 70)
    print("STEP 2: Fetching Create Metadata (Available Fields)")
    print("=" * 70)

    endpoint = f"{jira_url}/rest/api/2/issue/createmeta"
    params = {
        "projectKeys": project_key,
        "expand": "projects.issuetypes.fields"
    }

    print(f"\n📡 GET {endpoint}")
    print(f"📦 Params: {params}")

    try:
        response = requests.get(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params=params
        )

        print(f"✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            meta_data = response.json()

            # Save full metadata
            meta_output_path = Path(__file__).parent.parent / "results" / "create_meta.json"
            with open(meta_output_path, 'w') as f:
                json.dump(meta_data, f, indent=2)
            print(f"\n💾 Full metadata saved to: {meta_output_path}")

            # Analyze Test Execution fields
            if 'projects' in meta_data and len(meta_data['projects']) > 0:
                project = meta_data['projects'][0]

                for issue_type in project.get('issuetypes', []):
                    if 'Test Execution' in issue_type['name'] or 'execution' in issue_type['name'].lower():
                        print(f"\n🧪 Found Test Execution Type: {issue_type['name']}")
                        print(f"   - ID: {issue_type['id']}")
                        print(f"\n📝 Available Fields for Test Execution:")

                        fields = issue_type.get('fields', {})
                        xray_fields = []

                        for field_key, field_info in fields.items():
                            field_name = field_info.get('name', field_key)
                            required = "⚠️  REQUIRED" if field_info.get('required') else "Optional"

                            # Highlight Xray-specific fields
                            if 'xray' in field_key.lower() or 'test' in field_name.lower():
                                xray_fields.append((field_key, field_name, field_info))
                                print(f"   🎯 {field_name} ({field_key}) - {required}")

                        if xray_fields:
                            print(f"\n🎯 Xray-Related Fields Found: {len(xray_fields)}")
                        else:
                            print(f"\n⚠️  No Xray-specific fields found in metadata")
                            print(f"   This might indicate a screen configuration issue")

            return meta_data
        else:
            print(f"❌ Failed to get create metadata")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_issue_type_screens(jira_url, token, issue_type_id):
    """Get screen information for a specific issue type"""
    print("\n" + "=" * 70)
    print(f"STEP 3: Analyzing Screens for Issue Type ID: {issue_type_id}")
    print("=" * 70)

    # Note: This endpoint might require admin permissions
    endpoint = f"{jira_url}/rest/api/2/screens"

    print(f"\n📡 GET {endpoint}")
    print("⚠️  Note: This may require admin permissions")

    try:
        response = requests.get(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        print(f"✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            screens_data = response.json()
            print(f"\n📺 Found {len(screens_data.get('values', []))} screens")
            return screens_data
        elif response.status_code == 403:
            print(f"\n⚠️  Forbidden: You need admin permissions to view screens")
            print(f"   This is OK - we can still test the import")
            return None
        else:
            print(f"❌ Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main execution"""
    print("\n🔍 Xray Project Inspection Script")
    print("=" * 70)

    # Load config and token
    config = load_config()
    token = load_token()
    project_key = config['test_config']['project_key']
    issue_type_id = config['test_config']['test_execution_issue_type_id']

    # Get Jira URL
    jira_url = get_jira_url()

    # Save Jira URL to config for future use
    config['jira_url'] = jira_url
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"💾 Jira URL saved to config")

    # Get project info
    project_info = get_project_info(jira_url, token, project_key)
    if project_info:
        output_path = Path(__file__).parent.parent / "results" / "project_info.json"
        with open(output_path, 'w') as f:
            json.dump(project_info, f, indent=2)

    # Get create metadata
    create_meta = get_create_meta(jira_url, token, project_key)

    # Try to get screen info (might fail without admin perms)
    analyze_issue_type_screens(jira_url, token, issue_type_id)

    print("\n" + "=" * 70)
    print("✅ Project Inspection Complete!")
    print("=" * 70)
    print(f"\n💡 Next step: Review the metadata in results/ folder")
    print(f"💡 Then run '3_test_import.py' to test the import")


if __name__ == "__main__":
    main()

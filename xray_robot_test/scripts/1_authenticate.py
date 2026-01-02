#!/usr/bin/env python3
"""
Script to authenticate with Xray Cloud API and get bearer token.
Also fetches user details from Jira API.
"""

import json
import requests
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def get_xray_token(client_id, client_secret, auth_url):
    """Authenticate with Xray Cloud and get bearer token"""
    print("=" * 70)
    print("STEP 1: Authenticating with Xray Cloud API")
    print("=" * 70)

    payload = {
        "client_id": client_id,
        "client_secret": client_secret
    }

    print(f"\n📡 POST {auth_url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            auth_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            token = response.text.strip('"')  # Remove quotes from token
            print(f"🎟️  Token received: {token[:50]}...{token[-10:]}")
            print(f"📏 Token length: {len(token)} characters")
            return token
        else:
            print(f"❌ Authentication failed!")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return None


def get_jira_instance_url(token):
    """Try to determine the Jira instance URL from token or config"""
    # For Xray Cloud, we need the actual Jira instance URL
    # This will need to be provided by the user
    print("\n" + "=" * 70)
    print("STEP 2: Determine Jira Instance URL")
    print("=" * 70)
    print("\n⚠️  For user details, we need your Jira instance URL")
    print("Example: https://your-domain.atlassian.net")
    return None


def get_user_details(jira_url, token):
    """Get current user details from Jira API"""
    if not jira_url:
        print("\n⏭️  Skipping user details (Jira URL not provided)")
        return None

    print("\n" + "=" * 70)
    print("STEP 3: Fetching User Details")
    print("=" * 70)

    endpoint = f"{jira_url}/rest/api/2/myself"

    print(f"\n📡 GET {endpoint}")

    try:
        response = requests.get(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        print(f"\n✅ Status Code: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            print(f"\n👤 User Details:")
            print(f"   - Name: {user_data.get('displayName')}")
            print(f"   - Email: {user_data.get('emailAddress')}")
            print(f"   - Account ID: {user_data.get('accountId')}")
            print(f"   - Active: {user_data.get('active')}")
            return user_data
        else:
            print(f"❌ Failed to get user details")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error fetching user details: {e}")
        return None


def save_token(token, output_path):
    """Save token to file for use by other scripts"""
    data = {
        "token": token,
        "token_preview": f"{token[:50]}...{token[-10:]}"
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Token saved to: {output_path}")


def main():
    """Main execution"""
    print("\n🚀 Xray Cloud Authentication Script")
    print("=" * 70)

    # Load configuration
    config = load_config()
    xray_config = config['xray_cloud']

    # Authenticate with Xray
    token = get_xray_token(
        xray_config['client_id'],
        xray_config['client_secret'],
        xray_config['auth_url']
    )

    if not token:
        print("\n❌ Authentication failed. Exiting.")
        sys.exit(1)

    # Save token for other scripts
    output_path = Path(__file__).parent.parent / "results" / "auth_token.json"
    save_token(token, output_path)

    # Try to get Jira instance URL (this will need user input)
    jira_url = get_jira_instance_url(token)

    # Get user details if Jira URL is available
    if jira_url:
        user_data = get_user_details(jira_url, token)
        if user_data:
            user_output_path = Path(__file__).parent.parent / "results" / "user_details.json"
            with open(user_output_path, 'w') as f:
                json.dump(user_data, f, indent=2)
            print(f"💾 User details saved to: {user_output_path}")

    print("\n" + "=" * 70)
    print("✅ Authentication Complete!")
    print("=" * 70)
    print(f"\n💡 Next step: Run '2_inspect_project.py' to inspect your project")


if __name__ == "__main__":
    main()

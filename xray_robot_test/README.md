# Xray Robot Framework Import Test Suite

This test suite helps reproduce and diagnose the issue with importing Robot Framework test results to Xray Cloud using the multipart endpoint with `testPlanKey` field.

## Problem Description

When trying to associate a Test Execution with a Test Plan using the `/api/v2/import/execution/robot/multipart` endpoint, different configurations of `info.json` produce different errors:

1. **Issue 1**: Using `testPlanKey` as an array `["XSP-100"]` instead of string
2. **Issue 2**: Using correct format but getting error: "Field 'xrayFields' cannot be set. It is not on the appropriate screen, or unknown."

## Project Structure

```
xray_robot_test/
├── config.json                    # Configuration with credentials
├── scripts/
│   ├── 1_authenticate.py          # Get bearer token from Xray API
│   ├── 2_inspect_project.py       # Inspect project and issue types
│   └── 3_test_import.py           # Test different import scenarios
├── templates/
│   ├── sample_robot_output.xml    # Sample Robot Framework XML output
│   ├── info_scenario1_array_testplan.json     # Scenario 1: Array format (wrong)
│   ├── info_scenario2_xrayfields_string.json  # Scenario 2: xrayFields (correct)
│   ├── info_scenario3_issuetype_name.json     # Scenario 3: Issue type name
│   ├── info_scenario4_project_id.json         # Scenario 4: Project ID
│   └── info_scenario5_no_testplan.json        # Scenario 5: No test plan
├── results/                       # Test results and logs
├── run_all_tests.py              # Master script to run everything
└── README.md                     # This file
```

## Prerequisites

- Python 3.7+
- `requests` library

Install dependencies:
```bash
pip install requests
```

## Configuration

The `config.json` file contains:
- **Xray Cloud API credentials** (client_id, client_secret)
- **Test configuration** (project key, test plan key, issue type ID)

**Current Configuration:**
- Project: `XSP`
- Test Plan: `XSP-100`
- Issue Type ID: `10858`

## How to Run

### Option 1: Run All Tests at Once (Recommended)

```bash
python run_all_tests.py
```

This will execute all three steps automatically:
1. Authenticate
2. Inspect project
3. Test imports

### Option 2: Run Individual Scripts

**Step 1: Authenticate**
```bash
python scripts/1_authenticate.py
```
This will:
- Authenticate with Xray Cloud API
- Get bearer token
- Save token to `results/auth_token.json`

**Step 2: Inspect Project** (requires Jira URL input)
```bash
python scripts/2_inspect_project.py
```
This will:
- Prompt for your Jira instance URL (e.g., https://your-domain.atlassian.net)
- Fetch project details
- List all issue types with their IDs
- Get create metadata (available fields)
- Save results to `results/` folder

**Step 3: Test Import Scenarios**
```bash
python scripts/3_test_import.py
```
This will:
- Test the simple endpoint (working baseline)
- Test 5 different multipart configurations
- Generate detailed results report
- Save results to `results/import_test_results.json`

## Test Scenarios

### Scenario 0: Simple Endpoint (Baseline)
- Uses: `/api/v2/import/execution/robot?projectKey=XSP&testPlanKey=XSP-100`
- Expected: ✅ SUCCESS (this is the user's current working method)
- Purpose: Verify API access and baseline functionality

### Scenario 1: testPlanKey as Array
- Format: `"testPlanKey": ["XSP-100"]` (in fields)
- Expected: ❌ FAIL - "Field 'testPlanKey' cannot be set"
- Purpose: Reproduce user's first error

### Scenario 2: xrayFields with String testPlanKey
- Format: `"xrayFields": { "testPlanKey": "XSP-100" }`
- Expected: ✅ SUCCESS or ❌ FAIL with screen error
- Purpose: Test documented format

### Scenario 3: Issue Type Name Instead of ID
- Format: `"issuetype": { "name": "Test Execution" }`
- Expected: ✅ SUCCESS (recommended approach)
- Purpose: Test if using name instead of ID resolves screen issue

### Scenario 4: Project ID + xrayFields
- Format: `"project": { "id": "10402" }` + xrayFields
- Expected: ✅ SUCCESS
- Purpose: Test documentation example format

### Scenario 5: No testPlanKey (Control)
- Format: Basic import without Test Plan association
- Expected: ✅ SUCCESS
- Purpose: Verify basic import works without xrayFields

## Results

After running the tests, check:
- `results/import_test_results.json` - Detailed test results
- `results/project_info.json` - Project configuration
- `results/create_meta.json` - Available fields metadata

## Expected Findings

This test suite should help identify:
1. ✅ Which `info.json` format works correctly
2. ✅ Whether the issue is with issue type ID or screen configuration
3. ✅ The correct field structure for Test Plan association
4. ✅ Any differences between documentation and actual implementation

## Troubleshooting

### "Token file not found"
- Run `1_authenticate.py` first

### "Project info not found"
- Run `2_inspect_project.py` before `3_test_import.py`

### Authentication fails
- Verify credentials in `config.json`
- Check if API client is still valid

### Import fails with screen error
- Check `results/create_meta.json` for available fields
- Verify issue type ID in config
- Try using issue type name instead of ID (Scenario 3)

## Documentation References

- [Xray Cloud REST API - Import Execution Results](https://docs.getxray.app/display/XRAYCLOUD/Import+Execution+Results+-+REST)
- [Robot Framework Integration](https://docs.getxray.app/display/XRAYCLOUD/Integration+with+Robot+Framework)
- [Custom Fields and Screen Configuration](https://docs.getxray.app/display/XRAYCLOUD/Custom+Fields+and+Screen+Configuration)

## Next Steps After Testing

Based on the results:
1. If Scenario 3 works → Use issue type name instead of ID
2. If Scenario 4 works → Use project ID instead of key
3. If all scenarios fail with xrayFields → Screen configuration issue
4. If only Scenario 5 works → Use two-step approach (import + link)

## Support

For issues with this test suite, check:
- Error messages in console output
- `results/` folder for detailed logs
- Xray documentation for latest API changes

# Quick Start Guide

## 🚀 RECOMMENDED: Simple Test (No Jira URL Required!)

**Fastest way to reproduce the issue:**

```bash
cd /Users/ashish/Jira/docai/xray_robot_test
python run_simple_test.py
```

This will:
1. ✅ Authenticate with Xray Cloud API (no Jira URL needed!)
2. ✅ Test 6 different import scenarios
3. ✅ Generate detailed results

**Uses only**: `https://xray.cloud.getxray.app/api/v2/*` endpoints

---

## 📊 Alternative: Full Test Suite (with Project Inspection)

If you also want to inspect your project configuration:

```bash
cd /Users/ashish/Jira/docai/xray_robot_test
python run_all_tests.py
```

This will:
1. ✅ Authenticate with Xray Cloud API
2. ✅ Inspect your project (you'll need to provide Jira URL)
3. ✅ Test 6 different import scenarios
4. ✅ Generate detailed results

## What to Expect

### During Execution

**Step 1: Authentication**
- Gets bearer token
- Saves token for other scripts

**Step 2: Project Inspection**
- **YOU WILL BE PROMPTED**: Enter your Jira instance URL
  - Example: `https://your-company.atlassian.net`
- Lists all issue types and their IDs
- Identifies Test Execution issue type
- Shows available fields

**Step 3: Import Testing**
- Tests 6 scenarios (5-10 seconds each)
- Shows success/failure for each
- Identifies which configuration works

### After Execution

Check these files:
```
results/
├── auth_token.json           # Your bearer token
├── project_info.json         # Project details
├── create_meta.json          # Available fields
└── import_test_results.json  # Test results ⭐ MAIN OUTPUT
```

## Quick Analysis

Open `results/import_test_results.json` and look for:

```json
{
  "summary": {
    "total": 6,
    "passed": X,
    "failed": Y
  },
  "tests": [
    {
      "name": "Scenario X",
      "success": true/false,
      "result": {...}
    }
  ]
}
```

## Expected Outcomes

✅ **If Scenario 2 or 3 passes**: Use that format!
❌ **If all xrayFields scenarios fail**: Screen configuration issue confirmed
✅ **If Scenario 5 passes**: Basic import works, use two-step workaround

## Troubleshooting

### "Module not found"
```bash
pip install requests
```

### "Permission denied"
```bash
chmod +x run_all_tests.py
```

### Need to rerun just one step?
```bash
python scripts/1_authenticate.py  # Just auth
python scripts/2_inspect_project.py  # Just inspection
python scripts/3_test_import.py  # Just import tests
```

## Time Required

- **Total time**: ~5-10 minutes
- Authentication: 10 seconds
- Project inspection: 30 seconds
- Import testing: 1-2 minutes (6 scenarios)

## What's Next?

After running, you'll know:
1. ✅ Which `info.json` format works
2. ✅ If it's a screen configuration issue
3. ✅ The correct approach to use going forward

Then apply the solution to your actual automation!

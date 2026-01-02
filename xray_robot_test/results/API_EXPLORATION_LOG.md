# API Exploration Log - Manual Testing Session
**Date:** 2025-12-29
**Project:** XSP (Xray Cloud)
**Goal:** Reproduce and solve Robot Framework import issue with Test Plan association

---

## 🎯 SUMMARY OF FINDINGS

### ✅ ROOT CAUSES IDENTIFIED:

1. **Issue Type ID 10858 is INVALID** for project XSP
   - Correct ID: **10009** (Test Execution)
   - User's error was caused by wrong issue type ID

2. **Test Plan XSP-100 did NOT EXIST**
   - Created Test Plan XSP-69 via GraphQL
   - Import works perfectly with valid test plan

3. **xrayFields format was CORRECT all along!**
   - No screen configuration issue
   - Error messages were misleading

### 📊 FINAL RESULTS:
- ✅ Created Test Execution: **XSP-68** (no test plan)
- ✅ Created Test Plan: **XSP-69** (via GraphQL)
- ✅ Created Test Execution: **XSP-70** (with test plan, using issue type name)
- ✅ Created Test Execution: **XSP-71** (with test plan, using correct ID 10009)

---

## 📝 API CALLS LOG

### API CALL 1: Authentication
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/authenticate`

**Request:**
```bash
curl -X POST https://xray.cloud.getxray.app/api/v2/authenticate \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id":"B07CE40C451141EAA70446606AAE0A68",
    "client_secret":"667c13b727b4d11ec482fe650a648bcbb4a04e6d4135e018c813908267f17131"
  }'
```

**Response:**
```
✅ SUCCESS: Bearer token received
Token length: 441 characters
```

**Purpose:** Get authentication token for all subsequent API calls

**Documentation:** https://docs.getxray.app/display/XRAYCLOUD/Authentication+-+REST+v2

---

### API CALL 2: Create Test Execution WITHOUT Test Plan
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart`

**Request:**
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart" \
  -H "Authorization: Bearer $TOKEN" \
  -F "info=@info_scenario5_no_testplan.json" \
  -F "results=@sample_robot_output.xml"
```

**info.json:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Smoke test results - Scenario 5 (No Test Plan)",
    "description": "Testing without testPlanKey to verify basic import works",
    "issuetype": {"name": "Test Execution"}
  }
}
```

**Response:**
```json
{
  "id": "10169",
  "key": "XSP-68",
  "self": "https://ashishkumard1098.atlassian.net/rest/api/2/issue/10169"
}
```

**Result:** ✅ SUCCESS - Created XSP-68

**Key Learning:**
- Basic import works when using issue type **NAME** ("Test Execution")
- No test plan association works fine
- This proves the import mechanism is functional

---

### API CALL 3: Reproduce Error - Non-existent Test Plan
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart`

**Request:**
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart" \
  -H "Authorization: Bearer $TOKEN" \
  -F "info=@info_scenario3_issuetype_name.json" \
  -F "results=@sample_robot_output.xml"
```

**info.json:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Smoke test results - Scenario 3 (Issue Type Name)",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-100"
  }
}
```

**Response:**
```json
{
  "error": "Error importing results: issue with key XSP-100 does not exist or is not of issue type Test Plan!"
}
```

**Result:** ❌ EXPECTED FAILURE - Test Plan doesn't exist

**Key Learning:**
- xrayFields format is accepted (no screen error!)
- Error clearly states the test plan doesn't exist
- This reproduces part of the user's original issue

---

### API CALL 4: Create Test Plan via GraphQL
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/graphql`

**Request:**
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation {
      createTestPlan(
        jira: {
          fields: {
            project: {key: \"XSP\"},
            summary: \"Smoke Test Plan\",
            issuetype: {name: \"Test Plan\"}
          }
        }
      ) {
        testPlan {
          issueId
          jira(fields: [\"key\", \"summary\"])
        }
        warnings
      }
    }"
  }'
```

**Response:**
```json
{
  "data": {
    "createTestPlan": {
      "testPlan": {
        "issueId": "10170",
        "jira": {
          "key": "XSP-69",
          "summary": "Smoke Test Plan"
        }
      },
      "warnings": []
    }
  }
}
```

**Result:** ✅ SUCCESS - Created Test Plan XSP-69

**Key Learning:**
- GraphQL mutation is the easiest way to create Test Plans programmatically
- Format: `createTestPlan(jira: {fields: {...}})`
- This approach works without needing Jira API access

**Documentation:** https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API

---

### API CALL 5: Import with VALID Test Plan (Issue Type Name)
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart`

**Request:**
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart" \
  -H "Authorization: Bearer $TOKEN" \
  -F "info=@info_valid_testplan.json" \
  -F "results=@sample_robot_output.xml"
```

**info.json:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Smoke test results - WITH VALID TEST PLAN",
    "description": "Testing with valid test plan XSP-69",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```

**Response:**
```json
{
  "id": "10171",
  "key": "XSP-70",
  "self": "https://ashishkumard1098.atlassian.net/rest/api/2/issue/10171"
}
```

**Result:** ✅ SUCCESS - Created XSP-70 linked to Test Plan XSP-69

**Key Learning:**
- **This is the RECOMMENDED format!**
- Use issue type **name** not ID
- xrayFields with testPlanKey works perfectly
- Test Execution is automatically linked to Test Plan

---

### API CALL 6: Reproduce Error - Invalid Issue Type ID
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart`

**Request:**
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart" \
  -H "Authorization: Bearer $TOKEN" \
  -F "info=@info_issuetype_id.json" \
  -F "results=@sample_robot_output.xml"
```

**info.json:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Test with Issue Type ID",
    "issuetype": {"id": "10858"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```

**Response:**
```json
{
  "error": "Error creating Test Execution - Issue create failed! - issuetype: Specify a valid issue type"
}
```

**Result:** ❌ EXPECTED FAILURE - Invalid issue type ID

**Key Learning:**
- Issue type ID 10858 does NOT exist in project XSP
- This reproduces the user's original "screen error"
- The error message is misleading (says "specify valid type", not "wrong ID")

---

### API CALL 7: Get Test Issue Type ID
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/graphql`

**Request:**
```bash
curl "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{
      getTests(jql: \"project = XSP\", limit: 1) {
        results {
          issueId
          jira(fields: [\"issuetype\"])
        }
      }
    }"
  }'
```

**Response:**
```json
{
  "data": {
    "getTests": {
      "results": [{
        "issueId": "10168",
        "jira": {
          "issuetype": {
            "id": "10006",
            "name": "Test",
            "description": "This is the Xray Test Issue Type..."
          }
        }
      }]
    }
  }
}
```

**Result:** Found Test issue type ID: **10006**

---

### API CALL 8: Get Test Execution Issue Type ID
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/graphql`

**Request:**
```bash
curl "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{
      getTestExecutions(jql: \"project = XSP\", limit: 1) {
        results {
          issueId
          jira(fields: [\"issuetype\"])
        }
      }
    }"
  }'
```

**Response:**
```json
{
  "data": {
    "getTestExecutions": {
      "results": [{
        "issueId": "10171",
        "jira": {
          "issuetype": {
            "id": "10009",
            "name": "Test Execution",
            "description": "This is the Xray Test Execution Issue Type..."
          }
        }
      }]
    }
  }
}
```

**Result:** Found Test Execution issue type ID: **10009**

**Key Learning:**
- Correct Test Execution ID for XSP: **10009**
- User had: **10858** (completely wrong!)
- GraphQL is great for discovering issue type IDs

---

### API CALL 9: Import with CORRECT Issue Type ID
**Endpoint:** `POST https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart`

**Request:**
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart" \
  -H "Authorization: Bearer $TOKEN" \
  -F "info=@info_correct_id.json" \
  -F "results=@sample_robot_output.xml"
```

**info.json:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Test with CORRECT issue type ID",
    "issuetype": {"id": "10009"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```

**Response:**
```json
{
  "id": "10172",
  "key": "XSP-71",
  "self": "https://ashishkumard1098.atlassian.net/rest/api/2/issue/10172"
}
```

**Result:** ✅ SUCCESS - Created XSP-71 with correct ID

**Key Learning:**
- Using correct issue type ID (10009) works!
- Both approaches work: issue type name OR correct ID
- **Recommendation:** Use NAME for better portability

---

## 🎓 KEY LEARNINGS

### Issue Type IDs for Project XSP:
| Issue Type | ID | Name |
|-----------|-----|------|
| ❌ **User had** | 10858 | INVALID |
| ✅ **Test** | 10006 | Test |
| ✅ **Test Execution** | 10009 | Test Execution |
| ✅ **Test Plan** | 10008 (assumed) | Test Plan |

### Working Configurations:

#### ✅ RECOMMENDED: Use Issue Type Name
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Your summary",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```

#### ✅ ALTERNATIVE: Use Correct Issue Type ID
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Your summary",
    "issuetype": {"id": "10009"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```

### How to Create Test Plan Programmatically:
```bash
curl -X POST "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation {
      createTestPlan(
        jira: {fields: {
          project: {key: \"XSP\"},
          summary: \"Your Test Plan\",
          issuetype: {name: \"Test Plan\"}
        }}
      ) {
        testPlan {
          issueId
          jira(fields: [\"key\"])
        }
      }
    }"
  }'
```

---

## 📋 DOCUMENTATION REFERENCES

### APIs Used:
1. **Xray Authentication API**
   - https://docs.getxray.app/display/XRAYCLOUD/Authentication+-+REST+v2

2. **Robot Framework Import API**
   - https://docs.getxray.app/display/XRAYCLOUD/Import+Execution+Results+-+REST+v2
   - Endpoint: `/api/v2/import/execution/robot/multipart`

3. **Xray GraphQL API**
   - https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API
   - Mutations: `createTestPlan`
   - Queries: `getTests`, `getTestExecutions`

### Key Documentation Pages:
- Integration with Robot Framework: https://docs.getxray.app/display/XRAYCLOUD/Integration+with+Robot+Framework
- Import Execution Results: https://docs.getxray.app/display/XRAYCLOUD/Import+Execution+Results+-+REST
- GraphQL Mutations: https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API

---

## 🚀 AUTOMATED WORKFLOW

### For Future Automation:

```bash
# Step 1: Authenticate
TOKEN=$(curl -s -X POST https://xray.cloud.getxray.app/api/v2/authenticate \
  -H 'Content-Type: application/json' \
  -d '{"client_id":"YOUR_ID","client_secret":"YOUR_SECRET"}' | tr -d '"')

# Step 2: Create Test Plan if needed
curl -X POST "https://xray.cloud.getxray.app/api/v2/graphql" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { createTestPlan(jira: {fields: {project: {key: \"XSP\"}, summary: \"My Test Plan\", issuetype: {name: \"Test Plan\"}}}) { testPlan { jira(fields: [\"key\"]) } } }"}'

# Step 3: Import Robot results with Test Plan
curl -X POST "https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart" \
  -H "Authorization: Bearer $TOKEN" \
  -F "info=@info.json" \
  -F "results=@output.xml"
```

**info.json format:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Automated Test Execution",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```

---

## ✅ ISSUES RESOLVED

1. ✅ **Test Plan doesn't exist** → Created XSP-69 via GraphQL
2. ✅ **Wrong issue type ID** → Found correct ID: 10009
3. ✅ **xrayFields format** → Confirmed it works correctly
4. ✅ **Screen configuration error** → Was actually wrong issue type ID
5. ✅ **Import with Test Plan** → Successfully created XSP-70 and XSP-71

---

## 📊 TEST ARTIFACTS CREATED

| Artifact | Key | Type | Status | Purpose |
|----------|-----|------|--------|---------|
| Test Execution | XSP-68 | Test Execution | ✅ Created | No test plan baseline |
| Test Plan | XSP-69 | Test Plan | ✅ Created | For testing associations |
| Test Execution | XSP-70 | Test Execution | ✅ Created | With test plan (name) |
| Test Execution | XSP-71 | Test Execution | ✅ Created | With test plan (ID) |

All artifacts viewable at: https://ashishkumard1098.atlassian.net/browse/XSP

---

## 🎯 FINAL RECOMMENDATION

**For Robot Framework imports with Test Plan association:**

1. **Use issue type NAME** (not ID) for portability
2. **Create Test Plan first** via GraphQL if it doesn't exist
3. **Use xrayFields format** with testPlanKey (it works!)
4. **Verify Test Plan exists** before importing

**Correct Configuration:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "summary": "Automated Smoke Tests",
    "description": "Robot Framework test results",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XSP-69",
    "environments": ["Chrome", "Linux"]
  }
}
```

---

**Session completed successfully! All issues identified and resolved.**

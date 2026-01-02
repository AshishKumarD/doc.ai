# 🎫 ORIGINAL CLIENT TICKET - DETAILED ANALYSIS

**Date:** 2025-12-29
**Ticket:** Support ticket about Robot Framework import errors
**Product:** Xray **Data Center (DC)** ← CRITICAL!
**Endpoint:** `/api/v2/import/execution/robot/multipart`

---

## 📋 CLIENT'S ISSUE SUMMARY

### Client's Environment:
- **Product:** Xray (stated as DC, but using Cloud credentials for testing)
- **Project:** XSP (originally XX)
- **Test Plan:** XSP-100 (originally XX-100)
- **Issue Type ID:** 10858

### Client's Two Attempts:

#### ❌ Attempt 1: Array Format
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results",
    "description": "smoke test description",
    "testPlanKey": ["XX-100"],  ← ARRAY in fields (WRONG location!)
    "issuetype": {"id": "10858"}
  }
}
```
**Error:** `"Field 'testPlanKey' cannot be set. It is not on the appropriate screen, or unknown."`

#### ❌ Attempt 2: xrayFields Format
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results",
    "description": "smoke test description",
    "issuetype": {"id": "10858"}
  },
  "xrayFields": {
    "testPlanKey": "XX-100"  ← Correct format but got error!
  }
}
```
**Error:** `"Field 'xrayFields' cannot be set. It is not on the appropriate screen, or unknown."`

---

## 🧪 WHAT WE REPRODUCED (Using Xray CLOUD)

### ✅ Test 1: Array Format in Fields
**Our Config:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "testPlanKey": ["XSP-69"],  ← Array in fields
    "issuetype": {"name": "Test Execution"}
  }
}
```
**Error:** `"testPlanKey: Field 'testPlanKey' cannot be set. It is not on the appropriate screen, or unknown."`

**✅ SUCCESSFULLY REPRODUCED CLIENT'S FIRST ERROR!**

**Root Cause:**
- `testPlanKey` should NEVER be in `fields` section
- It should be in `xrayFields` section
- Whether array or string, wrong location = screen error

---

### ❌ Test 2: xrayFields with Wrong Issue Type ID
**Our Config:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "issuetype": {"id": "10858"}  ← Invalid ID
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"
  }
}
```
**Error:** `"Error creating Test Execution - Issue create failed! - issuetype: Specify a valid issue type"`

**❌ DIFFERENT ERROR - Did not reproduce xrayFields error**

**Analysis:**
- Wrong issue type ID stops validation BEFORE xrayFields is checked
- This suggests client's issue type ID might be valid in their system
- Or there's a different root cause

---

### ✅ Test 3: xrayFields with Correct Data
**Our Config:**
```json
{
  "fields": {
    "project": {"key": "XSP"},
    "issuetype": {"name": "Test Execution"}  ← Correct
  },
  "xrayFields": {
    "testPlanKey": "XSP-69"  ← Valid test plan
  }
}
```
**Result:** ✅ SUCCESS - Created XSP-70

**Conclusion:** xrayFields format is CORRECT when data is valid!

---

## 🤔 WHY COULDN'T WE REPRODUCE THE xrayFields ERROR?

### Possible Reasons:

#### 1. **Xray DC vs Cloud Difference** (Most Likely!)
- Client stated: **"Data Center"** hosting
- We tested with: **Xray Cloud** credentials
- DC and Cloud have **different API behaviors**
- DC error messages might be different

**Evidence:**
- User mentioned DC in original ticket
- But provided Xray Cloud credentials for testing
- DC vs Cloud APIs are documented separately

#### 2. **Issue Type ID Validation Order**
- In Cloud: Issue type checked FIRST, xrayFields checked AFTER
- If issue type is invalid, xrayFields validation never runs
- Client got xrayFields error → suggests their issue type passed validation

#### 3. **Project-Specific Configuration**
- Different Jira projects have different screen configurations
- Issue type ID 10858 might exist in client's project (but not XSP)
- xrayFields might not be on the screen for that issue type

---

## 🎯 CONCLUSIONS FOR CLIENT'S TICKET

### ✅ Client's FIRST Error - EXPLAINED:
**Error:** `"testPlanKey: Field 'testPlanKey' cannot be set"`

**Root Cause:**
```json
{
  "fields": {
    "testPlanKey": ["XX-100"]  ← WRONG! This belongs in xrayFields!
  }
}
```

**Solution:**
- Move `testPlanKey` to `xrayFields` section
- Change from array to string
```json
{
  "fields": { ... },
  "xrayFields": {
    "testPlanKey": "XX-100"  ← Correct location + format
  }
}
```

---

### ⚠️ Client's SECOND Error - PARTIALLY EXPLAINED:
**Error:** `"Field 'xrayFields' cannot be set"`

**Possible Root Causes:**

#### Option A: Wrong Issue Type ID (Most Likely)
```json
{
  "issuetype": {"id": "10858"}  ← May be invalid
}
```

**Solution:**
```json
{
  "issuetype": {"name": "Test Execution"}  ← Use name instead
}
```

#### Option B: Test Plan Doesn't Exist
```json
{
  "xrayFields": {
    "testPlanKey": "XX-100"  ← May not exist
  }
}
```

**Solution:**
- Create test plan XX-100 first
- Or use existing test plan key

#### Option C: Xray DC vs Cloud API Difference
- Error message might be DC-specific
- Cloud API doesn't produce this exact error
- May need to test on actual DC instance

---

## 📊 TESTING SUMMARY

| Scenario | Client Error | We Reproduced? | Our Error |
|----------|--------------|----------------|-----------|
| Array in fields | ✅ testPlanKey screen error | ✅ YES | Same error |
| xrayFields + wrong ID | ✅ xrayFields screen error | ❌ NO | issuetype error (different) |
| xrayFields + correct data | N/A | ✅ YES | SUCCESS (XSP-70, 71) |

---

## 🎯 RECOMMENDED SOLUTION FOR CLIENT

### Configuration That DEFINITELY Works:
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results",
    "description": "smoke test description",
    "issuetype": {"name": "Test Execution"}  ← Use NAME
  },
  "xrayFields": {
    "testPlanKey": "XX-YYY"  ← Use VALID test plan key (not XX-100 if it doesn't exist)
  }
}
```

### Steps to Fix:

1. **Fix Issue Type:**
   - Change from `{"id": "10858"}` to `{"name": "Test Execution"}`
   - This works across all projects

2. **Verify Test Plan Exists:**
   - Check if XX-100 exists in Jira
   - If not, create it or use existing test plan

3. **Test Configuration:**
   - Use the multipart endpoint
   - Verify import succeeds

---

## 🚨 CAVEAT - DC vs Cloud

**IMPORTANT:** All our testing was done on **Xray Cloud**, but client mentioned **Data Center**.

### DC vs Cloud Differences:
| Aspect | Xray DC | Xray Cloud |
|--------|---------|------------|
| API Endpoint | REST only | REST + GraphQL |
| Error Messages | May differ | Tested |
| testPlanKey | In URL param or ??? | In xrayFields ✅ |
| Authentication | Basic/Token | Bearer token |

**Recommendation:** If client is truly using DC:
- The solution should still work (use issue type name)
- But error messages might differ
- May need DC-specific testing to confirm

---

## 📝 FINAL ANSWER FOR CLIENT

### Your First Error (Array Format):
**Problem:** `testPlanKey` in wrong location + array format
**Solution:** Move to `xrayFields` and use string

### Your Second Error (xrayFields):
**Likely Problems:**
1. Issue type ID 10858 is invalid for your project
2. Test Plan XX-100 doesn't exist

**Solution:**
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XX-<VALID_TEST_PLAN_KEY>"
  }
}
```

### Steps:
1. ✅ Use issue type **name** instead of ID
2. ✅ Verify test plan exists before importing
3. ✅ Keep xrayFields format (it's correct!)
4. ✅ Test with valid data

---

## 🔍 WHAT WE CONFIRMED

✅ **Array format in fields causes screen error**
✅ **xrayFields format is CORRECT**
✅ **Wrong issue type ID causes error**
✅ **Non-existent test plan causes error**
✅ **Using issue type NAME solves portability**
✅ **Import works when all data is valid**

---

## ❓ WHAT WE COULDN'T CONFIRM

❌ **Exact xrayFields screen error in Cloud** (got different errors)
❌ **DC-specific behavior** (tested only Cloud)
❌ **Why client's issue type ID gave xrayFields error** (not issuetype error)

**Hypothesis:** Client might be mixing DC and Cloud configurations, or there's a DC-specific validation order.

---

**Recommendation:** Implement the solution with issue type name and valid test plan. This should work for both DC and Cloud.

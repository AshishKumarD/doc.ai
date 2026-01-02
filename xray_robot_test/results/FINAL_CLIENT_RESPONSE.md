# Support Response for Client

---

**Subject:** Solution for Robot Framework Import with Test Plan Association

---

Hi,

Thanks for reaching out. I've reviewed both configurations you sent and found the issue. Here's what's happening and how to fix it.

---

## Your First Attempt - Array Format

**What you tried:**
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results",
    "testPlanKey": ["XX-100"],
    "issuetype": {"id": "10858"}
  }
}
```

**The problem:**

You put `testPlanKey` directly in the `fields` section, but it's an Xray-specific field and doesn't belong there. Jira only recognizes standard fields like project, summary, and issuetype in the `fields` section. That's why you're getting the "not on the appropriate screen" error.

Also, `testPlanKey` needs to be a string, not an array. It only accepts a single test plan key.

---

## Your Second Attempt - xrayFields Location

**What you tried:**
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results",
    "issuetype": {"id": "10858"}
  },
  "xrayFields": {
    "testPlanKey": "XX-100"
  }
}
```

**The problem:**

Based on the error you're getting, it looks like `xrayFields` might be nested inside the `fields` section in your actual code. The `xrayFields` section needs to be at the same level as `fields`, not inside it.

The structure should be:
```json
{
  "fields": { ... },
  "xrayFields": { ... }
}
```

---

## The Correct Configuration

Here's what works:

```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke test results - Automated Run",
    "description": "Robot Framework smoke test execution",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XX-100"
  }
}
```

**Key changes:**
- `xrayFields` is at the same level as `fields` (not inside it)
- `testPlanKey` is a string, not an array
- Using `"name": "Test Execution"` instead of the ID is more reliable since issue type IDs can vary between projects

**Important:** Make sure test plan XX-100 already exists in your project before importing.

---

## Addressing Your Concern About Generic Titles

You mentioned you're not happy with the generic test execution title when using the simple endpoint. The good news is that the **multipart endpoint solves this problem**.

**Simple endpoint (limited control):**
```bash
POST /api/v2/import/execution/robot?projectKey=XX&testPlanKey=XX-100
```
This generates a generic title automatically, which is why you're not satisfied.

**Multipart endpoint (full control):**
```bash
POST /api/v2/import/execution/robot/multipart
```
With the multipart endpoint and the correct `info.json` configuration above, you can:
- Set a **custom summary** (title) for your Test Execution
- Associate it with a **Test Plan**
- Add a **description**, **labels**, **components**, or any other fields you need

So by using the multipart endpoint with the correct format, you get both what you want: a meaningful title AND test plan association.

---

## Can I Use Multiple Test Plans?

No, the array format isn't supported. `testPlanKey` only accepts one test plan at a time. If you need to link a Test Execution to multiple test plans, you'll need to use the API after the import to add the additional associations.

---

## Complete Import Example

**1. Create your `info.json` file:**
```json
{
  "fields": {
    "project": {"key": "XX"},
    "summary": "Smoke Tests - Build #123 - Chrome",
    "description": "Automated smoke test execution for release 2.5.0",
    "issuetype": {"name": "Test Execution"}
  },
  "xrayFields": {
    "testPlanKey": "XX-100",
    "environments": ["Chrome", "Windows"]
  }
}
```

**2. Run the import command:**
```bash
curl -H "Content-Type: multipart/form-data" -X POST \
  -F info=@info.json \
  -F results=@output.xml \
  -H "Authorization: Bearer $token" \
  https://xray.cloud.getxray.app/api/v2/import/execution/robot/multipart
```

**3. Successful response:**
```json
{
  "id": "10123",
  "key": "XX-456",
  "self": "https://your-instance.atlassian.net/rest/api/2/issue/10123"
}
```

Now your Test Execution will have:
- Your custom title: "Smoke Tests - Build #123 - Chrome"
- Associated with Test Plan: XX-100
- Environment tags: Chrome, Windows

---

## Quick Reference

| Aspect | Correct Format |
|--------|----------------|
| JSON Structure | `xrayFields` at same level as `fields` |
| testPlanKey | String: `"XX-100"` (not array) |
| Issue Type | Use `"name": "Test Execution"` |
| Custom Title | Set in `fields.summary` |

---

## References

For more details, you can refer to our documentation:

- **Robot Framework Integration Guide**
  https://docs.getxray.app/display/XRAYCLOUD/Integration+with+Robot+Framework

- **Import Execution Results - REST API v2**
  https://docs.getxray.app/display/XRAYCLOUD/Import+Execution+Results+-+REST+v2

- **Xray JSON Format Specification**
  https://docs.getxray.app/display/XRAYCLOUD/Using+Xray+JSON+format+to+import+execution+results

- **Authentication - REST v2**
  https://docs.getxray.app/display/XRAYCLOUD/Authentication+-+REST+v2

---

Let me know if you run into any issues or have questions!

Best regards,
**Xray Support Team**

# Support Ticket Response Workflow

This document outlines the complete workflow for responding to Xray support tickets using the DocAI system.

---

## Overview

**Context: You are a member of the Xray Support Team**

This workflow is used by Xray support team members to respond to customer support tickets. When a customer submits a support ticket, you (the support member) use this system to query our internal ChromaDB vector database containing indexed Xray documentation, then synthesize accurate answers based on that documentation.

**Your Role:**
- You are responding **as an official Xray support team member**
- You represent Xray (by Xpand IT) to customers
- Your responses should be authoritative, professional, and accurate
- When documentation is unclear or missing, you should escalate internally or reach out to engineering teams

**The Flow:**
1. Customer submits support ticket → You (Support Member)
2. You (via Claude) run `query_direct.py` script
3. Script queries ChromaDB (vector search only, no LLM)
4. Script returns raw documentation to you
5. You read the docs and synthesize the answer
6. You provide official response to Customer

**Key Point:** There is NO local LLM model running. Claude (you) is the only AI doing the synthesis, acting as a support team member.

---

## Prerequisites

### Virtual Environment
The system uses a Python virtual environment with all required dependencies:
```bash
./venv/bin/python
```

**Required packages:**
- `chromadb` - Vector database
- `sentence-transformers` - For embeddings

---

## Step-by-Step Workflow

### Step 1: Receive the Ticket
When you receive a support ticket (e.g., SUPPORT-110034), identify:
- **Ticket ID**: The unique identifier
- **Customer Question(s)**: What the customer is asking
- **Context**: Any specific API, feature, or workflow they're working with

### Step 2: Formulate the Query
Based on the ticket, create specific queries that:
- Focus on the core technical question
- Use terminology from the Xray documentation
- Break complex questions into multiple simpler queries if needed

**Example for SUPPORT-110034:**
- Query 1: "Is it possible to update multiple iteration statuses in a single GraphQL API call?"
- Query 2: "How can I optimize the workflow of finding test keys, getting testrun IDs, and updating iteration status?"

### Step 3: Search Jira Backlog for Similar Tickets (FIRST PRIORITY)

**IMPORTANT:** Before searching documentation, ALWAYS check the Jira backlog to see if similar questions have been asked and resolved.

**Script Location:**
```
/Users/ashish/Jira/ticket-tracker/backlog_search.py
```

**Quick Usage:**
```bash
cd /Users/ashish/Jira/ticket-tracker
python3 backlog_search.py "your keywords here"
```

**Why Search Backlog First:**
1. **Find Official Answers**: Resolved tickets contain official Xray support responses
2. **Pattern Recognition**: See if multiple customers asked the same question
3. **Context & Examples**: Real customer scenarios and resolutions
4. **Recent Issues**: Catch issues not yet in documentation
5. **Workarounds**: Find documented workarounds or known limitations

**When to Use Backlog Search:**
- ✅ ALWAYS run before documentation search
- ✅ For all customer questions (no exceptions)
- ✅ Even if you think you know the answer (verify with backlog)

**Search Strategy:**

Run 1-3 targeted searches with different keyword combinations:

```bash
# Search 1: Broad search (include resolved tickets)
python3 backlog_search.py "test repository clone" -r -m 20

# Search 2: Specific terms
python3 backlog_search.py "export import tests CSV" -r -m 20

# Search 3: Action-oriented (if needed)
python3 backlog_search.py "copy folder test repository" -r -m 20
```

**Search Options:**
- `-r` or `--include-resolved`: Include resolved/closed tickets (RECOMMENDED - shows official answers)
- `-m 20` or `--max-results 20`: Limit results to 20 (default: 20)
- `-p xray` or `--product xray`: Filter by product (xray, xporter, any)
- `-t Cloud` or `--hosting Cloud`: Filter by hosting (Cloud, Data Center, any)
- `-s filename`: Save results to JSON file for later reference

**Analyzing Search Results:**

Follow the analysis guidelines from `/Users/ashish/Jira/ticket-tracker/BACKLOG_SEARCH.md`:

1. **Pattern Recognition**: Scan titles for exact keyword matches
2. **Relevance Scoring**: Categorize as Most Relevant (🎯), Related (🔗), or Not Relevant (❌)
3. **Pattern Detection**: Look for recurring themes (multiple customers, time span, status patterns)
4. **Synthesis**: Combine backlog findings with documentation

**What to Look For:**
- 🎯 **Exact Matches**: Customers asking the exact same question
- ✅ **Resolved Status**: Official answers from Xray support team
- 📅 **Recent Tickets**: Issues from last 6 months
- 🔄 **Multiple Requests**: Same question asked by 3+ customers
- ⚠️ **Known Limitations**: Tickets marked as "Won't Fix" or "Feature Request"

**Output Example:**
```
🔍 Found 28 tickets (showing 20)

🎯 Most Relevant:
1. [SUPPORT-110607] Is there a way to clone the Test Repository...
   Status: Waiting for L1 Support | Created: 2025-12-31
   🔗 https://jira.getxray.app/browse/SUPPORT-110607
   → This is YOUR current ticket!

2. [SUPPORT-105234] Clone Test Repository folders between projects
   Status: Resolved | Created: 2025-08-15
   🔗 https://jira.getxray.app/browse/SUPPORT-105234
   → Official answer provided by support team
```

**If Backlog Search Finds Relevant Tickets:**
- ✅ Read the resolved tickets to see official answers
- ✅ Check if there's a linked feature request (XRAYCLOUD-XXXX)
- ✅ Note common workarounds mentioned in multiple tickets
- ✅ Include backlog findings in your response to customer
- ✅ STILL proceed to Step 4 (ChromaDB) for documentation verification

**If No Relevant Tickets Found:**
- ✅ Proceed to Step 4 (ChromaDB documentation search)
- ✅ Note in your response that this appears to be a new question

### Step 4: Query ChromaDB Using query_direct.py

**Script Location:**
```
/Users/ashish/Jira/docai/src/claude/query_direct.py
```

**Usage:**
```bash
cd /Users/ashish/Jira/docai
./venv/bin/python src/claude/query_direct.py "your question here"
```

**What the Script Does:**
1. Connects to ChromaDB at `./data/chroma_db/chroma_xray_cloud_db`
2. Uses sentence-transformers (`BAAI/bge-small-en-v1.5`) to generate query embedding
3. Retrieves top 10 most relevant documents (configurable)
4. Returns RAW documentation content without any LLM synthesis
5. Shows relevance scores for each document

**Script Configuration:**
- ChromaDB Path: `./data/chroma_db/chroma_xray_cloud_db`
- Embedding Model: `BAAI/bge-small-en-v1.5`
- Top K: 10 (retrieves 10 most relevant documents)
- Output: Raw documentation snippets with metadata

### Step 4: Run Multiple Queries
For comprehensive answers, run multiple targeted queries:

```bash
# Query 1: Specific API functionality
./venv/bin/python src/claude/query_direct.py "Can I batch update multiple iteration statuses?"

# Query 2: Workflow optimization
./venv/bin/python src/claude/query_direct.py "How to optimize getTestRuns and updateIterationStatus workflow?"

# Query 3: GraphQL bulk operations
./venv/bin/python src/claude/query_direct.py "GraphQL bulk operations mutations aliases in Xray"
```

### Step 5: Analyze the Results

Each query returns raw documentation:

**Output Structure:**
- **Document snippets**: First 500 characters of each relevant doc (or full content if shorter)
- **Relevance score**: Percentage showing how relevant the doc is to the query
- **File name**: Which documentation file it came from
- **Metadata**: Additional context about the source

**Your Job (Claude's Job):**
Now YOU read the raw documentation and:
1. Identify what's explicitly stated in the docs
2. Note what's NOT mentioned in the docs
3. Look for specific examples, code snippets, or instructions
4. Check relevance scores - lower scores may be less reliable

### Step 6: [OPTIONAL] Perform Web Search for Additional Confirmation

**When to use this step:**
- If the documentation does NOT provide a 100% clear answer
- When there are gaps or ambiguities in the retrieved documentation
- To find additional context from official sources (Atlassian Community, Xray forums, etc.)
- To validate or supplement findings with real-world user experiences

**How to perform web search:**

Use the WebSearch tool with targeted queries:

```bash
# Example searches
WebSearch: "Xray Jira license expiration data retention 2025"
WebSearch: "Xray app license expired can still view test data Jira Cloud"
```

**What to look for:**
1. **Official Xray/Atlassian sources**: Documentation, KB articles, support pages
2. **Community discussions**: Atlassian Community forums, verified responses
3. **Real user experiences**: How others handled similar situations
4. **Official statements**: Direct quotes from Xray team or Atlassian support

**Important guidelines:**
- Prioritize official sources over community speculation
- Look for recent information (check dates - prefer 2024-2025)
- Cross-reference multiple sources for consistency
- Clearly distinguish between official documentation and community insights

**Integration with documentation findings:**
- Compare web search results with ChromaDB documentation findings
- Use web search to fill gaps where documentation is silent
- Cite both sources separately in your final response
- If web search contradicts documentation, note the discrepancy and prioritize official docs

### Step 7: Synthesize the Response (Claude Does This)

**CRITICAL RULES:**

**IMPORTANT:** It is OKAY and ENCOURAGED to suggest theoretical solutions based on industry standards, specifications, or general knowledge. However, you MUST clearly distinguish them from documented facts.

#### ✅ DO:
1. **Only cite information explicitly found in the documentation as "documented"**
2. **Quote relevance scores and source files for all documented claims**
3. **If documentation doesn't cover something, state it clearly**:
   - "The documentation does not provide examples of..."
   - "This is not explicitly documented..."
4. **Suggest theoretical solutions with clear labeling**:
   - Documented: "According to the Xray documentation..."
   - Theoretical: "While not documented in Xray, GraphQL standard supports... (requires testing)"
5. **Provide rationale for theoretical suggestions** (e.g., "based on GraphQL specification", "standard REST API pattern")

#### ❌ DON'T:
1. **Never present theoretical examples as if they're from documentation** (always label them clearly)
2. **Never infer Xray-specific features without documentation** (but you CAN reference general standards/specs)
3. **Never claim something is documented when it's only theoretically possible**
4. **Never omit disclaimers when suggesting theoretical solutions** (always include "requires testing" or similar)

### Step 7.1: Extract Accurate Documentation URLs

**CRITICAL: Always provide exact documentation URLs, not generic home page links.**

When citing documentation sources, you MUST extract the actual URL from the source file:

**How to extract URLs:**

1. **Read the source file header** - All documentation files have the URL in the first few lines:
   ```bash
   head -5 data/documentation/xray_cloud/[FILENAME].md
   ```

2. **Look for the "Source:" line** - Example:
   ```markdown
   # Requirement Traceability Report - Xray Cloud Documentation - XRAY view

   Source: https://docs.getxray.app/space/XRAYCLOUD/44565208
   ```

3. **Use the exact URL** - Not the generic home page URL

**Example:**

❌ **WRONG:**
- [Requirement Traceability Report - Xray Cloud Documentation](https://docs.getxray.app/display/XRAYCLOUD/)

✅ **CORRECT:**
- [Requirement Traceability Report](https://docs.getxray.app/space/XRAYCLOUD/44565208)

**Command to extract URLs:**
```bash
# If you found relevant information in file 44565208.md
head -5 data/documentation/xray_cloud/44565208.md

# This will show you the exact URL in the "Source:" line
```

**Important:** Customers need exact documentation links to:
- Verify the information
- Read more details
- Bookmark specific pages
- Share with their teams

Generic home page links are not helpful and make your response less professional.

### Step 8: Format the Response

**Template:**

```markdown
Hi [Customer Name],

Thank you for contacting Xray Support. I'll be happy to help with your question.

## Answer for [TICKET-ID]

### Question 1: [First question]

**[Yes/No/Partial Answer]**

[Explanation based on documentation]

**Source:**
- [File name] • [Relevance %]
- Documentation URL: [link]

### Question 2: [Second question]

**[Yes/No/Partial Answer]**

[Explanation based on documentation]

**Source:**
- [File name] • [Relevance %]
- Documentation URL: [link]

---

### Additional Findings from Web Search (Optional)

**If web search was performed:**

[Explanation of findings from official sources, community forums, etc.]

**Sources:**
- [Community discussion title - URL]
- [Official KB article - URL]
- [Other relevant sources]

---

### Theoretical Solutions (Not Documented)

If applicable, suggest theoretical approaches with clear disclaimer:

**Note:** The following is based on [standard/specification], not Xray documentation. Testing required.

[Explanation of theoretical approach]

**Recommendation:** Test this approach and report findings.

---

### References
- [Exact Documentation Page Title](https://docs.getxray.app/space/XRAYCLOUD/[PAGE_ID]) - Extract from source file
- [Another Documentation Page](https://docs.getxray.app/space/XRAYCLOUD/[PAGE_ID])
- [Web search sources - if applicable with full URLs]

**Example of extracting URL:**
```bash
# If you cited information from file 44565208.md
head -5 data/documentation/xray_cloud/44565208.md
# Output shows: Source: https://docs.getxray.app/space/XRAYCLOUD/44565208
```

---

If you have any further questions or need clarification, please don't hesitate to reach out.

Best regards,
Xray Support Team
```

---

## Example Response Structure

### Good Example:

```markdown
Hi [Customer Name],

Thank you for contacting Xray Support. I'll be happy to help with your question.

**Question:** Can I update multiple iterations in one call?

**Answer (from documentation):**
No, the Xray Cloud GraphQL API documentation does not provide
examples or confirmation of batch updates for updateIterationStatus.
Each iteration must be updated individually.

Source: GraphQL_API.md • 56.5% relevance

**Theoretical Approach (NOT documented):**
While not documented in Xray's API docs, GraphQL standard supports
aliases which could allow multiple mutations in one request:

mutation {
  update1: updateIterationStatus(...) { ... }
  update2: updateIterationStatus(...) { ... }
}

⚠️ This approach is based on GraphQL specification, not Xray
documentation. Testing is required to confirm it works with Xray's
implementation, considering the 25-resolver limit.

**References:**
- [GraphQL API Documentation](https://docs.getxray.app/space/XRAYCLOUD/44577089) - Extracted from GraphQL_API.md

If you have any further questions or need clarification, please don't hesitate to reach out.

Best regards,
Xray Support Team
```

### Good Example (With Web Search):

```markdown
Hi [Customer Name],

Thank you for contacting Xray Support. I'll be happy to help with your question.

**Question:** Will Xray data be retained after license expiration?

**Answer (from documentation):**
"If you have a paid or trial license and it expires, you won't be able
to use the Xray app."

Source: 44566412.md • 74.6% relevance

**Additional Findings:**
For Xray Cloud, when the license expires:
- You cannot view Xray panels or functionality
- All data is retained and will be restored when license is renewed
- Xray issue types remain as basic Jira issues with limited fields

**References:**
- [FAQ - Xray Cloud](https://docs.getxray.app/space/XRAYCLOUD/44566412) - Extracted from 44566412.md
- [What happens to my XRay issues after license expires? - Atlassian Community](https://community.atlassian.com/forums/App-Central-questions/What-happens-to-my-XRay-issues-after-my-XRay-lincense-expires/qaq-p/2976314)
- [Xray with expired license - Atlassian Community](https://community.atlassian.com/forums/Jira-questions/XRAY-with-expired-license/qaq-p/1355576)

If you have any further questions or need clarification, please don't hesitate to reach out.

Best regards,
Xray Support Team
```

### Bad Example (Avoid):

```markdown
❌ You can batch updates using GraphQL aliases like this:
mutation {
  update1: updateIterationStatus(...) { ... }
  update2: updateIterationStatus(...) { ... }
}

[This implies it's documented/confirmed when it's not]
```

### Bad Example - Incorrect URL References:

```markdown
❌ **WRONG - Generic home page links:**

**References:**
- [Xray Documentation](https://docs.getxray.app/)
- [Xray Cloud Docs](https://docs.getxray.app/display/XRAYCLOUD/)

[These are not helpful - customers can't find the specific information]
```

```markdown
✅ **CORRECT - Specific page links:**

**References:**
- [Requirement Traceability Report](https://docs.getxray.app/space/XRAYCLOUD/44565208)
- [Project Settings: Test Coverage](https://docs.getxray.app/space/XRAYCLOUD/44566845)

[These link directly to the relevant documentation pages]
```

---

## Common Pitfalls to Avoid

1. **Using generic home page URLs** - ALWAYS extract exact URLs from documentation files using `head -5 data/documentation/xray_cloud/[FILENAME].md`. Generic links like `https://docs.getxray.app/` are not helpful to customers
2. **Presenting theoretical examples as documented** - It's OKAY to suggest theoretical solutions based on standards (like GraphQL specs), but you MUST clearly label them as "not documented" or "requires testing"
3. **Inferring features without basis** - Don't assume capabilities not explicitly mentioned unless you can reference a relevant standard/spec
4. **Omitting source references** - Always cite relevance scores and source files for documented information
5. **Mixing documented and theoretical** - Clearly separate these sections with headers like "From Documentation:" and "Theoretical Approach (Not Documented):"
6. **Not mentioning missing documentation** - If something isn't documented, say so explicitly

---

## Troubleshooting

### ChromaDB Not Found
Verify the database exists:
```bash
ls -la /Users/ashish/Jira/docai/data/chroma_db/chroma_xray_cloud_db
```

### Module Not Found Errors
Ensure you're using the virtual environment:
```bash
./venv/bin/python src/cli/quick_query.py "query"
```

### Low Relevance Scores
If relevance is below 50%, try:
- Reformulating the query with different terminology
- Breaking complex queries into simpler ones
- Checking if the topic is actually covered in the documentation

---

## Query Optimization Tips

### Good Queries:
- ✅ "Can I batch update multiple iteration statuses in GraphQL?"
- ✅ "What is the resolver limit for GraphQL requests?"
- ✅ "How to optimize getTestRuns API calls?"

### Poor Queries:
- ❌ "How do I make this faster?" (too vague)
- ❌ "Tell me about APIs" (too broad)
- ❌ "Why isn't this working?" (requires debugging, not documentation)

---

## Documentation Source

The ChromaDB contains documentation from:
- **Source:** Xray Cloud official documentation
- **Location:** `./data/documentation/xray_cloud/`
- **Format:** Markdown files with source URLs
- **Database:** `./data/chroma_db/chroma_xray_cloud_db`

---

## Summary Checklist

Before sending a response, verify:

- [ ] Ran `query_direct.py` with multiple targeted queries
- [ ] Read the raw documentation returned by the script
- [ ] Cited source files and relevance scores from the output
- [ ] **CRITICAL:** Extracted exact documentation URLs from source files (using `head -5 data/documentation/xray_cloud/[FILENAME].md`)
- [ ] Verified all documentation links point to specific pages, not generic home pages
- [ ] [OPTIONAL] Performed web search if documentation didn't provide 100% clear answer
- [ ] [OPTIONAL] If web search performed, cited official sources and community forums separately
- [ ] Clearly distinguished documented facts from web search findings and theoretical solutions
- [ ] Included proper disclaimers for non-documented approaches
- [ ] Only referenced examples that actually appear in the retrieved docs
- [ ] Stated clearly when something is NOT documented
- [ ] If suggesting theoretical approaches, labeled them as "not documented" or "requires testing"

---

## Updates and Improvements

### When Documentation Updates:
1. Re-index the documentation into ChromaDB
2. Verify queries return updated information
3. Update this workflow if new features are added

### When Queries Don't Find Answers:
1. Try rephrasing with different keywords
2. Check if the topic is in the documentation source
3. Perform web search for additional context (see Step 6)
4. If truly not documented anywhere:
   - Clearly state this in your response to the customer
   - **Escalate internally:** Reach out to engineering teams or senior support members for clarification
   - Document the answer once received for future reference
5. Provide a preliminary answer based on best knowledge while noting that you're confirming with the team

---

## Internal Support and Escalation

**For issues with this DocAI workflow system:**
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Review recent changes to the system
4. Contact the system administrator or DevOps team

**For customer questions that require escalation:**
1. **Documentation gaps:** If critical information is missing from documentation, escalate to technical writers
2. **Complex technical issues:** Escalate to senior support engineers or engineering team
3. **Feature requests:** Log in internal feature request system
4. **Bugs:** Create internal bug tickets with reproduction steps
5. **Policy/licensing questions:** Escalate to sales or licensing team

**Remember:** As a support team member, you can escalate internally rather than leaving customers without answers. Always provide a preliminary response acknowledging the question and indicating you're confirming details with the team.

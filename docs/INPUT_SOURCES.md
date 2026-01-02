# JiraDocAI - Input Sources

## Current Data Source

**Location**: `/Users/ashish/Jira/Issue1`

This folder contains your **Jira production server diagnostic data and logs**.

## What's Currently Being Indexed

### 1. **Server Configuration Files**
- `application-config/` - Jira application configurations
- `application-properties/` - Server properties
- `cache-cfg/` - Cache configuration files
- `auth-cfg/` - Authentication settings
- `tomcat-config/` - Tomcat server configuration

### 2. **Application Logs**
- `application-logs/` - Jira application logs
  - `atlassian-jira.log` - Main Jira logs
  - `atlassian-jira-security.log` - Security events
  - `atlassian-jira-sql.log` - Database queries
  - `atlassian-greenhopper.log` - Agile board logs
  - `atlassian-jira-migration.log` - Migration logs
  - Many more...

### 3. **System Diagnostics**
- `healthchecks/` - Health check results
- `thread-dump/` - Thread dumps for debugging
- `database-queries/` - Database query logs
- `cluster-nodes/` - Cluster node information

### 4. **Server Logs**
- `tomcat-access-logs/` - HTTP access logs
- `tomcat-logs/` - Tomcat server logs
- `node2_logs/` - Secondary node logs (if clustered)

### 5. **Analysis Documents**
- `XRAY_WORKING_CASE_ANALYSIS.md` - Your Xray working case analysis

### 6. **Support Archives**
- `.zip` files - Jira support archives (not currently indexed)
- WhatsApp images - Screenshots (not currently indexed)

## File Types Indexed

Currently, JiraDocAI indexes:
- ✅ `.md` - Markdown files
- ✅ `.txt` - Text files
- ✅ `.log` - Log files
- ✅ `.pdf` - PDF documents
- ❌ `.zip` - Archives (not extracted)
- ❌ `.jpeg/.png` - Images (not OCR'd)
- ❌ `.properties` - Not currently indexed
- ❌ `.xml` - Not currently indexed

**Total Files**: ~287 indexable files found

## What Questions Can You Ask?

Based on this data, you can ask:

### Configuration Questions
```
What authentication methods are configured?
What cache settings are in place?
How is the database configured?
What are the cluster node settings?
```

### Troubleshooting Questions
```
What errors are in the application logs?
Are there any security issues logged?
What SQL queries are slow?
What do the health checks show?
```

### Analysis Questions
```
What's the working case analysis about?
What migration issues were encountered?
What performance issues are documented?
```

## Adding More Documentation

### Option 1: Add Xray Documentation from the Web

```bash
cd /Users/ashish/Jira/jiradocai
python download_xray_docs.py
```

This will:
- Crawl https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions
- Download all linked pages
- Save to `/Users/ashish/Jira/Issue1/xray_docs/`
- Give you Xray product documentation

### Option 2: Add Your Own Documentation

Just copy any documentation to `/Users/ashish/Jira/Issue1/`:

```bash
# Copy Markdown files
cp ~/my-jira-docs/*.md /Users/ashish/Jira/Issue1/

# Copy PDFs
cp ~/jira-manuals/*.pdf /Users/ashish/Jira/Issue1/

# Copy from another location
cp -r ~/confluence-export/ /Users/ashish/Jira/Issue1/confluence/
```

### Option 3: Change the Source Directory

Edit `1_index_documents.py`, `2_query_cli.py`, and `3_query_web.py`:

```python
# Change this line:
DOCS_PATH = "/Users/ashish/Jira/Issue1"

# To point to your docs:
DOCS_PATH = "/path/to/your/documentation"
```

## After Adding New Docs

Re-run the indexer:

```bash
python 1_index_documents.py
```

This will re-index everything including new documents.

## Current Index Coverage

```
📁 /Users/ashish/Jira/Issue1/
├── ✅ Server configs (application-config, cache-cfg, etc.)
├── ✅ Application logs (jira, security, sql, etc.)
├── ✅ Diagnostics (healthchecks, thread-dumps)
├── ✅ Server logs (tomcat access/logs)
├── ✅ Analysis docs (XRAY_WORKING_CASE_ANALYSIS.md)
├── ❌ ZIP archives (need extraction)
└── ❌ WhatsApp images (need OCR)
```

## Expanding File Type Support

To index more file types, edit `1_index_documents.py`:

```python
# Current:
required_exts=[".md", ".txt", ".pdf", ".log"]

# Add more:
required_exts=[".md", ".txt", ".pdf", ".log", ".properties", ".xml", ".json"]
```

Then re-run indexing.

## Data Privacy Note

Since everything runs locally with Ollama:
- ✅ Your Jira logs stay on your machine
- ✅ No data sent to external APIs
- ✅ No cloud storage
- ✅ 100% private and secure

## Summary

**What JiraDocAI currently knows about**:
- Your Jira production server configuration
- Application logs and errors
- Health checks and diagnostics
- Server settings and cluster info
- Your Xray working case analysis

**What you can add**:
- Xray documentation from the web (via `download_xray_docs.py`)
- Your own documentation files
- Confluence exports
- Admin guides
- Runbooks
- Any text-based documentation

**After indexing**, you can ask questions and get answers with **source citations** showing exactly which log file, config file, or document the answer came from!

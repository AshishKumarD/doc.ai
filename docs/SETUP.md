# JiraDocAI Setup for Xray Documentation

**Goal**: Create an AI assistant that answers questions about Xray documentation with source citations.

**Source**: https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions

**Cost**: $0 (100% free and open source)

---

## Complete Setup Guide

### Step 1: Install Ollama (Local LLM)

**macOS**:
```bash
brew install ollama
```

**Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows**:
Download from https://ollama.com/download

### Step 2: Start Ollama & Download Model

**Terminal 1** (keep this running):
```bash
ollama serve
```

**Terminal 2** (one-time download):
```bash
# Download Llama 3.1 model (~4GB)
ollama pull llama3.1:8b
```

### Step 3: Setup Python Environment

```bash
cd /Users/ashish/Jira/jiradocai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Download Xray Documentation (5-10 minutes)

This crawls the entire Xray documentation website:

```bash
python download_xray_docs.py
```

**What it does**:
- Starts at: https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions
- Follows all links (up to 5 levels deep)
- Downloads all pages as Markdown
- Saves to: `/Users/ashish/Jira/xray_documentation/`

**You'll see**:
```
======================================================================
Xray Documentation Downloader for JiraDocAI
======================================================================

📍 Starting URL: https://docs.getxray.app/...
📁 Output directory: /Users/ashish/Jira/xray_documentation
🔢 Max depth: 5
⏱️  Delay between requests: 1s

======================================================================

🚀 Starting crawl...

[Depth 0] Processing: https://docs.getxray.app/...
📥 Downloading: https://docs.getxray.app/...
✅ Saved: App_Editions.md

[Depth 1] Processing: https://docs.getxray.app/...
📥 Downloading: https://docs.getxray.app/...
✅ Saved: Test_Management.md

...

======================================================================
✅ CRAWL COMPLETE!
======================================================================
📄 Documents downloaded: 150
🔗 URLs visited: 150
⏱️  Time elapsed: 180.5s
📁 Saved to: /Users/ashish/Jira/xray_documentation
```

### Step 5: Index the Documentation (5-10 minutes, one-time)

```bash
python 1_index_documents.py
```

**What it does**:
- Reads all downloaded Xray docs
- Breaks them into chunks
- Generates embeddings (locally, free)
- Stores in ChromaDB vector database

**You'll see**:
```
======================================================================
JiraDocAI - Documentation Indexer
100% Free & Open Source
======================================================================

📁 Documentation path: /Users/ashish/Jira/xray_documentation
💾 Database path: ./chroma_jira_db
🤖 LLM: Ollama (llama3.1:8b)

🤖 Initializing Ollama...
🧠 Loading embedding model (this may take a moment)...
💾 Setting up vector database...

📖 Loading documents from /Users/ashish/Jira/xray_documentation...
✅ Loaded 150 documents

🔨 Creating index (this will take a few minutes)...
   - Chunking documents...
   - Generating embeddings (local, free)...
   - Storing in vector database...

✅ Index created successfully!

======================================================================
✅ SUCCESS! Your documentation has been indexed.
======================================================================

💰 Cost: $0 (everything runs locally!)
```

### Step 6: Start Asking Questions!

**Option A: Command Line**

```bash
python 2_query_cli.py
```

Example session:
```
💬 You: What are the different Xray App editions?

🔍 Searching documentation...

======================================================================
📝 ANSWER
======================================================================
Xray offers several editions:

1. Xray Free - Basic test management features
2. Xray Standard - Advanced test management
3. Xray Premium - Enterprise features with compliance
4. Xray Enterprise - Full-scale enterprise solution

Each edition includes different features and capabilities.

======================================================================
📚 SOURCES
======================================================================

[1] App_Editions.md
    Relevance: 94.7%
    Path: /Users/ashish/Jira/xray_documentation/App_Editions.md

    Preview:
    "Xray Cloud offers different editions to match your needs..."

[2] Pricing_and_Licensing.md
    Relevance: 87.2%
    Path: /Users/ashish/Jira/xray_documentation/Pricing_and_Licensing.md

    Preview:
    "Compare features across editions to find the right fit..."
======================================================================
```

**Option B: Web Interface**

```bash
python 3_query_web.py
```

Opens a beautiful web interface at: http://localhost:7860

- Chat interface
- Formatted markdown responses
- Automatic source citations
- Example questions
- Mobile-friendly

---

## What You Can Ask

### About Xray Features
```
What are the different Xray App editions?
How do I create test cases in Xray?
What's the difference between test plans and test executions?
How do I integrate Xray with Jira?
```

### About Test Management
```
How do I organize tests in Xray?
What are test repositories?
How do I execute tests?
How do I track test coverage?
```

### About Integration & API
```
How do I integrate Xray with CI/CD?
What APIs does Xray provide?
How do I automate test execution?
How do I import test results?
```

### About Pricing & Features
```
What features are in each edition?
How much does Xray cost?
What's included in the free tier?
What's the difference between Cloud and Server?
```

---

## File Structure

```
/Users/ashish/Jira/
├── xray_documentation/          ← Downloaded Xray docs (Step 4)
│   ├── App_Editions.md
│   ├── Test_Management.md
│   ├── API_Reference.md
│   └── ... (all downloaded pages)
│
└── jiradocai/                   ← Application
    ├── chroma_jira_db/          ← Vector database (created in Step 5)
    ├── download_xray_docs.py    ← Step 4: Download docs
    ├── 1_index_documents.py     ← Step 5: Index docs
    ├── 2_query_cli.py           ← Step 6: Query CLI
    ├── 3_query_web.py           ← Step 6: Query Web
    └── SETUP.md                 ← This file
```

---

## Troubleshooting

### "Ollama is not running"
```bash
# Start Ollama in a terminal (keep it running)
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull llama3.1:8b
```

### "No documents found"
```bash
# Run the download script first
python download_xray_docs.py

# Then index
python 1_index_documents.py
```

### Download fails or incomplete
```bash
# The script is safe to re-run
# It will skip already downloaded pages
python download_xray_docs.py
```

### Want to re-download everything
```bash
# Delete the folder and re-run
rm -rf /Users/ashish/Jira/xray_documentation
python download_xray_docs.py
```

---

## Updating Documentation

When Xray docs are updated on the website:

```bash
# Re-download docs
python download_xray_docs.py

# Re-index
python 1_index_documents.py
```

---

## Cost Summary

| Component | Cost |
|-----------|------|
| Ollama (LLM) | **$0** |
| HuggingFace Embeddings | **$0** |
| ChromaDB Vector DB | **$0** |
| Web Scraping | **$0** |
| Gradio Web UI | **$0** |
| **Total** | **$0** 🎉 |

---

## Privacy & Security

✅ Everything runs locally on your machine
✅ No data sent to external APIs
✅ No API keys required
✅ No cloud storage
✅ 100% private and secure

---

## Next Steps After Setup

1. **Explore**: Try different questions
2. **Share**: Show teammates the web interface
3. **Customize**: Adjust chunking, retrieval settings
4. **Extend**: Add more documentation sources
5. **Deploy**: Use Docker for production (see DOCKER_GUIDE.md)

---

## Quick Reference

```bash
# Start Ollama (keep running)
ollama serve

# Download Xray docs
python download_xray_docs.py

# Index docs (one-time)
python 1_index_documents.py

# Query - CLI
python 2_query_cli.py

# Query - Web UI
python 3_query_web.py
```

---

**Ready to start?** Begin with Step 1!

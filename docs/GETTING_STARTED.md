# Getting Started with JiraDocAI

Welcome to **JiraDocAI** - your AI-powered documentation assistant!

## What is JiraDocAI?

JiraDocAI uses RAG (Retrieval Augmented Generation) to let you ask questions about your Jira documentation and get accurate answers with source citations.

**Key Features:**
- 🤖 AI-powered Q&A over your documentation
- 📚 Automatic source citations for every answer
- 🆓 100% open source and free (only pay for Claude API usage)
- 🐳 Docker-ready for easy deployment
- 🌐 Beautiful web interface or CLI
- ⚡ Fast: Index once, query unlimited times

## Choose Your Setup Method

### Option 1: Docker (Recommended) 🐳

**Best for**: Isolation, production use, easy deployment

```bash
# 1. Set your API key
echo "ANTHROPIC_API_KEY=your-key" > .env

# 2. Build
docker-compose build

# 3. Index docs (one time)
docker-compose up -d jiradocai
docker exec -it jiradocai-assistant python 1_index_documents.py

# 4. Query
docker exec -it jiradocai-assistant python 2_query_cli.py

# Or use web UI
docker-compose --profile web up jiradocai-web
```

**📖 Full Docker Guide**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

### Option 2: Native Python 🐍

**Best for**: Development, testing, local experimentation

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY='your-key'

# 3. Index docs
python 1_index_documents.py

# 4. Query
python 2_query_cli.py

# Or web UI
python 3_query_web.py
```

**📖 Full Python Guide**: [README.md](README.md)

## Quick Start Video Guide

### Step 1: Get Your API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy it (keep it secret!)

### Step 2: Configure
```bash
cd /Users/ashish/Jira/jiradocai

# Create .env file
cp .env.example .env

# Edit .env and add your key
nano .env  # or use your favorite editor
```

### Step 3: Choose Your Path
- **Docker**: Follow [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- **Python**: Follow [README.md](README.md)

## File Guide

```
jiradocai/
├── GETTING_STARTED.md       ← You are here!
├── README.md                ← Native Python setup guide
├── DOCKER_GUIDE.md          ← Docker setup guide (recommended)
├── requirements.txt         ← Python dependencies
├── Dockerfile              ← Docker image configuration
├── docker-compose.yml      ← Docker Compose setup
├── .env.example            ← Environment variables template
├── .gitignore              ← Git ignore rules
│
├── 1_index_documents.py     ← Run once to index your docs
├── 2_query_cli.py          ← Command-line interface
├── 3_query_web.py          ← Web interface (Gradio)
│
└── chroma_jira_db/         ← Vector database (created automatically)
```

## Example Usage

### CLI Interface

```bash
$ python 2_query_cli.py

💬 You: How do I create a custom field in Jira?

🔍 Searching documentation...

======================================================================
📝 ANSWER
======================================================================
To create a custom field in Jira:
1. Go to Settings > Issues > Custom fields
2. Click "Add custom field"
3. Select field type
4. Configure and create

======================================================================
📚 SOURCES
======================================================================

[1] jira_admin_guide.md (Relevance: 92.3%)
    Path: /app/docs/admin_docs/jira_admin_guide.md
    Preview: "Custom fields allow you to capture additional..."

[2] field_config.md (Relevance: 87.1%)
    Path: /app/docs/config/field_config.md
    Preview: "Field types include: Text, Number, Date..."
======================================================================
```

### Web Interface

1. Run: `python 3_query_web.py`
2. Open: http://localhost:7860
3. Ask questions in the chat interface
4. Get answers with automatic source citations

## Cost Breakdown

| Component | Cost |
|-----------|------|
| LlamaIndex Framework | FREE ✅ |
| HuggingFace Embeddings | FREE ✅ (runs locally) |
| ChromaDB Vector Database | FREE ✅ (runs locally) |
| Claude API | ~$0.01-0.05 per 100 queries |
| **Total** | **~$0.01 per 100 queries** |

Want 100% free? Use Ollama instead of Claude! See guides for details.

## What Gets Indexed?

By default, JiraDocAI indexes:
- Markdown files (`.md`)
- Text files (`.txt`)
- PDF files (`.pdf`)
- Log files (`.log`)

From directory: `/Users/ashish/Jira/Issue1`

## Common Questions

### Do I need to re-index every time?
**No!** Index once, then query unlimited times. Only re-index when docs change.

### Can I use without Claude API?
**Yes!** Use Ollama for 100% free local LLM. See guides for setup.

### How accurate are the answers?
Very accurate - answers are grounded in your actual documentation with source citations showing relevance scores.

### Can I index multiple documentation sets?
Yes! Either combine them in one folder or configure multiple instances.

### Does this work offline?
Embeddings and vector database are local (offline). Only Claude API calls require internet. Use Ollama for 100% offline.

## Troubleshooting

### "API key not found"
```bash
# Check if set
echo $ANTHROPIC_API_KEY  # or check .env file

# Set it
export ANTHROPIC_API_KEY='your-key'
# or add to .env file
```

### "No documents found"
- Check that docs exist at: `/Users/ashish/Jira/Issue1`
- Ensure files have supported extensions (`.md`, `.txt`, `.pdf`, `.log`)
- Check file permissions

### "Database not found"
Run `1_index_documents.py` first to create the index.

### Slow indexing
Normal on first run (downloads embedding model ~100MB). Subsequent runs are fast.

## Next Steps

1. **Choose your setup method** (Docker or Python)
2. **Follow the guide** (DOCKER_GUIDE.md or README.md)
3. **Index your documentation** (`1_index_documents.py`)
4. **Start asking questions!** (CLI or Web)

## Advanced Topics

- **Custom chunking strategies**: See FREE_RAG_SETUP.md in knowledge folder
- **Production deployment**: See DOCKER_GUIDE.md
- **Alternative LLMs**: See README.md for Ollama setup
- **API deployment**: See FREE_RAG_SETUP.md for FastAPI example

## Resources

### Documentation
- [Main README](README.md) - Native Python setup
- [Docker Guide](DOCKER_GUIDE.md) - Docker setup
- [Free RAG Setup](../knowledge/FREE_RAG_SETUP.md) - Detailed implementation guide
- [RAG Implementation Guide](../knowledge/RAG_IMPLEMENTATION_GUIDE.md) - Comprehensive RAG guide

### External Links
- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [Claude API](https://console.anthropic.com/)
- [Docker Docs](https://docs.docker.com/)
- [ChromaDB](https://www.trychroma.com/)

## Support

Questions? Check:
1. This guide
2. README.md or DOCKER_GUIDE.md
3. Knowledge folder for detailed guides

## Contributing

This is your project! Feel free to:
- Modify chunking strategies
- Add new interfaces (Slack bot, Discord, etc.)
- Improve prompts
- Add new features

---

**Ready?** Choose your setup method above and get started!

**Recommended**: Start with [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for easiest setup.

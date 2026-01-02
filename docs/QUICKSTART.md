# JiraDocAI - Quick Start (100% FREE!)

**AI Assistant for Xray Documentation**

Index the entire Xray documentation website and ask questions with source citations!

**Source**: https://docs.getxray.app/space/XRAYCLOUD/393183414/App+Editions

## What You Get

- 💰 **100% FREE** - No API costs, no subscriptions
- 🔓 **100% Open Source** - LlamaIndex, Ollama, ChromaDB
- 🏠 **100% Local** - Everything runs on your machine
- 🌐 **Complete Xray Docs** - Automatically downloads entire documentation site
- 📚 **Source Citations** - See exactly which page answers come from
- ⚡ **Fast** - Index once, query unlimited times

## Step 1: Install Ollama (2 minutes)

Ollama is a free, local LLM runner (like running ChatGPT on your computer).

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
Download from: https://ollama.com/download

## Step 2: Start Ollama

```bash
# Terminal 1: Start the Ollama server
ollama serve
```

Keep this terminal open!

## Step 3: Pull a Model (1 minute)

In a **new terminal**:

```bash
# Download Llama 3.1 (4GB) - recommended
ollama pull llama3.1:8b

# Or other options:
# ollama pull mistral        # Mistral 7B
# ollama pull qwen2.5:7b     # Qwen 2.5
```

## Step 4: Install Python Dependencies (1 minute)

```bash
cd /Users/ashish/Jira/jiradocai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Download Xray Documentation (5-10 minutes, one-time)

```bash
# Install web scraping dependencies
pip install requests beautifulsoup4 html2text

# Download all Xray documentation
python download_xray_docs.py
```

This will:
- Crawl https://docs.getxray.app starting from App Editions
- Follow all links (up to 5 levels deep)
- Download all pages as Markdown
- Save to `/Users/ashish/Jira/xray_documentation/`

**Expected**: ~150 documents downloaded in 3-5 minutes

## Step 6: Index the Documentation (5-10 minutes, one-time)

```bash
python 1_index_documents.py
```

This will:
- Load all downloaded Xray docs
- Generate embeddings (locally, free)
- Store in ChromaDB
- Test with a sample query

**You only need to do this once!**

## Step 7: Start Asking Questions!

### Option A: Command Line (fastest)

```bash
python 2_query_cli.py
```

Then type your questions:
```
💬 You: How do I create a custom field in Jira?
```

### Option B: Web Interface (prettiest)

```bash
python 3_query_web.py
```

Opens in your browser at: http://localhost:7860

## Example Questions

About Xray documentation:

```
What are the different Xray App editions?
How do I create test cases in Xray?
What's the difference between test plans and test executions?
How do I integrate Xray with CI/CD?
What APIs does Xray provide?
How do I organize tests in test repositories?
What features are in the free tier?
How do I import automated test results?
```

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Ollama LLM | FREE 💰 |
| HuggingFace Embeddings | FREE 💰 |
| ChromaDB Vector Database | FREE 💰 |
| Gradio Web UI | FREE 💰 |
| **TOTAL** | **$0** 🎉 |

## Available Models

```bash
# Fast & efficient (recommended)
ollama pull llama3.1:8b      # 4GB

# More powerful
ollama pull llama3.1:70b     # 40GB (needs good GPU/RAM)

# Alternative options
ollama pull mistral          # 4GB
ollama pull qwen2.5:7b       # 4GB
ollama pull phi3             # 2GB (smaller, faster)

# List installed models
ollama list
```

## Switching Models

Edit any of the Python scripts and change this line:

```python
OLLAMA_MODEL = "llama3.1:8b"  # Change to your preferred model
```

## Troubleshooting

### "Ollama is not running"
```bash
# Start Ollama in a terminal
ollama serve

# Keep that terminal open
```

### "Model not found"
```bash
# Pull the model first
ollama pull llama3.1:8b
```

### "Database not found"
```bash
# Index your docs first
python 1_index_documents.py
```

### Slow responses
- Use a smaller model: `ollama pull phi3`
- Or use GPU acceleration (if you have NVIDIA GPU)

### Out of memory
- Use smaller model: `phi3` or `mistral:7b`
- Close other applications
- Reduce `similarity_top_k` in scripts (from 3 to 2)

## What's Different from Claude API?

| Aspect | JiraDocAI (Ollama) | Claude API |
|--------|-------------------|------------|
| Cost | **$0** | ~$0.01-0.05 per 100 queries |
| Privacy | **Everything local** | Data sent to Anthropic |
| Speed | Depends on your hardware | Fast (cloud) |
| Quality | Very good (Llama 3.1) | Excellent (Claude) |
| Setup | Need to install Ollama | Just API key |
| Internet | **Not needed** | Required |

## Tips & Tricks

### Speed Up Queries
```bash
# Keep Ollama running in background
brew services start ollama  # macOS
systemctl start ollama      # Linux
```

### Use GPU (if you have NVIDIA)
Edit scripts to enable GPU for embeddings:
```python
embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    device="cuda"
)
```

### Multiple Documentation Sets
Just put all docs in `/Users/ashish/Jira/Issue1` or update `DOCS_PATH` in the scripts.

## Next Steps

1. ✅ Start using: `python 2_query_cli.py` or `python 3_query_web.py`
2. 📖 Read detailed guides: `README.md` and `DOCKER_GUIDE.md`
3. 🎨 Customize: Edit chunking, retrieval, prompts
4. 🚀 Deploy: Use Docker for production

## Resources

- **Ollama**: https://ollama.com/
- **LlamaIndex**: https://docs.llamaindex.ai/
- **ChromaDB**: https://www.trychroma.com/
- **Models**: https://ollama.com/library

---

**Ready!** Run: `python 2_query_cli.py`

**Cost**: $0 | **Time**: 5 minutes | **Privacy**: 100% local

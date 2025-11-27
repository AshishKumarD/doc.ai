# JiraDocAI - Production-Ready Documentation AI Assistant

**Author:** Yuki
**Version:** 1.0.0

A powerful, production-ready documentation assistant that uses RAG (Retrieval Augmented Generation) to help you query documentation intelligently. Built with 100% open-source components.

## 🌟 Features

- **Master Configuration System**: Centralized control over all settings via JSON config or CLI
- **Documentation Source Management**: Track, enable/disable multiple documentation sets
- **Multi-Model Support**: Choose from 4 different ML models based on your RAM
- **Dual Execution Mode**: Run via Docker or Native Python
- **Web & CLI Interfaces**: Beautiful Gradio web UI or terminal CLI
- **Custom Documentation Scraping**: Scrape any documentation website
- **Production Ready**: Organized structure, proper logging, configuration management
- **Cross-Platform**: Works on macOS, Linux, and Windows (via Git Bash/WSL)

## 📁 Project Structure

```
docai/
├── docai.sh              # Main management script (ALL operations)
├── config/               # Configuration files
│   ├── docai_config.json       # Master configuration (NEW!)
│   ├── models.json             # ML model definitions
│   └── settings.env.example
├── src/                  # Source code
│   ├── config_manager.py       # Configuration manager (NEW!)
│   ├── core/                   # Core indexing & scraping
│   │   └── 1_index_documents.py
│   ├── cli/                    # Command-line interface
│   │   ├── 2_query_cli.py
│   │   └── quick_query.py
│   └── web/                    # Web interface
│       └── 3_query_web.py
├── scripts/              # Utility scripts
│   ├── config_cli.py           # Config management CLI (NEW!)
│   ├── download_xray_docs*.py
│   ├── query_chroma.py
│   └── cleanup_*.py
├── data/                 # Data directory
│   ├── documentation/          # Downloaded docs go here
│   └── chroma_db/              # Vector database
├── docker/               # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                 # Project documentation
│   ├── CONFIGURATION.md        # Configuration guide (NEW!)
│   ├── QUICK_CONFIG_REFERENCE.md (NEW!)
│   ├── GETTING_STARTED.md
│   ├── QUICKSTART.md
│   └── ...
└── requirements/         # Python dependencies
    ├── base.txt          # Core dependencies
    └── dev.txt           # Development dependencies
```

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.9+** - Check with: `python3 --version`
- **Ollama** - For running ML models locally ([Install Ollama](https://ollama.com/download))
- **Docker** (optional) - Only if you want to use Docker mode
- **8GB+ RAM** - Recommended for best performance

### Auto-Setup Wizard (3 Simple Steps!)

```bash
# 1. Make executable (one-time)
chmod +x docai.sh

# 2. Run the wizard
./docai.sh

# 3. Follow the prompts!
#    - Choose Python or Docker
#    - Select a model (wizard helps)
#    - Wizard checks for docs
#    - Wizard offers to index
#    - Choose Web UI or CLI
#    - Done! 🎉
```

**What the wizard does for you:**
- ✅ Detects your OS (Mac/Linux/Windows)
- ✅ Checks if Ollama is installed (shows install commands if needed)
- ✅ Auto-starts Ollama server
- ✅ Downloads selected model
- ✅ Scans for documentation in data folder
- ✅ Offers to index documentation
- ✅ Launches your chosen interface

**Time:** 5-10 minutes total (mostly model download)

### Manual Setup (Advanced)

For step-by-step manual control:

```bash
./docai.sh --manual
```

This shows the full menu with 15 options for advanced users who want fine-grained control over each step.

See [Auto Wizard Guide](docs/AUTO_WIZARD_GUIDE.md) for detailed information.

### Configuration Management (NEW!)

After initial setup, manage your configuration easily:

```bash
# View current settings
python3 scripts/config_cli.py show

# Interactive configuration menu
python3 scripts/config_cli.py

# List documentation sources
python3 scripts/config_cli.py docs --list

# Change model
python3 scripts/config_cli.py set --model llama3.2:3b

# Enable/disable documentation sources
python3 scripts/config_cli.py docs --enable myproject
python3 scripts/config_cli.py docs --disable oldproject
```

See [Configuration Guide](docs/QUICK_CONFIG_REFERENCE.md) for more details.

## 🎯 Daily Usage

### Quick Start (After Initial Setup)

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Launch DocAI**:
   ```bash
   ./docai.sh
   ```

3. **Choose your interface**:
   - Option 6: Web UI (recommended)
   - Option 7: CLI
   - Option 8: Quick Query

### Common Tasks

#### Query Documentation
```bash
# Web UI (recommended)
./docai.sh  # → Option 6

# CLI
./docai.sh  # → Option 7

# One-time query
./docai.sh  # → Option 8
```

#### Add New Documentation
```bash
# 1. Scrape new docs
./docai.sh  # → Option 3

# 2. Add to config
python3 scripts/config_cli.py docs --add myproject "My Project" ./data/documentation/myproject

# 3. Index the docs
./docai.sh  # → Option 4

# 4. Enable for queries
python3 scripts/config_cli.py docs --enable myproject
```

#### Switch Between Documentation Sets
```bash
# Disable current docs
python3 scripts/config_cli.py docs --disable project_a

# Enable different docs
python3 scripts/config_cli.py docs --enable project_b

# Now queries only search project_b!
```

#### Change Model
```bash
# Use lighter model for quick queries
python3 scripts/config_cli.py set --model qwen2.5:0.5b

# Use heavier model for complex queries
python3 scripts/config_cli.py set --model llama3.1:8b
```

### Main Menu Reference

Run `./docai.sh` to access these options:

**SETUP**
1. **Initial Setup** - Choose Docker or Native Python (first-time only)
2. **Select ML Model** - Choose/switch models (0.5B to 14B parameters)

**DOCUMENTATION**
3. **Scrape Documentation** - Download docs from any URL
4. **Index Documentation** - Create searchable vector database
5. **Manage Documentation** - View/delete documentation folders

**QUERY & USE**
6. **Launch Web UI** - Start Gradio web interface (http://localhost:7860)
7. **Launch CLI** - Interactive command-line interface
8. **Quick Query** - One-time query without opening full interface

**SYSTEM**
9. **Check System Status** - View configuration, models, data
10. **Start Ollama Server** - Start Ollama in background
11. **Stop Ollama Server** - Stop Ollama server
12. **View Logs** - Application, Docker, and Ollama logs
13. **Restart Services** - Restart Ollama or Docker containers
14. **Clean/Reset Data** - Clean database or documentation

**HELP**
15. **Documentation & Guides** - View help and troubleshooting

## 🤖 ML Model Options

Choose based on your system's RAM:

| Model | RAM | Parameters | Best For |
|-------|-----|------------|----------|
| Qwen2.5 0.5B | ~1GB | 0.5B | Low-end systems, quick responses |
| Llama 3.2 3B | ~4GB | 3B | Mid-range systems, balanced |
| Llama 3.1 8B | ~8GB | 8B | High-end systems, detailed (Recommended) |
| Qwen2.5 14B | ~14GB | 14B | Production, best quality |

## 📖 Complete Workflow Example

Here's a complete example of setting up and using DocAI:

### First-Time Setup Example

```bash
# 1. Navigate to project
cd /Users/ashish/Jira/docai

# 2. Make script executable (one-time)
chmod +x docai.sh

# 3. Initial setup
./docai.sh
# Select: 1 (Initial Setup)
# Choose: 2 (Native Python)
# Wait for dependencies to install...

# 4. Start Ollama (keep running in another terminal)
ollama serve

# 5. Select and download model
./docai.sh
# Select: 2 (Select ML Model)
# Choose: 3 (Llama 3.1 8B - Recommended)
# Wait for model download...

# 6. Add React documentation
./docai.sh
# Select: 3 (Scrape Documentation)
# Name: react_docs
# URL: https://react.dev/learn
# Depth: 5
# Wait for scraping...

# 7. Add to configuration
python3 scripts/config_cli.py docs --add \
  react_docs \
  "React Documentation" \
  ./data/documentation/react_docs \
  "https://react.dev/learn" \
  "Official React framework documentation"

# 8. Index the documentation
./docai.sh
# Select: 4 (Index Documentation)
# Choose: react_docs
# Wait for indexing...

# 9. Start Web UI
./docai.sh
# Select: 6 (Launch Web UI)
# Opens browser at http://localhost:7860

# 10. Ask questions!
# "How do I use useState hook in React?"
# "What is the difference between props and state?"
```

### Daily Usage Example

```bash
# Morning: Start Ollama
ollama serve

# Launch Web UI
./docai.sh  # → Option 6

# Query your documentation all day!

# Need different docs? Switch them:
python3 scripts/config_cli.py docs --disable react_docs
python3 scripts/config_cli.py docs --enable vue_docs
```

### Multi-Project Example

```bash
# Add multiple projects
./docai.sh  # Scrape Vue docs → Option 3
python3 scripts/config_cli.py docs --add vue_docs "Vue.js" ./data/documentation/vue_docs

./docai.sh  # Scrape Angular docs → Option 3
python3 scripts/config_cli.py docs --add angular_docs "Angular" ./data/documentation/angular_docs

# Index all
./docai.sh  # → Option 4 (repeat for each)

# Working on Vue project? Enable only Vue docs
python3 scripts/config_cli.py docs --disable react_docs
python3 scripts/config_cli.py docs --disable angular_docs
python3 scripts/config_cli.py docs --enable vue_docs

# Now queries only search Vue documentation!
./docai.sh  # → Option 6 (Web UI)
```

## 🐳 Docker Mode

When running in Docker mode:

```bash
# Build is automatic via jiradocai.sh option 1
# Or manually:
cd docker
docker-compose build

# Run services
docker-compose up -d

# Web UI
docker-compose --profile web up jiradocai-web
```

## 🐍 Python Mode

When running in native Python:

```bash
# Setup is automatic via jiradocai.sh option 1
# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/base.txt
```

## 🔧 Configuration

### Master Configuration System (NEW!)

DocAI now features a comprehensive master configuration system:

```bash
# View current configuration
python3 scripts/config_cli.py show

# Interactive configuration menu
python3 scripts/config_cli.py

# Manage documentation sources
python3 scripts/config_cli.py docs --list
python3 scripts/config_cli.py docs --add myproject "My Project" ./data/docs

# Change settings
python3 scripts/config_cli.py set --model llama3.1:8b
python3 scripts/config_cli.py set --mode python

# Validate configuration
python3 scripts/config_cli.py validate
```

**Features:**
- Centralized control via `config/docai_config.json`
- Manage multiple documentation sources
- Enable/disable docs without deleting them
- Track indexing status
- Python API for scripting

**Documentation:**
- Quick Start: `docs/QUICK_CONFIG_REFERENCE.md`
- Complete Guide: `docs/CONFIGURATION.md`

### Legacy Configuration

The system maintains backward compatibility:

```bash
# Environment variables still work
export OLLAMA_MODEL=llama3.1:8b
export CHROMA_DB_PATH=./data/chroma_db
export GRADIO_SERVER_PORT=7860

# Model configuration
cat .model_config          # Auto-synced with master config
```

## 📝 Real-World Example: Company Documentation

Let's say you want to add your company's internal documentation:

```bash
# 1. Scrape your company docs
./docai.sh
# Select: 3 (Scrape Documentation)
# Name: company_internal
# URL: https://docs.yourcompany.com
# Depth: 5

# 2. Add to configuration with metadata
python3 scripts/config_cli.py docs --add \
  company_internal \
  "Company Internal Docs" \
  ./data/documentation/company_internal \
  "https://docs.yourcompany.com" \
  "Internal company documentation and procedures"

# 3. Index the docs
./docai.sh
# Select: 4 (Index Documentation)
# Choose: company_internal

# 4. Query with Web UI
./docai.sh
# Select: 6 (Launch Web UI)
# Ask: "What is our vacation policy?"
# Ask: "How do I submit an expense report?"
# Ask: "What are the deployment procedures?"
```

### Example: Xray Cloud Documentation

```bash
./docai.sh
# Option 3: Scrape Documentation
# Name: xray_cloud
# URL: https://docs.getxray.app/space/XRAYCLOUD/
# Depth: 5

# Add to config
python3 scripts/config_cli.py docs --add xray_cloud "Xray Cloud" ./data/documentation/xray_cloud

# Option 4: Index Documentation
# Select: xray_cloud

# Option 6: Launch Web UI
# Ask: "How do I configure permissions in Xray?"
# Ask: "How do I create test execution?"
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Ollama Not Running

**Error**: "Could not connect to Ollama"

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# In another terminal, verify model is downloaded
ollama list
```

#### 2. Model Not Found

**Error**: "Model 'llama3.1:8b' not found"

**Solution**:
```bash
# Pull the model
ollama pull llama3.1:8b

# Verify it's downloaded
ollama list

# Update DocAI config
python3 scripts/config_cli.py set --model llama3.1:8b
```

#### 3. Permission Denied on docai.sh

**Error**: "Permission denied: ./docai.sh"

**Solution**:
```bash
chmod +x docai.sh
```

#### 4. Python Virtual Environment Issues

**Error**: "venv not found" or "module not found"

**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
./docai.sh
# Select: 1 (Initial Setup) → 2 (Python)
```

#### 5. Database/Index Not Found

**Error**: "ChromaDB not found" or "No index available"

**Solution**:
```bash
# Re-index your documentation
./docai.sh
# Select: 4 (Index Documentation)
# Choose the documentation folder
```

#### 6. Documentation Scraping Fails

**Error**: "Failed to scrape" or "Connection error"

**Solution**:
```bash
# Check internet connection
ping google.com

# Try with higher timeout
# Edit config/docai_config.json:
# "scraper.timeout_seconds": 60

# Or scrape manually and place files in data/documentation/
```

#### 7. Web UI Port Already in Use

**Error**: "Port 7860 is already allocated"

**Solution**:
```bash
# Change port in configuration
python3 scripts/config_cli.py set --key interfaces.web_ui.port --value 8080

# Or kill process using the port
lsof -ti:7860 | xargs kill -9
```

#### 8. Out of Memory Errors

**Error**: "Out of memory" or "Killed"

**Solution**:
```bash
# Use a lighter model
python3 scripts/config_cli.py set --model qwen2.5:0.5b

# Or reduce chunk size
python3 scripts/config_cli.py set --key query_engine.chunk_size --value 512
```

#### 9. Configuration File Not Found

**Error**: "config/docai_config.json not found"

**Solution**:
```bash
# Check if file exists
ls -la config/docai_config.json

# If missing, restore from backup
cp config/docai_config.json.bak config/docai_config.json

# Or check out from git
git checkout config/docai_config.json
```

#### 10. Queries Return No Results

**Problem**: Queries don't find relevant information

**Solution**:
```bash
# 1. Verify documentation is indexed
python3 scripts/config_cli.py docs --list

# 2. Check if source is enabled
python3 scripts/config_cli.py docs --enable your_docs

# 3. Verify ChromaDB exists
ls -la data/chroma_db/

# 4. Re-index if needed
./docai.sh  # → Option 4

# 5. Increase similarity results
python3 scripts/config_cli.py set --key query_engine.similarity_top_k --value 10
```

### Getting More Help

```bash
# Check system status
./docai.sh  # → Option 9

# View logs
./docai.sh  # → Option 12

# Validate configuration
python3 scripts/config_cli.py validate

# Read documentation
cat docs/QUICK_CONFIG_REFERENCE.md
cat docs/CONFIGURATION.md
```

### Still Having Issues?

1. Check the logs: `./docai.sh` → Option 12
2. Validate config: `python3 scripts/config_cli.py validate`
3. Read guides in `docs/` folder
4. Check GitHub issues or create a new one

## 📚 Documentation

- **Getting Started**: `docs/GETTING_STARTED.md`
- **Quick Start**: `docs/QUICKSTART.md`
- **Docker Guide**: `docs/DOCKER_GUIDE.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Setup Guide**: `docs/SETUP.md`

## 🔐 Security

- All processing happens locally
- No data sent to external services
- Ollama models run on your machine
- Documentation stays on your filesystem

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

Built with open-source tools:
- **Ollama** - Local LLM execution
- **ChromaDB** - Vector database
- **LlamaIndex** - RAG framework
- **Gradio** - Web UI
- **HuggingFace** - Embedding models

## 📞 Support

For issues or questions:
- Check `docs/` folder for guides
- Run `./jiradocai.sh` → Option 13 for troubleshooting
- Review logs: `./jiradocai.sh` → Option 10

---

**Made with ❤️ by Yuki**

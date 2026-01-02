# DocAI Auto-Setup Wizard Guide

**Version**: 2.0
**Created**: 2025-11-26
**Status**: Production Ready

## Overview

DocAI now features an intelligent auto-setup wizard that guides new users through the entire setup process in 6 easy steps. No technical knowledge required!

## Two Modes

### Auto Mode (Default)
```bash
./docai.sh
```

**Perfect for:**
- First-time users
- Quick setup
- Guided experience

**Features:**
- Step-by-step wizard
- OS detection
- Smart setup
- Auto-configuration

### Manual Mode
```bash
./docai.sh --manual
# or
./docai.sh -m
```

**Perfect for:**
- Experienced users
- Advanced operations
- Fine-grained control

**Features:**
- Full 15-option menu
- Individual operation control
- All advanced features

---

## Auto-Setup Wizard Flow

### Step 1: Choose Execution Mode

**Smart Detection:**
The wizard first checks if you've already configured an execution mode by looking for `.exec_mode` file.

**If already configured:**
```
Step 1/6: Check Execution Mode

✓ Execution mode already configured: python
✓ Python environment ready

Press Enter to continue...
```

**If not configured, prompts:**
```
How would you like to run DocAI?

  1) Python (Recommended)
     - Direct execution
     - Easier to debug
     - Works on Mac, Linux, Windows (Git Bash/WSL)

  2) Docker
     - Isolated environment
     - Easy deployment
     - Requires Docker installed

Choose [1-2]:
```

**What happens:**
- **Already configured**: Verifies the environment is still valid, skips asking
- **New setup**: Python creates venv and installs dependencies, Docker builds image

---

### Step 2: Check Ollama

**What it does:**
1. Checks if Ollama is installed
2. Detects your OS (Mac/Linux/Windows)
3. Shows installation instructions if needed
4. Checks if Ollama server is running
5. Attempts to auto-start Ollama
6. Waits for confirmation if needed

**OS Detection:**

**macOS:**
```bash
brew install ollama
# or download from: https://ollama.com/download
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
```
Download from: https://ollama.com/download
```

**Auto-start:**
- Attempts: `nohup ollama serve > /tmp/ollama.log 2>&1 &`
- Waits 3 seconds to verify
- Falls back to manual instructions if fails

---

### Step 3: Select AI Model

**Smart Detection:**
The wizard first checks if you've already configured a model by looking for `.model_config` file.

**If already configured and model is available:**
```
Step 3/6: Check AI Model

✓ Model already configured: llama3.1:8b
✓ Model is downloaded and ready

Press Enter to continue...
```

**If already configured but model needs download:**
```
Step 3/6: Check AI Model

✓ Model already configured: llama3.1:8b
⚠ Model not found locally, downloading...

[download progress shown]

✓ Model downloaded successfully
```

**If not configured, displays full selection:**
```
Step 3/6: Select AI Model

Checking downloaded models...

═══ DOWNLOADED MODELS (Ready to Use) ═══

  1) llama3.1:8b [READY]
  2) qwen2.5:0.5b [READY]

═══ RECOMMENDED MODELS (Download if Needed) ═══

Choose a model based on your system's RAM:

  3) Qwen2.5 0.5B  - ~1GB RAM  (fastest, basic quality)
  4) Llama 3.2 3B  - ~4GB RAM  (balanced)
  5) Llama 3.1 8B  - ~8GB RAM  (recommended, best quality)
  6) Qwen2.5 14B   - ~14GB RAM (production, highest quality)

  7) Enter custom model name

Choose model [1-7]:
```

**Options:**
- **Downloaded models** (1-N): Use immediately without download
- **Recommended models** (N+1 to N+4): Download if not already available
- **Custom model** (last option): Enter any Ollama model name

**What happens:**
1. **Already configured**: Uses existing model, only downloads if missing
2. **New setup**: Shows full selection, downloads chosen model
3. Saves to `.model_config`
4. Updates `config/docai_config.json`

**Models:**

| Model | RAM | Speed | Quality | Use Case |
|-------|-----|-------|---------|----------|
| Qwen2.5 0.5B | ~1GB | Fastest | Basic | Quick queries, low RAM |
| Llama 3.2 3B | ~4GB | Fast | Good | General use |
| Llama 3.1 8B | ~8GB | Medium | Excellent | Recommended |
| Qwen2.5 14B | ~14GB | Slower | Best | Production |

---

### Step 4: Check Documentation

**What it does:**
1. Scans `data/documentation/` folder
2. Lists found documentation sources
3. Counts documentation folders

**If documentation found:**
```
✓ Found 2 documentation folder(s)

Available documentation:
  - xray_cloud
  - react_docs
```

**If no documentation:**
```
No documentation found

You can add documentation later using:
  - Option 3: Scrape Documentation (from URL)
  - Or manually place docs in: ./data/documentation

Continue without documentation? [y/n]:
```

---

### Step 5: Index Documentation

**Only runs if documentation exists**

**Checks:**
1. Does ChromaDB exist?
2. Is it populated?

**If already indexed:**
```
✓ Documentation index already exists

Re-index documentation? [y/n]:
```

**If not indexed:**
```
Documentation needs to be indexed

This creates a searchable database from your documentation.
It only needs to be done once (takes 2-5 minutes).

Index documentation now? [y/n]:
```

**What happens during indexing:**
- Loads all documents
- Creates embeddings (vector representations)
- Stores in ChromaDB
- Shows progress
- Saves for future queries

---

### Step 6: Launch Interface

**Final step!**

**Prompt:**
```
✓ Setup complete!

How would you like to use DocAI?

  1) Web UI (Recommended)
     - Beautiful graphical interface
     - Opens in your browser
     - Best for extended use

  2) CLI
     - Terminal-based interface
     - Interactive chat
     - Good for quick queries

  3) Exit (launch manually later)

Choose [1-3]:
```

**Options:**

**1. Web UI:**
- Launches Gradio interface
- Opens at http://localhost:7860
- Shows system information
- Multi-source querying

**2. CLI:**
- Terminal-based chat
- Interactive prompt
- Keyboard shortcuts
- Source citations

**3. Exit:**
- Completes setup
- Shows how to launch later
- Exits wizard

---

## Smart Features

### Configuration Memory

**The wizard remembers your choices!** It checks for existing configuration before asking questions:

| Configuration | File Checked | Smart Behavior |
|--------------|--------------|----------------|
| **Execution Mode** | `.exec_mode` | Skips asking, verifies environment still valid |
| **AI Model** | `.model_config` | Skips selection, only downloads if missing |
| **Documentation** | `data/chroma_db/` | Skips indexing if already done |
| **Ollama** | Running process | Auto-starts if not running |

**Result:** On subsequent runs, the wizard skips to Step 6 (Launch Interface) if everything is configured!

### OS Detection

Automatically detects your operating system:
```bash
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS-specific instructions
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux-specific instructions
else
    # Windows-specific instructions
fi
```

### Smart Skipping Logic

**Step 1 - Execution Mode:**
- ✅ **Configured**: `.exec_mode` exists → Skip asking, verify environment
- ❌ **Not configured**: Ask user to choose Python or Docker

**Step 2 - Ollama:**
- ✅ **Running**: Continue immediately
- ❌ **Not running**: Auto-start or wait for user

**Step 3 - AI Model:**
- ✅ **Configured & Downloaded**: `.model_config` exists and model present → Skip selection
- ✅ **Configured but Missing**: Auto-download the configured model
- ❌ **Not configured**: Show full model selection menu

**Steps 4-5 - Documentation:**
- ✅ **Already indexed**: ChromaDB exists → Ask if re-index needed
- ❌ **Not indexed**: Ask if user wants to index now

**Step 6 - Launch:**
- Always shown (user chooses how to use DocAI)

### Auto-Start Ollama

Attempts to start Ollama automatically:
```bash
nohup ollama serve > /tmp/ollama.log 2>&1 &
```

Falls back to manual if fails.

### Configuration Sync

Updates both legacy and new config:
- `.model_config` (legacy)
- `config/docai_config.json` (new)
- Maintains backward compatibility

---

## Web UI Enhancements

### System Information Panel

**New expandable panel showing:**
- **Model:** Current LLM (e.g., llama3.1:8b)
- **Ollama Status:** 🟢 Running / 🔴 Not Running
- **Ollama Host:** http://localhost:11434
- **Documentation Sources:** Count of indexed sources
- **Embedding Model:** BAAI/bge-small-en-v1.5
- **Available Documentation:** List of all indexed docs

**Location:**
- Top of Web UI
- Collapsed by default
- Click "📊 System Information" to expand

**Example:**
```markdown
### Current Configuration
- **Model:** `llama3.1:8b`
- **Ollama Status:** 🟢 Running
- **Ollama Host:** `http://localhost:11434`
- **Documentation Sources:** 2 indexed
- **Embedding Model:** BAAI/bge-small-en-v1.5

### Available Documentation
- ✓ Xray Cloud Documentation
- ✓ React Documentation
```

---

## Usage Examples

### First-Time Setup

```bash
# Navigate to project
cd /Users/ashish/Jira/docai

# Run auto wizard
./docai.sh

# Follow prompts:
# Step 1: Choose Python
# Step 2: Wait for Ollama check
# Step 3: Choose model (3 - Llama 3.1 8B)
# Step 4: Documentation detected
# Step 5: Index now? Yes
# Step 6: Choose Web UI

# Done! Interface opens in browser
```

**Time:** 5-10 minutes (depending on model download)

### Already Set Up

```bash
./docai.sh

# Wizard detects existing configuration:
# Step 1: ✓ Execution mode configured: python
# Step 2: ✓ Ollama running
# Step 3: ✓ Model configured: llama3.1:8b
# Step 4: ✓ Documentation found
# Step 5: ✓ Already indexed
# Step 6: Choose interface (Web UI/CLI/Exit)

# Total time: ~5 seconds!
# Just press Enter through confirmations and choose your interface
```

**No more repetitive questions!** The wizard is now truly intelligent.

### Manual Control

```bash
./docai.sh --manual

# Shows full menu:
#   1) Initial Setup
#   2) Select Model
#   3) Scrape Docs
#   ... etc

# Choose specific operations
```

### Quick Launch After Setup

```bash
# For Web UI
./docai.sh
# → Wizard → Step 6 → Choose 1 (Web UI)

# Or manually:
./docai.sh --manual
# → Choose 6 (Launch Web UI)
```

---

## Troubleshooting Auto Wizard

### Ollama Won't Start

**Problem:** Wizard can't start Ollama automatically

**Solution:**
```bash
# In another terminal:
ollama serve

# Then press Enter in wizard
```

### Model Download Fails

**Problem:** Network issues during model download

**Solution:**
```bash
# Exit wizard
# Download manually:
ollama pull llama3.1:8b

# Re-run wizard
./docai.sh
```

### No Documentation Found

**Problem:** Wizard can't find any docs

**Options:**

1. **Skip for now:**
   - Choose "y" to continue
   - Add docs later with manual mode

2. **Add documentation:**
   - Exit wizard
   - Run: `./docai.sh --manual`
   - Choose: 3 (Scrape Documentation)
   - Re-run wizard

3. **Manual placement:**
   ```bash
   # Place docs in:
   mkdir -p data/documentation/my_docs
   # Add files...

   # Re-run wizard
   ./docai.sh
   ```

### Indexing Fails

**Problem:** Indexing crashes or fails

**Check:**
```bash
# 1. Check Python dependencies
./docai.sh --manual
# Choose: 9 (System Status)

# 2. Check ChromaDB path
ls -la data/chroma_db

# 3. Re-run indexing
./docai.sh --manual
# Choose: 4 (Index Documentation)
```

### Web UI Port Conflict

**Problem:** Port 7860 already in use

**Solution:**
```bash
# Check what's using port
lsof -ti:7860

# Kill process:
lsof -ti:7860 | xargs kill -9

# Or change port:
python3 scripts/config_cli.py set --key interfaces.web_ui.port --value 8080
```

---

## Comparison: Auto vs Manual

| Feature | Auto Mode | Manual Mode |
|---------|-----------|-------------|
| **Entry Point** | `./docai.sh` | `./docai.sh --manual` |
| **User Level** | Beginners | Advanced |
| **Guidance** | Step-by-step | Self-directed |
| **Setup Time** | 5-10 min | Varies |
| **Control** | Guided choices | Full control |
| **Best For** | First use | Fine-tuning |

**When to use Auto:**
- First time using DocAI
- Quick setup needed
- Want guided experience
- Don't want to remember options

**When to use Manual:**
- Need specific operation
- Advanced configuration
- Troubleshooting
- Multiple operations

---

## Technical Details

### Wizard Implementation

**Location:** `docai.sh` lines 1402-1706

**Key Functions:**
- `auto_setup_wizard()` - Main wizard flow
- `manual_mode()` - Traditional menu
- `main()` - Mode dispatcher

**Argument Parsing:**
```bash
if [ "$1" = "--manual" ] || [ "$1" = "-m" ]; then
    manual_mode
else
    auto_setup_wizard
fi
```

### Configuration Updates

**Files modified by wizard:**
1. `.exec_mode` - Execution mode (python/docker)
2. `.model_config` - Selected model
3. `config/docai_config.json` - Master config

**Sync mechanism:**
```bash
# Save to legacy config
echo "OLLAMA_MODEL=$selected_model" > .model_config

# Update master config
venv/bin/python3 scripts/config_cli.py set --model "$selected_model"
```

### Web UI Changes

**File:** `src/web/3_query_web.py` lines 209-229

**Added:**
- System information accordion
- Dynamic status indicators
- Model display
- Documentation list

---

## Future Enhancements

**Potential additions:**
- [ ] Resume wizard from specific step
- [ ] Configuration profiles (dev/prod)
- [ ] Automatic dependency updates
- [ ] Multi-language support
- [ ] Docker Compose detection
- [ ] GPU detection and optimization
- [ ] Wizard progress bar
- [ ] Setup validation tests

---

## Summary

The Auto-Setup Wizard makes DocAI accessible to everyone:

✅ **No technical knowledge required**
✅ **6 simple steps**
✅ **Intelligent OS detection**
✅ **Auto-configuration**
✅ **Smart configuration memory** - Never asks the same question twice!
✅ **5 seconds on subsequent runs** - Just press Enter and go!
✅ **Ready to use in minutes**

Try it now:
```bash
./docai.sh
```

For advanced users:
```bash
./docai.sh --manual
```

---

**Questions?** Check the main README or run:
```bash
./docai.sh --manual
# → Option 15 (Documentation & Guides)
```

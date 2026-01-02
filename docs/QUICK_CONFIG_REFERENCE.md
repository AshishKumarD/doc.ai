# DocAI Configuration Quick Reference

Quick reference for the most common configuration tasks.

## 🚀 Quick Start

```bash
# Interactive configuration menu
python scripts/config_cli.py

# View current settings
python scripts/config_cli.py show
```

## 📋 Common Commands

### View Configuration

```bash
# Summary
python scripts/config_cli.py show

# Documentation sources
python scripts/config_cli.py show --sources

# Specific value
python scripts/config_cli.py show --key models.llm.model_name
```

### Change Model

```bash
# Set model
python scripts/config_cli.py set --model llama3.1:8b

# Available models
python scripts/config_cli.py show --key models.available_models
```

### Change Execution Mode

```bash
# Python mode
python scripts/config_cli.py set --mode python

# Docker mode
python scripts/config_cli.py set --mode docker
```

### Manage Documentation

```bash
# List all docs
python scripts/config_cli.py docs --list

# Add new source
python scripts/config_cli.py docs --add \
  myproject "My Project" ./data/documentation/myproject

# Enable/disable
python scripts/config_cli.py docs --enable myproject
python scripts/config_cli.py docs --disable oldproject

# Remove
python scripts/config_cli.py docs --remove oldproject

# View details
python scripts/config_cli.py docs --info myproject
```

### Validation & Export

```bash
# Validate config
python scripts/config_cli.py validate

# Export to env file
python scripts/config_cli.py export
```

## 🎯 Common Tasks

### Setup New Model

```bash
# 1. Check available models
python scripts/config_cli.py show --key models.available_models

# 2. Set model
python scripts/config_cli.py set --model llama3.2:3b

# 3. Verify
python scripts/config_cli.py show
```

### Add New Documentation

```bash
# 1. Add to config
python scripts/config_cli.py docs --add \
  vue_docs \
  "Vue.js Documentation" \
  ./data/documentation/vue \
  "https://vuejs.org/guide" \
  "Vue.js framework documentation"

# 2. Scrape docs (using docai.sh)
./docai.sh  # Option 3

# 3. Index docs (using docai.sh)
./docai.sh  # Option 4

# 4. Verify
python scripts/config_cli.py docs --info vue_docs
```

### Switch Between Doc Sets

```bash
# Scenario: Working on React project, want only React docs

# Disable all
python scripts/config_cli.py docs --disable vue_docs
python scripts/config_cli.py docs --disable angular_docs

# Enable React
python scripts/config_cli.py docs --enable react_docs

# Verify active sources
python scripts/config_cli.py show --sources
```

### Change Web UI Port

```bash
# Set port
python scripts/config_cli.py set --key interfaces.web_ui.port --value 8080

# Verify
python scripts/config_cli.py show --key interfaces.web_ui.port
```

### Adjust Query Settings

```bash
# More results per query
python scripts/config_cli.py set --key query_engine.similarity_top_k --value 10

# Larger chunks
python scripts/config_cli.py set --key query_engine.chunk_size --value 2048

# View current settings
python scripts/config_cli.py show --key query_engine
```

## 🔧 Configuration Keys

### Most Commonly Modified

| Key | Description | Example Value |
|-----|-------------|---------------|
| `models.llm.model_name` | LLM model | `llama3.1:8b` |
| `models.llm.temperature` | Response randomness | `0.7` |
| `execution.mode` | Execution mode | `python` or `docker` |
| `interfaces.web_ui.port` | Web UI port | `7860` |
| `query_engine.similarity_top_k` | Results per query | `5` |
| `query_engine.chunk_size` | Document chunk size | `1024` |
| `scraper.max_depth` | Crawl depth | `5` |

### Quick Set Examples

```bash
# Model settings
python scripts/config_cli.py set --key models.llm.temperature --value 0.5
python scripts/config_cli.py set --key models.llm.max_tokens --value 4096

# Query settings
python scripts/config_cli.py set --key query_engine.similarity_top_k --value 10
python scripts/config_cli.py set --key query_engine.chunk_size --value 2048

# Scraper settings
python scripts/config_cli.py set --key scraper.max_depth --value 10
python scripts/config_cli.py set --key scraper.delay_seconds --value 2
```

## 🐍 Python API Quick Reference

```python
from src.config_manager import ConfigManager

# Initialize
cm = ConfigManager()

# Get values
model = cm.get('models.llm.model_name')
port = cm.get('interfaces.web_ui.port')

# Set values
cm.set('models.llm.model_name', 'llama3.1:8b')
cm.set('interfaces.web_ui.port', 8080)

# Shortcuts
cm.set_model('llama3.1:8b')
cm.set_execution_mode('python')

# Documentation sources
sources = cm.get_documentation_sources(enabled_only=True)
cm.add_documentation_source('my_docs', 'My Docs', './data/docs')
cm.enable_documentation_source('my_docs')
cm.mark_source_indexed('my_docs')

# Validate
is_valid, errors = cm.validate()

# Export
cm.export_to_env('config/settings.env')
```

## 📁 File Locations

| File | Purpose |
|------|---------|
| `config/docai_config.json` | Master configuration file |
| `config/docai_config.json.bak` | Automatic backup |
| `src/config_manager.py` | Python configuration manager |
| `scripts/config_cli.py` | CLI tool |
| `.model_config` | Legacy model config (auto-synced) |
| `.exec_mode` | Legacy exec mode (auto-synced) |

## ⚠️ Troubleshooting

### Config Not Loading

```bash
# Check file exists
ls -l config/docai_config.json

# Validate JSON
python -m json.tool config/docai_config.json

# Restore from backup
cp config/docai_config.json.bak config/docai_config.json
```

### Validation Errors

```bash
# Run validation
python scripts/config_cli.py validate

# Common fixes:
# - Ensure paths exist
# - Check JSON syntax
# - Verify required sections present
```

### Changes Not Taking Effect

```bash
# Check if config was actually saved
cat config/docai_config.json | grep -A2 "last_updated"

# Re-export env file if needed
python scripts/config_cli.py export

# Restart services
./docai.sh  # Option 13 (Restart Services)
```

## 💡 Tips

1. **Always validate after manual edits**: `python scripts/config_cli.py validate`
2. **Use interactive mode for exploration**: `python scripts/config_cli.py`
3. **Enable only docs you need**: Improves query speed and relevance
4. **Keep model config synced**: Changes in either `.model_config` or master config sync automatically
5. **Back up before major changes**: Config manager creates `.bak` files automatically
6. **Use descriptive source IDs**: Makes management easier (e.g., `react_v18_docs` not `docs1`)

## 📚 More Information

- Full documentation: [docs/CONFIGURATION.md](./CONFIGURATION.md)
- Config manager source: [src/config_manager.py](../src/config_manager.py)
- CLI tool source: [scripts/config_cli.py](../scripts/config_cli.py)

## 🆘 Getting Help

```bash
# CLI help
python scripts/config_cli.py --help
python scripts/config_cli.py show --help
python scripts/config_cli.py docs --help

# Interactive mode
python scripts/config_cli.py

# View current config
python scripts/config_cli.py show
```

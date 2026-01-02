# Master Configuration System - Overview

> **Created**: 2025-11-26
> **Version**: 1.0.0
> **Status**: ✅ Production Ready

## What Was Created

A comprehensive master configuration system for DocAI that provides centralized control over all application settings, documentation sources, models, and system parameters.

## 📁 Files Created

### Core Components

1. **`config/docai_config.json`**
   - Master configuration file
   - Single source of truth for all settings
   - Includes execution, models, documentation, database, query engine, interfaces, scraper, logging, and performance settings

2. **`src/config_manager.py`** (713 lines)
   - Python configuration manager class
   - Full CRUD operations for all config sections
   - Documentation source management
   - Validation and export functionality
   - Backward compatibility with legacy config files
   - CLI interface for standalone use

3. **`scripts/config_cli.py`** (515 lines)
   - Interactive CLI tool for configuration management
   - Menu-driven interface
   - Command-line arguments for scripting
   - Color-coded output for better UX

### Documentation

4. **`docs/CONFIGURATION.md`**
   - Complete configuration guide
   - API reference
   - Integration examples
   - Troubleshooting guide

5. **`docs/QUICK_CONFIG_REFERENCE.md`**
   - Quick reference for common tasks
   - Command cheat sheet
   - Common configuration scenarios

## 🎯 Key Features

### 1. Centralized Configuration

All settings in one place:
- Execution mode (Python/Docker)
- ML models (LLM and embedding)
- Documentation sources with enable/disable
- Database settings
- Query engine parameters
- Web UI, CLI, and API interfaces
- Scraper configuration
- Logging and performance settings

### 2. Documentation Source Management

Track and control multiple documentation sets:
- Add/remove documentation sources
- Enable/disable sources individually
- Track indexing status
- Metadata and tagging support
- Priority management

### 3. Backward Compatibility

Seamlessly integrates with existing system:
- Auto-syncs with `.model_config`
- Auto-syncs with `.exec_mode`
- Works with existing `docai.sh` script
- No breaking changes to current workflow

### 4. Validation & Safety

Built-in protection:
- Configuration validation
- Automatic backups before changes
- JSON syntax checking
- Path verification

### 5. Export Functionality

Generate environment files:
- Export to `settings.env` format
- Compatible with Docker and scripts
- Auto-generated from master config

## 🚀 Quick Start

### 1. View Current Configuration

```bash
# Summary
python scripts/config_cli.py show

# Documentation sources
python scripts/config_cli.py show --sources
```

**Output:**
```
======================================================================
DocAI Configuration Summary
======================================================================

Version: 1.0.0
Last Updated: 2025-11-26T10:06:32.103695

Execution Mode: python
LLM Model: llama3.1:8b
Embedding Model: BAAI/bge-small-en-v1.5

Documentation Sources:
  Total: 1
  Enabled: 1
  Indexed: 0

Interfaces:
  Web UI: Enabled
  CLI: Enabled
  API: Disabled
======================================================================
```

### 2. Interactive Mode

```bash
python scripts/config_cli.py
```

Provides a menu-driven interface for all configuration tasks.

### 3. Common Tasks

```bash
# Change model
python scripts/config_cli.py set --model llama3.2:3b

# Change execution mode
python scripts/config_cli.py set --mode docker

# Add documentation source
python scripts/config_cli.py docs --add \
  vue_docs "Vue Documentation" ./data/documentation/vue

# Enable/disable sources
python scripts/config_cli.py docs --enable vue_docs
python scripts/config_cli.py docs --disable old_docs

# Validate configuration
python scripts/config_cli.py validate

# Export to env file
python scripts/config_cli.py export
```

## 📊 Configuration Structure

```
docai_config.json
├── version & metadata
├── execution
│   ├── mode (python/docker)
│   ├── python_version_required
│   └── docker_image
├── models
│   ├── llm (Ollama config)
│   ├── embedding
│   └── available_models (catalog)
├── documentation
│   ├── base_path
│   ├── sources[] (managed docs)
│   │   ├── id
│   │   ├── name
│   │   ├── path
│   │   ├── enabled
│   │   ├── indexed
│   │   ├── last_indexed
│   │   ├── source_url
│   │   ├── description
│   │   └── tags
│   └── options
├── database (ChromaDB)
├── query_engine
│   ├── similarity_top_k
│   ├── response_mode
│   ├── chunk_size
│   └── chunk_overlap
├── interfaces
│   ├── web_ui
│   ├── cli
│   └── api
├── scraper
│   ├── delay_seconds
│   ├── max_depth
│   ├── max_pages
│   └── content_selectors
├── logging
├── performance
└── paths
```

## 🔌 Integration with Existing System

### With docai.sh

The shell script continues to work as before. Config changes sync automatically:

```bash
./docai.sh  # Select option 2 (Select ML Model)
# This updates both .model_config AND docai_config.json

python scripts/config_cli.py show  # Shows updated model
```

### In Python Code

```python
from src.config_manager import ConfigManager

# Initialize
cm = ConfigManager()

# Get settings
model = cm.get_model()
sources = cm.get_documentation_sources(enabled_only=True)

# Use in your code
for source in sources:
    print(f"Processing: {source['name']} at {source['path']}")
```

### Legacy Compatibility

The system maintains backward compatibility:

```bash
# Old way (still works)
cat .model_config
# Output: OLLAMA_MODEL=llama3.1:8b

# New way
python scripts/config_cli.py show --key models.llm.model_name
# Output: "llama3.1:8b"

# Both stay in sync automatically
```

## 🎨 Use Cases

### 1. Managing Multiple Documentation Sets

**Scenario**: You work on multiple projects and want to switch between their docs.

```bash
# Add all your project docs
python scripts/config_cli.py docs --add \
  project_a "Project A Docs" ./data/documentation/project_a

python scripts/config_cli.py docs --add \
  project_b "Project B Docs" ./data/documentation/project_b

# When working on Project A
python scripts/config_cli.py docs --enable project_a
python scripts/config_cli.py docs --disable project_b

# When working on Project B
python scripts/config_cli.py docs --disable project_a
python scripts/config_cli.py docs --enable project_b

# Now your queries only search relevant docs!
```

### 2. Different Models for Different Tasks

**Scenario**: Use lightweight model for quick queries, heavy model for complex analysis.

```bash
# Quick queries
python scripts/config_cli.py set --model qwen2.5:0.5b
./docai.sh  # Option 8 (Quick Query)

# Deep analysis
python scripts/config_cli.py set --model llama3.1:8b
./docai.sh  # Option 6 (Launch Web UI)
```

### 3. Environment-Specific Configuration

**Scenario**: Different settings for development vs production.

```bash
# Development
python scripts/config_cli.py set --mode python
python scripts/config_cli.py set --key interfaces.web_ui.port --value 7860
python scripts/config_cli.py set --key logging.level --value DEBUG

# Production
python scripts/config_cli.py set --mode docker
python scripts/config_cli.py set --key interfaces.web_ui.port --value 80
python scripts/config_cli.py set --key logging.level --value WARNING
```

### 4. Tuning Query Performance

**Scenario**: Optimize query results based on feedback.

```bash
# Get more results per query
python scripts/config_cli.py set --key query_engine.similarity_top_k --value 10

# Larger context chunks
python scripts/config_cli.py set --key query_engine.chunk_size --value 2048

# More overlap for better continuity
python scripts/config_cli.py set --key query_engine.chunk_overlap --value 400

# Verify changes
python scripts/config_cli.py show --key query_engine
```

## 🔐 Security & Best Practices

### 1. Version Control

```bash
# Add to git
git add config/docai_config.json
git commit -m "Update configuration"

# For sensitive data, use environment variables
# Don't commit credentials in config
```

### 2. Backups

```bash
# Config manager auto-creates backups
ls -l config/*.bak
ls -l config/*.backup-*

# Manual backup before major changes
cp config/docai_config.json config/docai_config.json.manual-backup
```

### 3. Validation

```bash
# Always validate after manual edits
python scripts/config_cli.py validate

# Check JSON syntax
python -m json.tool config/docai_config.json
```

### 4. Documentation Sources

```bash
# Use descriptive IDs
✅ python scripts/config_cli.py docs --add react_v18_docs "React 18 Docs" ...
❌ python scripts/config_cli.py docs --add docs1 "Docs" ...

# Add metadata
python scripts/config_cli.py docs --add myproject "My Project" ./path \
  "https://example.com/docs" \
  "Comprehensive project documentation"
```

## 📈 Advanced Usage

### Python API

```python
from src.config_manager import ConfigManager

cm = ConfigManager()

# Get entire config
config = cm.get_all()

# Nested value access
similarity = cm.get('query_engine.similarity_top_k')
port = cm.get('interfaces.web_ui.port')

# Batch updates
cm.set('query_engine.similarity_top_k', 10, save=False)
cm.set('query_engine.chunk_size', 2048, save=False)
cm._save_config()  # Save all at once

# Documentation source lifecycle
cm.add_documentation_source('new_docs', 'New Docs', './path')
cm.mark_source_indexed('new_docs')  # After indexing
cm.enable_documentation_source('new_docs')

# Later...
cm.disable_documentation_source('old_docs')
cm.remove_documentation_source('obsolete_docs')

# Get summary
summary = cm.get_summary()
print(f"Active docs: {summary['documentation_sources']['enabled']}")

# Export
cm.export_to_env('config/production.env')

# Validate
is_valid, errors = cm.validate()
if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Custom Integration

```python
# Example: Custom script that uses config

from src.config_manager import ConfigManager

def main():
    cm = ConfigManager()

    # Get enabled documentation sources
    sources = cm.get_documentation_sources(enabled_only=True)

    # Process each source
    for source in sources:
        if source['indexed']:
            print(f"Processing {source['name']}...")
            # Your processing logic here
        else:
            print(f"Skipping {source['name']} (not indexed)")

    # Update model for heavy processing
    original_model = cm.get_model()
    cm.set_model('qwen2.5:14b-instruct')

    # Do heavy work...

    # Restore original model
    cm.set_model(original_model)

if __name__ == '__main__':
    main()
```

## 🧪 Testing

```bash
# Test configuration system
cd /Users/ashish/Jira/docai

# 1. View current config
python scripts/config_cli.py show

# 2. Validate
python scripts/config_cli.py validate

# 3. Test setting values
python scripts/config_cli.py set --key query_engine.similarity_top_k --value 7
python scripts/config_cli.py show --key query_engine.similarity_top_k

# 4. Test doc management
python scripts/config_cli.py docs --list

# 5. Test export
python scripts/config_cli.py export --output /tmp/test_settings.env
cat /tmp/test_settings.env

# 6. Test Python API
python -c "from src.config_manager import ConfigManager; \
           cm = ConfigManager(); \
           print('Model:', cm.get_model()); \
           print('Mode:', cm.get_execution_mode())"
```

## 📖 Documentation

- **Complete Guide**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- **Quick Reference**: [docs/QUICK_CONFIG_REFERENCE.md](docs/QUICK_CONFIG_REFERENCE.md)
- **Source Code**:
  - [src/config_manager.py](src/config_manager.py)
  - [scripts/config_cli.py](scripts/config_cli.py)

## 🎓 Learning Path

1. **Start Here**: `python scripts/config_cli.py show`
2. **Explore**: `python scripts/config_cli.py` (interactive mode)
3. **Read**: [docs/QUICK_CONFIG_REFERENCE.md](docs/QUICK_CONFIG_REFERENCE.md)
4. **Deep Dive**: [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
5. **Integrate**: Use Python API in your code

## ✅ What This Solves

### Before Master Config

- Settings scattered across multiple files
- No way to track which docs are active
- Manual sync between config files
- No validation
- Difficult to switch between configurations

### After Master Config

✅ All settings in one place
✅ Track and enable/disable documentation sources
✅ Automatic sync with legacy files
✅ Built-in validation
✅ Easy configuration management
✅ Export to any format
✅ Python API and CLI tools
✅ Comprehensive documentation

## 🔮 Future Enhancements

Potential additions (not implemented yet):

- Configuration profiles (dev, staging, prod)
- Configuration import from other formats
- Web-based configuration UI
- Configuration versioning and rollback
- Remote configuration management
- Configuration templates

## 🆘 Support

### Getting Help

```bash
# CLI help
python scripts/config_cli.py --help

# Validate current config
python scripts/config_cli.py validate

# Check system status
./docai.sh  # Option 9 (System Status)
```

### Common Issues

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) → Troubleshooting section.

---

## Summary

You now have a comprehensive master configuration system that:

1. ✅ Centralizes all DocAI configuration
2. ✅ Manages documentation sources with enable/disable
3. ✅ Provides both CLI and Python API
4. ✅ Maintains backward compatibility
5. ✅ Includes validation and safety features
6. ✅ Is fully documented with examples

**Start using it:**

```bash
# Interactive mode (easiest)
python scripts/config_cli.py

# Or quick commands
python scripts/config_cli.py show
python scripts/config_cli.py docs --list
```

Enjoy your new master configuration system! 🎉

# DocAI Master Configuration Guide

The DocAI Master Configuration system provides centralized control over all aspects of the DocAI application, including execution modes, models, documentation sources, and system settings.

## Table of Contents

1. [Overview](#overview)
2. [Configuration File Structure](#configuration-file-structure)
3. [Using the Configuration CLI](#using-the-configuration-cli)
4. [Managing Documentation Sources](#managing-documentation-sources)
5. [Python API](#python-api)
6. [Integration with Shell Script](#integration-with-shell-script)
7. [Configuration Reference](#configuration-reference)

---

## Overview

The master configuration system replaces scattered configuration files with a single source of truth:

- **Location**: `config/docai_config.json`
- **Python Module**: `src/config_manager.py`
- **CLI Tool**: `scripts/config_cli.py`

### Benefits

- **Centralized Control**: All settings in one place
- **Documentation Management**: Track and enable/disable doc sources
- **Validation**: Built-in configuration validation
- **Backward Compatible**: Automatically syncs with legacy `.model_config` and `.exec_mode` files
- **Export**: Generate environment files from master config

---

## Configuration File Structure

The master configuration is organized into logical sections:

```json
{
  "version": "1.0.0",
  "metadata": { ... },
  "execution": {
    "mode": "python",           // python or docker
    "docker_image": "docai:latest"
  },
  "models": {
    "llm": {
      "provider": "ollama",
      "model_name": "llama3.1:8b",
      "host": "http://localhost:11434"
    },
    "embedding": {
      "model_name": "BAAI/bge-small-en-v1.5"
    }
  },
  "documentation": {
    "sources": [
      {
        "id": "xray_cloud",
        "name": "Xray Cloud Documentation",
        "enabled": true,
        "indexed": false,
        "path": "./data/documentation/xray_cloud"
      }
    ]
  },
  "database": { ... },
  "query_engine": { ... },
  "interfaces": { ... },
  "scraper": { ... }
}
```

---

## Using the Configuration CLI

### Quick Start

```bash
# Show configuration summary
python scripts/config_cli.py show

# Interactive mode (menu-driven)
python scripts/config_cli.py
```

### Command Reference

#### 1. View Configuration

```bash
# Show complete summary
python scripts/config_cli.py show

# List documentation sources
python scripts/config_cli.py show --sources

# Get specific value
python scripts/config_cli.py show --key models.llm.model_name
```

#### 2. Modify Settings

```bash
# Set LLM model
python scripts/config_cli.py set --model llama3.1:8b

# Set execution mode
python scripts/config_cli.py set --mode python
python scripts/config_cli.py set --mode docker

# Set any configuration value
python scripts/config_cli.py set --key query_engine.similarity_top_k --value 10
```

#### 3. Manage Documentation Sources

```bash
# List all documentation sources
python scripts/config_cli.py docs --list

# Add new documentation source
python scripts/config_cli.py docs --add \
  myproject \
  "My Project Docs" \
  ./data/documentation/myproject \
  "https://example.com/docs" \
  "Project documentation"

# Enable/disable a source
python scripts/config_cli.py docs --enable xray_cloud
python scripts/config_cli.py docs --disable xray_cloud

# Remove a source
python scripts/config_cli.py docs --remove myproject

# View source details
python scripts/config_cli.py docs --info xray_cloud
```

#### 4. Validation & Export

```bash
# Validate configuration
python scripts/config_cli.py validate

# Export to environment file
python scripts/config_cli.py export
python scripts/config_cli.py export --output custom.env
```

---

## Managing Documentation Sources

Documentation sources are the core of DocAI. The master config tracks all available documentation and which sources are active.

### Source Properties

Each documentation source has:

- **id**: Unique identifier (e.g., `xray_cloud`)
- **name**: Human-readable name
- **path**: Filesystem path to documentation
- **enabled**: Whether this source is active for queries
- **indexed**: Whether this source has been indexed
- **last_indexed**: Timestamp of last indexing
- **source_url**: Original URL (for scraped docs)
- **description**: Description of the documentation
- **tags**: List of tags for categorization
- **priority**: Display/search priority

### Workflow Example

```bash
# 1. Add a new documentation source
python scripts/config_cli.py docs --add \
  react_docs \
  "React Documentation" \
  ./data/documentation/react \
  "https://react.dev" \
  "React framework documentation"

# 2. Scrape the documentation (using docai.sh)
./docai.sh  # Select option 3 to scrape

# 3. Index the documentation (using docai.sh)
./docai.sh  # Select option 4 to index

# The config_manager will automatically mark it as indexed

# 4. Later, if you want to temporarily exclude it from queries
python scripts/config_cli.py docs --disable react_docs

# 5. Re-enable when needed
python scripts/config_cli.py docs --enable react_docs
```

---

## Python API

### Basic Usage

```python
from src.config_manager import ConfigManager

# Initialize
cm = ConfigManager()

# Get values
model = cm.get('models.llm.model_name')
exec_mode = cm.get_execution_mode()

# Set values
cm.set_model('llama3.1:8b')
cm.set_execution_mode('docker')

# Get documentation sources
sources = cm.get_documentation_sources(enabled_only=True)

# Add a documentation source
cm.add_documentation_source(
    source_id='my_docs',
    name='My Documentation',
    path='./data/documentation/my_docs',
    enabled=True
)

# Mark as indexed
cm.mark_source_indexed('my_docs')

# Validate
is_valid, errors = cm.validate()
if not is_valid:
    print("Errors:", errors)
```

### Advanced Usage

```python
# Get entire config
config = cm.get_all()

# Set nested values
cm.set('query_engine.similarity_top_k', 10)
cm.set('interfaces.web_ui.port', 8080)

# Get summary
summary = cm.get_summary()
print(f"Model: {summary['llm_model']}")
print(f"Sources: {summary['documentation_sources']['total']}")

# Export to env file
cm.export_to_env('config/settings.env')

# Update documentation source
cm.update_documentation_source(
    'xray_cloud',
    description='Updated description',
    tags=['xray', 'cloud', 'testing', 'api']
)

# Enable/disable sources
cm.enable_documentation_source('xray_cloud')
cm.disable_documentation_source('old_docs')
```

---

## Integration with Shell Script

The master configuration integrates seamlessly with the existing `docai.sh` script:

### How It Works

1. **Legacy Compatibility**: The config manager automatically reads and syncs with:
   - `.model_config` - Model selection
   - `.exec_mode` - Execution mode

2. **Automatic Updates**: When you use `docai.sh` to:
   - Select a model → Updates master config
   - Choose execution mode → Updates master config
   - Index documentation → Marks source as indexed

3. **Shell Script Integration**:

```bash
# The shell script can read from master config
python -c "from src.config_manager import ConfigManager; \
           cm = ConfigManager(); \
           print(cm.get_model())"

# Or continue using legacy files (automatically synced)
source .model_config
echo $OLLAMA_MODEL
```

### Recommended Workflow

**Option 1: Use docai.sh for everything**
```bash
./docai.sh  # Interactive menus handle config automatically
```

**Option 2: Use config CLI for setup, then docai.sh**
```bash
# Configure using CLI
python scripts/config_cli.py set --model llama3.1:8b
python scripts/config_cli.py set --mode python

# Then use docai.sh for operations
./docai.sh  # Options will reflect your config
```

**Option 3: Pure CLI workflow**
```bash
# Configuration
python scripts/config_cli.py set --model llama3.1:8b

# Add source
python scripts/config_cli.py docs --add my_docs "My Docs" ./data/docs

# Then manually run Python scripts
python src/core/1_index_documents.py
python src/web/3_query_web.py
```

---

## Configuration Reference

### Execution Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `execution.mode` | string | `python` | Execution mode: `python` or `docker` |
| `execution.python_version_required` | string | `3.9` | Minimum Python version |
| `execution.docker_image` | string | `docai:latest` | Docker image name |
| `execution.venv_path` | string | `./venv` | Python virtual environment path |

### Model Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `models.llm.provider` | string | `ollama` | LLM provider |
| `models.llm.model_name` | string | `llama3.1:8b` | Model identifier |
| `models.llm.host` | string | `http://localhost:11434` | Ollama server URL |
| `models.llm.temperature` | float | `0.7` | Sampling temperature |
| `models.llm.max_tokens` | int | `2048` | Maximum response tokens |
| `models.embedding.model_name` | string | `BAAI/bge-small-en-v1.5` | Embedding model |

### Documentation Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `documentation.base_path` | string | `./data/documentation` | Base directory for docs |
| `documentation.sources` | array | `[...]` | List of documentation sources |
| `documentation.auto_index_on_scrape` | bool | `false` | Auto-index after scraping |
| `documentation.watch_for_changes` | bool | `false` | Watch for file changes |

### Query Engine Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `query_engine.similarity_top_k` | int | `5` | Number of relevant chunks to retrieve |
| `query_engine.response_mode` | string | `compact` | Response generation mode |
| `query_engine.chunk_size` | int | `1024` | Document chunk size in chars |
| `query_engine.chunk_overlap` | int | `200` | Overlap between chunks |

### Interface Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `interfaces.web_ui.enabled` | bool | `true` | Enable web UI |
| `interfaces.web_ui.host` | string | `0.0.0.0` | Web UI host |
| `interfaces.web_ui.port` | int | `7860` | Web UI port |
| `interfaces.cli.enabled` | bool | `true` | Enable CLI |
| `interfaces.api.enabled` | bool | `false` | Enable REST API |

### Scraper Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `scraper.delay_seconds` | int | `1` | Delay between requests |
| `scraper.max_depth` | int | `5` | Maximum crawl depth |
| `scraper.timeout_seconds` | int | `30` | Request timeout |
| `scraper.max_pages` | int | `1000` | Maximum pages to scrape |
| `scraper.respect_robots_txt` | bool | `true` | Respect robots.txt |

### Logging Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `logging.level` | string | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `logging.file` | string | `./logs/docai.log` | Log file path |
| `logging.max_size_mb` | int | `10` | Max log file size in MB |
| `logging.console_output` | bool | `true` | Output logs to console |

---

## Troubleshooting

### Configuration File Not Found

```bash
# Check if config file exists
ls -l config/docai_config.json

# If missing, restore from backup or git
git checkout config/docai_config.json
```

### Invalid Configuration

```bash
# Validate configuration
python scripts/config_cli.py validate

# Check JSON syntax
python -m json.tool config/docai_config.json
```

### Legacy Files Out of Sync

The config manager automatically syncs legacy files, but if issues persist:

```bash
# Force sync by reloading
python -c "from src.config_manager import ConfigManager; \
           cm = ConfigManager(); \
           cm.set_model(cm.get_model()); \
           cm.set_execution_mode(cm.get_execution_mode())"
```

### Backup and Restore

The config manager automatically creates backups:

```bash
# Backups are created as config/docai_config.json.bak

# Restore from backup
cp config/docai_config.json.bak config/docai_config.json

# Or from timestamped backup
ls -lt config/*.backup-*
cp config/docai_config.json.backup-20231126-120000 config/docai_config.json
```

---

## Best Practices

1. **Version Control**: Always commit `docai_config.json` to git
2. **Validation**: Run `validate` after manual edits
3. **Backups**: Config manager auto-backs up, but create manual backups before major changes
4. **Documentation Sources**: Use descriptive IDs and names
5. **Testing**: Validate config after adding new sources
6. **Environment Files**: Regenerate with `export` after config changes

---

## Examples

### Complete Setup Example

```bash
# 1. Configure execution
python scripts/config_cli.py set --mode python

# 2. Select model
python scripts/config_cli.py set --model llama3.1:8b

# 3. Add documentation sources
python scripts/config_cli.py docs --add \
  react_docs "React Documentation" ./data/documentation/react

python scripts/config_cli.py docs --add \
  python_docs "Python Documentation" ./data/documentation/python

# 4. Validate
python scripts/config_cli.py validate

# 5. Export for other tools
python scripts/config_cli.py export

# 6. View summary
python scripts/config_cli.py show
```

### Managing Multiple Documentation Sets

```bash
# Add multiple sources
for doc in react vue angular; do
  python scripts/config_cli.py docs --add \
    ${doc}_docs \
    "${doc^} Documentation" \
    ./data/documentation/$doc
done

# Enable only what you need
python scripts/config_cli.py docs --enable react_docs
python scripts/config_cli.py docs --disable vue_docs
python scripts/config_cli.py docs --disable angular_docs

# List active sources
python scripts/config_cli.py show --sources
```

---

## API Reference

See `src/config_manager.py` for complete API documentation.

### ConfigManager Class

```python
class ConfigManager:
    # Core methods
    def get(key_path: str, default=None) -> Any
    def set(key_path: str, value: Any, save=True) -> None
    def get_all() -> Dict

    # Model management
    def get_model() -> str
    def set_model(model_name: str) -> None

    # Execution mode
    def get_execution_mode() -> str
    def set_execution_mode(mode: str) -> None

    # Documentation sources
    def get_documentation_sources(enabled_only=False) -> List[Dict]
    def get_documentation_source(source_id: str) -> Optional[Dict]
    def add_documentation_source(**kwargs) -> None
    def update_documentation_source(source_id: str, **kwargs) -> None
    def remove_documentation_source(source_id: str) -> None
    def enable_documentation_source(source_id: str) -> None
    def disable_documentation_source(source_id: str) -> None
    def mark_source_indexed(source_id: str) -> None

    # Validation & Export
    def validate() -> Tuple[bool, List[str]]
    def export_to_env(output_path: str) -> None
    def get_summary() -> Dict
```

---

## Contributing

When adding new configuration options:

1. Add to `config/docai_config.json` with sensible defaults
2. Update `ConfigManager` class with getters/setters if needed
3. Add validation logic to `validate()` method
4. Update this documentation
5. Add examples to `config_cli.py` if appropriate

---

## Support

For issues or questions:
- Check validation: `python scripts/config_cli.py validate`
- View logs: `./docai.sh` → Option 12
- Report issues: GitHub Issues

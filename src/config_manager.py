#!/usr/bin/env python3
"""
DocAI Configuration Manager
Centralized configuration management for the DocAI system.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from copy import deepcopy


class ConfigManager:
    """Manages the master configuration for DocAI."""

    DEFAULT_CONFIG_PATH = "config/docai_config.json"
    TEMPLATE_CONFIG_PATH = "config/docai_config.json.template"
    LEGACY_MODEL_CONFIG = ".model_config"
    LEGACY_EXEC_MODE = ".exec_mode"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the master config file. Uses default if None.
        """
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_PATH)
        self._ensure_config_exists()
        self.config = self._load_config()
        self._migrate_legacy_configs()

    def _ensure_config_exists(self) -> None:
        """Create config from template if it doesn't exist."""
        if not self.config_path.exists():
            template_path = Path(self.TEMPLATE_CONFIG_PATH)

            if not template_path.exists():
                raise FileNotFoundError(
                    f"Configuration template not found: {template_path}\n"
                    f"Please ensure the template file exists."
                )

            # Create config directory if needed
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy template to config location
            import shutil
            shutil.copy(template_path, self.config_path)

            print(f"✓ Created configuration file from template: {self.config_path}")
            print(f"  You can customize this file for your environment.")

    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    def _save_config(self) -> None:
        """Save the current configuration to file."""
        # Update timestamp
        self.config['last_updated'] = datetime.now().isoformat()

        # Create backup
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix('.json.bak')
            with open(self.config_path, 'r') as f:
                with open(backup_path, 'w') as bf:
                    bf.write(f.read())

        # Save config
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _migrate_legacy_configs(self) -> None:
        """Migrate legacy .model_config and .exec_mode files to master config."""
        updated = False

        # Migrate model config
        model_config_path = Path(self.LEGACY_MODEL_CONFIG)
        if model_config_path.exists():
            with open(model_config_path, 'r') as f:
                content = f.read().strip()
                if content.startswith('OLLAMA_MODEL='):
                    model_name = content.split('=', 1)[1]
                    self.set_model(model_name)
                    updated = True

        # Migrate execution mode
        exec_mode_path = Path(self.LEGACY_EXEC_MODE)
        if exec_mode_path.exists():
            with open(exec_mode_path, 'r') as f:
                mode = f.read().strip()
                self.set_execution_mode(mode)
                updated = True

        if updated:
            self._save_config()

    # ========== Getters ==========

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the config value (e.g., 'models.llm.model_name')
            default: Default value if key doesn't exist

        Returns:
            The configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration."""
        return deepcopy(self.config)

    def get_model(self) -> str:
        """Get the currently selected LLM model."""
        return self.get('models.llm.model_name', 'llama3.1:8b')

    def get_execution_mode(self) -> str:
        """Get the execution mode (python or docker)."""
        return self.get('execution.mode', 'python')

    def get_documentation_sources(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all documentation sources.

        Args:
            enabled_only: If True, return only enabled sources

        Returns:
            List of documentation source configurations
        """
        sources = self.get('documentation.sources', [])
        if enabled_only:
            return [s for s in sources if s.get('enabled', False)]
        return sources

    def get_documentation_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific documentation source by ID."""
        sources = self.get_documentation_sources()
        for source in sources:
            if source.get('id') == source_id:
                return source
        return None

    # ========== Setters ==========

    def set(self, key_path: str, value: Any, save: bool = True) -> None:
        """
        Set a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the config value
            value: The value to set
            save: Whether to save the config immediately
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent dict
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

        if save:
            self._save_config()

    def set_model(self, model_name: str, save: bool = True) -> None:
        """Set the LLM model."""
        self.set('models.llm.model_name', model_name, save=save)

        # Update legacy config for backward compatibility
        with open(self.LEGACY_MODEL_CONFIG, 'w') as f:
            f.write(f"OLLAMA_MODEL={model_name}\n")

    def set_execution_mode(self, mode: str, save: bool = True) -> None:
        """Set the execution mode (python or docker)."""
        if mode not in ['python', 'docker']:
            raise ValueError(f"Invalid execution mode: {mode}. Must be 'python' or 'docker'")

        self.set('execution.mode', mode, save=save)

        # Update legacy config for backward compatibility
        with open(self.LEGACY_EXEC_MODE, 'w') as f:
            f.write(mode)

    # ========== Documentation Source Management ==========

    def add_documentation_source(
        self,
        source_id: str,
        name: str,
        path: str,
        source_url: Optional[str] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        tags: Optional[List[str]] = None,
        save: bool = True
    ) -> None:
        """
        Add a new documentation source.

        Args:
            source_id: Unique identifier for the source
            name: Human-readable name
            path: Path to the documentation files
            source_url: Original URL where docs were scraped from
            description: Description of the documentation
            enabled: Whether this source is enabled
            tags: List of tags for categorization
            save: Whether to save immediately
        """
        sources = self.get_documentation_sources()

        # Check if source already exists
        if any(s['id'] == source_id for s in sources):
            raise ValueError(f"Documentation source with id '{source_id}' already exists")

        new_source = {
            'id': source_id,
            'name': name,
            'path': path,
            'enabled': enabled,
            'indexed': False,
            'last_indexed': None,
            'source_url': source_url,
            'description': description or '',
            'tags': tags or [],
            'priority': len(sources) + 1,
            'metadata': {
                'version': None,
                'language': 'en',
                'format': 'html'
            }
        }

        sources.append(new_source)
        self.set('documentation.sources', sources, save=save)

    def update_documentation_source(
        self,
        source_id: str,
        **kwargs
    ) -> None:
        """
        Update a documentation source.

        Args:
            source_id: ID of the source to update
            **kwargs: Fields to update
        """
        sources = self.get_documentation_sources()

        for i, source in enumerate(sources):
            if source['id'] == source_id:
                # Update allowed fields
                allowed_fields = [
                    'name', 'path', 'enabled', 'indexed', 'last_indexed',
                    'source_url', 'description', 'tags', 'priority', 'metadata'
                ]
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        source[key] = value

                sources[i] = source
                self.set('documentation.sources', sources, save=True)
                return

        raise ValueError(f"Documentation source with id '{source_id}' not found")

    def remove_documentation_source(self, source_id: str, save: bool = True) -> None:
        """Remove a documentation source."""
        sources = self.get_documentation_sources()
        sources = [s for s in sources if s['id'] != source_id]
        self.set('documentation.sources', sources, save=save)

    def enable_documentation_source(self, source_id: str) -> None:
        """Enable a documentation source."""
        self.update_documentation_source(source_id, enabled=True)

    def disable_documentation_source(self, source_id: str) -> None:
        """Disable a documentation source."""
        self.update_documentation_source(source_id, enabled=False)

    def mark_source_indexed(self, source_id: str) -> None:
        """Mark a documentation source as indexed."""
        self.update_documentation_source(
            source_id,
            indexed=True,
            last_indexed=datetime.now().isoformat()
        )

    # ========== Validation ==========

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required sections
        required_sections = ['version', 'execution', 'models', 'documentation', 'database']
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required section: {section}")

        # Validate execution mode
        exec_mode = self.get('execution.mode')
        if exec_mode not in ['python', 'docker']:
            errors.append(f"Invalid execution mode: {exec_mode}")

        # Validate model configuration
        if not self.get('models.llm.model_name'):
            errors.append("LLM model not configured")

        # Validate paths
        paths_to_check = [
            'documentation.base_path',
            'database.path',
        ]
        for path_key in paths_to_check:
            path = self.get(path_key)
            if path and not Path(path).exists():
                errors.append(f"Path does not exist: {path} ({path_key})")

        return (len(errors) == 0, errors)

    # ========== Export/Import ==========

    def export_to_env(self, output_path: str = "config/settings.env") -> None:
        """Export configuration to environment file format."""
        env_lines = [
            "# DocAI Configuration (Auto-generated from docai_config.json)",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "# Ollama Configuration",
            f"OLLAMA_HOST={self.get('models.llm.host')}",
            f"OLLAMA_MODEL={self.get('models.llm.model_name')}",
            "",
            "# ChromaDB Configuration",
            f"CHROMA_DB_PATH={self.get('database.path')}",
            "",
            "# Documentation Paths",
            f"DOCS_BASE_PATH={self.get('documentation.base_path')}",
            "",
            "# Web UI Configuration",
            f"GRADIO_SERVER_NAME={self.get('interfaces.web_ui.host')}",
            f"GRADIO_SERVER_PORT={self.get('interfaces.web_ui.port')}",
            "",
            "# Query Engine Configuration",
            f"SIMILARITY_TOP_K={self.get('query_engine.similarity_top_k')}",
            f"RESPONSE_MODE={self.get('query_engine.response_mode')}",
            "",
            "# Scraper Configuration",
            f"SCRAPER_DELAY={self.get('scraper.delay_seconds')}",
            f"SCRAPER_MAX_DEPTH={self.get('scraper.max_depth')}",
        ]

        with open(output_path, 'w') as f:
            f.write('\n'.join(env_lines))

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            'version': self.get('version'),
            'last_updated': self.get('last_updated'),
            'execution_mode': self.get_execution_mode(),
            'llm_model': self.get_model(),
            'embedding_model': self.get('models.embedding.model_name'),
            'documentation_sources': {
                'total': len(self.get_documentation_sources()),
                'enabled': len(self.get_documentation_sources(enabled_only=True)),
                'indexed': len([s for s in self.get_documentation_sources() if s.get('indexed')])
            },
            'interfaces': {
                'web_ui': self.get('interfaces.web_ui.enabled'),
                'cli': self.get('interfaces.cli.enabled'),
                'api': self.get('interfaces.api.enabled')
            }
        }


# ========== CLI Functions ==========

def print_config_summary(config_manager: ConfigManager) -> None:
    """Print a formatted summary of the configuration."""
    summary = config_manager.get_summary()

    print("=" * 70)
    print("DocAI Configuration Summary")
    print("=" * 70)
    print(f"\nVersion: {summary['version']}")
    print(f"Last Updated: {summary['last_updated'] or 'Never'}")
    print(f"\nExecution Mode: {summary['execution_mode']}")
    print(f"LLM Model: {summary['llm_model']}")
    print(f"Embedding Model: {summary['embedding_model']}")
    print(f"\nDocumentation Sources:")
    print(f"  Total: {summary['documentation_sources']['total']}")
    print(f"  Enabled: {summary['documentation_sources']['enabled']}")
    print(f"  Indexed: {summary['documentation_sources']['indexed']}")
    print(f"\nInterfaces:")
    print(f"  Web UI: {'Enabled' if summary['interfaces']['web_ui'] else 'Disabled'}")
    print(f"  CLI: {'Enabled' if summary['interfaces']['cli'] else 'Disabled'}")
    print(f"  API: {'Enabled' if summary['interfaces']['api'] else 'Disabled'}")
    print("=" * 70)


def print_documentation_sources(config_manager: ConfigManager) -> None:
    """Print all documentation sources."""
    sources = config_manager.get_documentation_sources()

    print("\n" + "=" * 70)
    print("Documentation Sources")
    print("=" * 70)

    if not sources:
        print("\nNo documentation sources configured.")
        return

    for i, source in enumerate(sources, 1):
        status = "✓ ENABLED" if source.get('enabled') else "✗ DISABLED"
        indexed = "✓ INDEXED" if source.get('indexed') else "✗ NOT INDEXED"

        print(f"\n{i}. {source['name']} [{status}] [{indexed}]")
        print(f"   ID: {source['id']}")
        print(f"   Path: {source['path']}")
        if source.get('source_url'):
            print(f"   URL: {source['source_url']}")
        if source.get('description'):
            print(f"   Description: {source['description']}")
        if source.get('tags'):
            print(f"   Tags: {', '.join(source['tags'])}")
        if source.get('last_indexed'):
            print(f"   Last Indexed: {source['last_indexed']}")

    print("=" * 70)


if __name__ == '__main__':
    import sys

    # Simple CLI interface
    if len(sys.argv) < 2:
        print("Usage: python config_manager.py <command> [args]")
        print("\nCommands:")
        print("  summary                    - Show configuration summary")
        print("  sources                    - List documentation sources")
        print("  get <key_path>            - Get a config value")
        print("  set <key_path> <value>    - Set a config value")
        print("  export                     - Export to settings.env")
        print("  validate                   - Validate configuration")
        sys.exit(1)

    try:
        cm = ConfigManager()
        command = sys.argv[1]

        if command == 'summary':
            print_config_summary(cm)

        elif command == 'sources':
            print_documentation_sources(cm)

        elif command == 'get':
            if len(sys.argv) < 3:
                print("Error: Missing key path")
                sys.exit(1)
            value = cm.get(sys.argv[2])
            print(json.dumps(value, indent=2))

        elif command == 'set':
            if len(sys.argv) < 4:
                print("Error: Missing key path or value")
                sys.exit(1)
            key_path = sys.argv[2]
            value = sys.argv[3]
            # Try to parse as JSON, otherwise treat as string
            try:
                value = json.loads(value)
            except:
                pass
            cm.set(key_path, value)
            print(f"✓ Set {key_path} = {value}")

        elif command == 'export':
            output = sys.argv[2] if len(sys.argv) > 2 else "config/settings.env"
            cm.export_to_env(output)
            print(f"✓ Exported configuration to {output}")

        elif command == 'validate':
            is_valid, errors = cm.validate()
            if is_valid:
                print("✓ Configuration is valid")
            else:
                print("✗ Configuration has errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

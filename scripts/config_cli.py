#!/usr/bin/env python3
"""
DocAI Configuration CLI
Interactive command-line interface for managing DocAI configuration.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_manager import ConfigManager, print_config_summary, print_documentation_sources


class Colors:
    """ANSI color codes for terminal output."""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color


def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}{Colors.NC}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.NC}")


def cmd_show(args, cm: ConfigManager):
    """Show configuration information."""
    if args.sources:
        print_documentation_sources(cm)
    elif args.key:
        value = cm.get(args.key)
        if value is None:
            print_error(f"Key not found: {args.key}")
            return 1
        print(json.dumps(value, indent=2))
    else:
        print_config_summary(cm)
    return 0


def cmd_set(args, cm: ConfigManager):
    """Set configuration values."""

    if args.model:
        cm.set_model(args.model)
        print_success(f"Model set to: {args.model}")

    elif args.mode:
        if args.mode not in ['python', 'docker']:
            print_error("Mode must be 'python' or 'docker'")
            return 1
        cm.set_execution_mode(args.mode)
        print_success(f"Execution mode set to: {args.mode}")

    elif args.key and args.value:
        # Try to parse value as JSON
        try:
            value = json.loads(args.value)
        except:
            value = args.value

        cm.set(args.key, value)
        print_success(f"Set {args.key} = {value}")

    else:
        print_error("Please specify what to set (--model, --mode, or --key with --value)")
        return 1

    return 0


def cmd_docs(args, cm: ConfigManager):
    """Manage documentation sources."""

    if args.list:
        print_documentation_sources(cm)

    elif args.add:
        # Parse add arguments: id name path
        if len(args.add) < 3:
            print_error("Usage: --add <id> <name> <path> [url] [description]")
            return 1

        source_id = args.add[0]
        name = args.add[1]
        path = args.add[2]
        url = args.add[3] if len(args.add) > 3 else None
        description = args.add[4] if len(args.add) > 4 else None

        try:
            cm.add_documentation_source(
                source_id=source_id,
                name=name,
                path=path,
                source_url=url,
                description=description
            )
            print_success(f"Added documentation source: {name} ({source_id})")
        except ValueError as e:
            print_error(str(e))
            return 1

    elif args.remove:
        source_id = args.remove
        try:
            cm.remove_documentation_source(source_id)
            print_success(f"Removed documentation source: {source_id}")
        except Exception as e:
            print_error(str(e))
            return 1

    elif args.enable:
        source_id = args.enable
        try:
            cm.enable_documentation_source(source_id)
            print_success(f"Enabled documentation source: {source_id}")
        except Exception as e:
            print_error(str(e))
            return 1

    elif args.disable:
        source_id = args.disable
        try:
            cm.disable_documentation_source(source_id)
            print_success(f"Disabled documentation source: {source_id}")
        except Exception as e:
            print_error(str(e))
            return 1

    elif args.info:
        source_id = args.info
        source = cm.get_documentation_source(source_id)
        if not source:
            print_error(f"Documentation source not found: {source_id}")
            return 1

        print_header(f"Documentation Source: {source['name']}")
        print(f"ID: {source['id']}")
        print(f"Path: {source['path']}")
        print(f"Enabled: {source.get('enabled', False)}")
        print(f"Indexed: {source.get('indexed', False)}")
        if source.get('source_url'):
            print(f"Source URL: {source['source_url']}")
        if source.get('description'):
            print(f"Description: {source['description']}")
        if source.get('tags'):
            print(f"Tags: {', '.join(source['tags'])}")
        if source.get('last_indexed'):
            print(f"Last Indexed: {source['last_indexed']}")
        print()

    else:
        print_documentation_sources(cm)

    return 0


def cmd_validate(args, cm: ConfigManager):
    """Validate configuration."""
    print_header("Configuration Validation")

    is_valid, errors = cm.validate()

    if is_valid:
        print_success("Configuration is valid!")
        return 0
    else:
        print_error("Configuration has errors:")
        for error in errors:
            print(f"  • {error}")
        return 1


def cmd_export(args, cm: ConfigManager):
    """Export configuration."""
    output_path = args.output or "config/settings.env"

    try:
        cm.export_to_env(output_path)
        print_success(f"Exported configuration to: {output_path}")
        return 0
    except Exception as e:
        print_error(f"Export failed: {e}")
        return 1


def cmd_reset(args, cm: ConfigManager):
    """Reset configuration to defaults."""
    if not args.confirm:
        print_warning("This will reset ALL configuration to defaults!")
        response = input("Are you sure? Type 'yes' to confirm: ")
        if response.lower() != 'yes':
            print_info("Reset cancelled.")
            return 0

    # Create backup
    backup_path = f"{cm.config_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    import shutil
    shutil.copy(cm.config_path, backup_path)
    print_info(f"Backup created: {backup_path}")

    # Reset would require loading default config - for now just inform user
    print_warning("Please restore from config/docai_config.json manually or reinstall.")
    return 0


def interactive_menu():
    """Interactive configuration menu."""
    cm = ConfigManager()

    while True:
        print_header("DocAI Configuration Manager")
        print("1. Show Configuration Summary")
        print("2. List Documentation Sources")
        print("3. Set Model")
        print("4. Set Execution Mode")
        print("5. Add Documentation Source")
        print("6. Enable/Disable Documentation Source")
        print("7. Validate Configuration")
        print("8. Export to settings.env")
        print("9. Advanced: Edit Raw Config")
        print("0. Exit")
        print()

        try:
            choice = input(f"{Colors.CYAN}Select option [0-9]: {Colors.NC}").strip()

            if choice == '0':
                print_info("Goodbye!")
                break

            elif choice == '1':
                print_config_summary(cm)

            elif choice == '2':
                print_documentation_sources(cm)

            elif choice == '3':
                print("\nAvailable models:")
                models = cm.get('models.available_models', [])
                for i, model in enumerate(models, 1):
                    print(f"  {i}. {model['name']} ({model['id']}) - {model['ram_requirement_gb']}GB RAM")

                model_choice = input(f"\n{Colors.CYAN}Select model number or enter custom model name: {Colors.NC}").strip()

                try:
                    idx = int(model_choice) - 1
                    if 0 <= idx < len(models):
                        model_id = models[idx]['id']
                        cm.set_model(model_id)
                        print_success(f"Model set to: {model_id}")
                except ValueError:
                    cm.set_model(model_choice)
                    print_success(f"Model set to: {model_choice}")

            elif choice == '4':
                print("\nExecution modes:")
                print("  1. python - Native Python execution")
                print("  2. docker - Docker containerized execution")

                mode_choice = input(f"\n{Colors.CYAN}Select mode [1-2]: {Colors.NC}").strip()
                mode = 'python' if mode_choice == '1' else 'docker'

                cm.set_execution_mode(mode)
                print_success(f"Execution mode set to: {mode}")

            elif choice == '5':
                print_header("Add Documentation Source")
                source_id = input("ID (unique identifier): ").strip()
                name = input("Name: ").strip()
                path = input("Path: ").strip()
                url = input("Source URL (optional): ").strip() or None
                description = input("Description (optional): ").strip() or None

                try:
                    cm.add_documentation_source(
                        source_id=source_id,
                        name=name,
                        path=path,
                        source_url=url,
                        description=description
                    )
                    print_success(f"Added documentation source: {name}")
                except ValueError as e:
                    print_error(str(e))

            elif choice == '6':
                print_documentation_sources(cm)
                source_id = input(f"\n{Colors.CYAN}Enter source ID: {Colors.NC}").strip()
                action = input(f"{Colors.CYAN}Enable or Disable? [e/d]: {Colors.NC}").strip().lower()

                try:
                    if action == 'e':
                        cm.enable_documentation_source(source_id)
                        print_success(f"Enabled: {source_id}")
                    elif action == 'd':
                        cm.disable_documentation_source(source_id)
                        print_success(f"Disabled: {source_id}")
                except Exception as e:
                    print_error(str(e))

            elif choice == '7':
                is_valid, errors = cm.validate()
                if is_valid:
                    print_success("Configuration is valid!")
                else:
                    print_error("Configuration has errors:")
                    for error in errors:
                        print(f"  • {error}")

            elif choice == '8':
                output = input(f"{Colors.CYAN}Output path (default: config/settings.env): {Colors.NC}").strip()
                output = output or "config/settings.env"
                cm.export_to_env(output)
                print_success(f"Exported to: {output}")

            elif choice == '9':
                print_info(f"Config file location: {cm.config_path}")
                print_info("Edit with: nano/vim/code config/docai_config.json")

            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.NC}")

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted. Exiting...{Colors.NC}")
            break
        except Exception as e:
            print_error(f"Error: {e}")
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.NC}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='DocAI Configuration Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show configuration summary
  python config_cli.py show

  # List documentation sources
  python config_cli.py show --sources

  # Get a specific configuration value
  python config_cli.py show --key models.llm.model_name

  # Set the model
  python config_cli.py set --model llama3.1:8b

  # Set execution mode
  python config_cli.py set --mode python

  # Add documentation source
  python config_cli.py docs --add myproject "My Project" ./data/documentation/myproject

  # Enable/disable documentation source
  python config_cli.py docs --enable myproject
  python config_cli.py docs --disable myproject

  # Validate configuration
  python config_cli.py validate

  # Export to environment file
  python config_cli.py export --output config/settings.env

  # Interactive mode
  python config_cli.py
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show configuration')
    show_parser.add_argument('--sources', action='store_true', help='Show documentation sources')
    show_parser.add_argument('--key', help='Get specific configuration value')

    # Set command
    set_parser = subparsers.add_parser('set', help='Set configuration values')
    set_parser.add_argument('--model', help='Set LLM model')
    set_parser.add_argument('--mode', help='Set execution mode (python/docker)')
    set_parser.add_argument('--key', help='Configuration key to set')
    set_parser.add_argument('--value', help='Value to set')

    # Docs command
    docs_parser = subparsers.add_parser('docs', help='Manage documentation sources')
    docs_parser.add_argument('--list', action='store_true', help='List all sources')
    docs_parser.add_argument('--add', nargs='+', help='Add source: id name path [url] [description]')
    docs_parser.add_argument('--remove', help='Remove source by ID')
    docs_parser.add_argument('--enable', help='Enable source by ID')
    docs_parser.add_argument('--disable', help='Disable source by ID')
    docs_parser.add_argument('--info', help='Show source details')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export configuration')
    export_parser.add_argument('--output', help='Output file path')

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset to defaults')
    reset_parser.add_argument('--confirm', action='store_true', help='Skip confirmation')

    args = parser.parse_args()

    # If no command, run interactive mode
    if not args.command:
        interactive_menu()
        return 0

    # Load configuration manager
    try:
        cm = ConfigManager()
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        return 1

    # Execute command
    try:
        if args.command == 'show':
            return cmd_show(args, cm)
        elif args.command == 'set':
            return cmd_set(args, cm)
        elif args.command == 'docs':
            return cmd_docs(args, cm)
        elif args.command == 'validate':
            return cmd_validate(args, cm)
        elif args.command == 'export':
            return cmd_export(args, cm)
        elif args.command == 'reset':
            return cmd_reset(args, cm)
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print_error(f"Command failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

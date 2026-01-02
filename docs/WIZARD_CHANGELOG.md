# Auto Wizard Changelog

**Version**: 2.0
**Last Updated**: 2025-11-26

## Features Added

### Auto-Setup Wizard
- ✅ Intelligent 6-step guided setup
- ✅ OS detection (macOS/Linux/Windows)
- ✅ Auto Ollama installation guidance
- ✅ Auto Ollama server start
- ✅ Model selection with smart download
- ✅ Documentation auto-detection
- ✅ Smart indexing (skip if done)
- ✅ Interface launcher

### Model Selection Enhancements
- ✅ Shows already-downloaded models first
- ✅ Lists recommended models to download
- ✅ Custom model name entry
- ✅ Smart download logic (skip if exists)
- ✅ Dynamic numbering based on available models
- ✅ Fallback to default if invalid

### Execution Improvements
- ✅ Fixed all Python/pip command issues
- ✅ Direct venv execution (no activation)
- ✅ Auto dependency checking
- ✅ Auto dependency installation
- ✅ Robust error handling

### Web UI Enhancements
- ✅ System information panel
- ✅ Model display
- ✅ Ollama status indicator
- ✅ Documentation sources list
- ✅ Embedding model info
- ✅ Expandable accordion (collapsed by default)

### Configuration System
- ✅ Master config file (docai_config.json)
- ✅ Configuration manager Python API
- ✅ Interactive config CLI tool
- ✅ Documentation source management
- ✅ Enable/disable sources
- ✅ Validation and export

### File Organization
- ✅ Clean root directory (only README.md)
- ✅ All docs in docs/ folder
- ✅ Renamed config file to docai_config.json
- ✅ Professional structure

### Documentation
- ✅ Updated README (747 lines)
- ✅ Complete configuration guide
- ✅ Quick reference guide
- ✅ Auto wizard guide
- ✅ Troubleshooting (10+ issues)
- ✅ Real-world examples

## Usage

### Auto Mode (Default)
```bash
./docai.sh
```
- Runs 6-step wizard
- Guides through complete setup
- Launches interface when done

### Manual Mode
```bash
./docai.sh --manual
# or
./docai.sh -m
```
- Shows full 15-option menu
- Advanced control
- All operations available

## Technical Details

### Files Modified
1. `docai.sh` - Added wizard, fixed Python/pip issues (1771 lines)
2. `src/web/3_query_web.py` - Added system info panel
3. Multiple doc files - Updated references

### Files Created
1. `config/docai_config.json` - Master configuration
2. `src/config_manager.py` - Configuration API (713 lines)
3. `scripts/config_cli.py` - Config CLI tool (515 lines)
4. `docs/CONFIGURATION.md` - Config guide
5. `docs/QUICK_CONFIG_REFERENCE.md` - Quick ref
6. `docs/AUTO_WIZARD_GUIDE.md` - Wizard guide
7. `docs/MASTER_CONFIG_GUIDE.md` - Use cases
8. `docs/FILE_REORGANIZATION.md` - File changes
9. `docs/REORGANIZATION_COMPLETE.md` - Summary
10. `docs/WIZARD_CHANGELOG.md` - This file

### Total Lines of Code Added
- Shell script: ~360 lines (wizard)
- Python: ~1,230 lines (config system)
- Documentation: ~4,000 lines
- **Total: ~5,600 lines**

## Benefits

### For New Users
- No technical knowledge required
- Guided setup in minutes
- Smart defaults
- Clear instructions
- Error prevention

### For Experienced Users
- Manual mode for control
- Config CLI for advanced ops
- Python API for scripting
- Documentation source management

### For Everyone
- Robust execution
- Auto dependency management
- Clean organization
- Comprehensive docs
- Professional quality

## Version History

### v2.0 (2025-11-26)
- Added auto-setup wizard
- Enhanced model selection
- Fixed Python/pip issues
- Added system info to Web UI
- Created master config system
- Reorganized files
- Updated all documentation

### v1.0 (Previous)
- Manual menu system
- Basic functionality
- Individual operations

## Migration Guide

### From v1.0 to v2.0

**No breaking changes!** Everything works as before, plus:

**New features available:**
```bash
# Auto wizard (new default)
./docai.sh

# Manual mode (old behavior)
./docai.sh --manual

# Configuration management (new)
python3 scripts/config_cli.py
```

**Legacy files still work:**
- `.model_config` - Auto-synced
- `.exec_mode` - Auto-synced
- All existing scripts - Compatible

**No action required** - Upgrade is transparent!

## Future Roadmap

**Planned enhancements:**
- [ ] Resume wizard from specific step
- [ ] Configuration profiles
- [ ] GPU detection
- [ ] Docker Compose auto-setup
- [ ] Multi-language support
- [ ] Wizard progress bar
- [ ] Setup validation tests
- [ ] Remote config management

## Support

**Documentation:**
- Main guide: `README.md`
- Quick reference: `docs/QUICK_CONFIG_REFERENCE.md`
- Complete guide: `docs/CONFIGURATION.md`
- Wizard guide: `docs/AUTO_WIZARD_GUIDE.md`

**Getting help:**
```bash
./docai.sh --manual
# → Option 15 (Documentation & Guides)

python3 scripts/config_cli.py --help
```

---

**All features tested and working!** 🎉

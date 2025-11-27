#!/bin/bash
###############################################################################
# DocAI - Management Script
#
# This script provides a comprehensive menu system for managing DocAI:
# - Documentation scraping and indexing
# - ML model selection and download
# - Docker or Native Python execution
# - Web UI and CLI interfaces
###############################################################################

set -e

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
CONFIG_DIR="$SCRIPT_DIR/config"
SRC_DIR="$SCRIPT_DIR/src"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"
DATA_DIR="$SCRIPT_DIR/data"
DOCS_DIR="$DATA_DIR/documentation"
CHROMA_DB_DIR="$DATA_DIR/chroma_db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Execution mode (docker or python)
EXEC_MODE=""

###############################################################################
# BANNER
###############################################################################

show_banner() {
    clear
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "           ██████╗  ██████╗  ██████╗ █████╗ ██╗"
    echo "           ██╔══██╗██╔═══██╗██╔════╝██╔══██╗██║"
    echo "           ██║  ██║██║   ██║██║     ███████║██║"
    echo "           ██║  ██║██║   ██║██║     ██╔══██║██║"
    echo "           ██████╔╝╚██████╔╝╚██████╗██║  ██║██║"
    echo "           ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo -e "               ${CYAN}Documentation AI Assistant${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

###############################################################################
# UTILITY FUNCTIONS
###############################################################################

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if Python venv is set up
check_python() {
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        return 0
    else
        return 1
    fi
}

# Check if Python dependencies are installed
check_python_deps() {
    if [ ! -d "venv" ]; then
        return 1
    fi

    # Check for key packages
    if venv/bin/python3 -c "import llama_index" 2>/dev/null && \
       venv/bin/python3 -c "import chromadb" 2>/dev/null && \
       venv/bin/python3 -c "import gradio" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if Ollama is running
check_ollama() {
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Load ML models configuration
load_models_config() {
    if [ -f "$CONFIG_DIR/models.json" ]; then
        cat "$CONFIG_DIR/models.json"
    else
        echo -e "${RED}Error: models.json not found!${NC}"
        exit 1
    fi
}

# Pause and wait for user
pause() {
    echo ""
    read -p "Press Enter to continue..."
}

###############################################################################
# MAIN MENU
###############################################################################

show_main_menu() {
    show_banner

    # Show current execution mode if set
    if [ ! -z "$EXEC_MODE" ]; then
        echo -e "${GREEN}Current Mode: $(echo "$EXEC_MODE" | tr '[:lower:]' '[:upper:]')${NC}"
        echo ""
    fi

    echo -e "${YELLOW}═══ MAIN MENU ═══${NC}"
    echo ""
    echo -e "  ${CYAN}SETUP${NC}"
    echo "    1) Initial Setup (Choose Docker or Python)"
    echo "    2) Select ML Model & Download"
    echo ""
    echo -e "  ${CYAN}DOCUMENTATION${NC}"
    echo "    3) Scrape Documentation (Custom URL)"
    echo "    4) Index Documentation"
    echo "    5) Manage Documentation Folders"
    echo ""
    echo -e "  ${CYAN}QUERY & USE${NC}"
    echo "    6) Launch Web UI"
    echo "    7) Launch CLI Interface"
    echo "    8) Quick Query (One-time)"
    echo ""
    echo -e "  ${CYAN}SYSTEM${NC}"
    echo "    9) Check System Status"
    echo "   10) Start Ollama Server"
    echo "   11) Stop Ollama Server"
    echo "   12) View Logs"
    echo "   13) Restart Services"
    echo "   14) Clean/Reset Data"
    echo ""
    echo -e "  ${CYAN}HELP${NC}"
    echo "   15) Documentation & Guides"
    echo "    0) Exit"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

###############################################################################
# 1. INITIAL SETUP
###############################################################################

menu_initial_setup() {
    show_banner
    echo -e "${YELLOW}═══ INITIAL SETUP ═══${NC}"
    echo ""
    echo "Choose your execution environment:"
    echo ""
    echo "  1) Docker (Recommended for production)"
    echo "     - Isolated environment"
    echo "     - Easy deployment"
    echo "     - No Python setup needed"
    echo ""
    echo "  2) Native Python"
    echo "     - Direct execution"
    echo "     - Easier debugging"
    echo "     - More control"
    echo ""
    echo "  0) Back to main menu"
    echo ""
    read -p "Choose option [0-2]: " choice
    echo ""

    case $choice in
        1)
            setup_docker
            ;;
        2)
            setup_python
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            pause
            ;;
    esac
}

setup_docker() {
    echo -e "${GREEN}Setting up Docker environment...${NC}"
    echo ""

    # Check Docker
    if ! check_docker; then
        echo -e "${RED}Error: Docker not found!${NC}"
        echo ""
        echo "Install Docker:"
        echo "  macOS: brew install --cask docker"
        echo "  Linux: curl -fsSL https://get.docker.com | sh"
        echo "  Or visit: https://docs.docker.com/get-docker/"
        pause
        return 1
    fi

    echo -e "${GREEN}✓ Docker found${NC}"

    # Build Docker image
    echo ""
    echo -e "${BLUE}Building Docker image...${NC}"
    if [ -f "docker/Dockerfile" ]; then
        docker build -f docker/Dockerfile -t docai:latest .
    else
        docker build -t docai:latest .
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Docker image built successfully${NC}"
        EXEC_MODE="docker"
        echo "docker" > .exec_mode
        echo ""
        echo -e "${GREEN}Docker setup complete!${NC}"
    else
        echo -e "${RED}✗ Docker build failed${NC}"
    fi

    pause
}

setup_python() {
    echo -e "${GREEN}Setting up Python environment...${NC}"
    echo ""

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 not found!${NC}"
        echo ""
        echo "Please install Python 3.9 or higher:"
        echo "  macOS: brew install python3"
        echo "  Linux: apt-get install python3 python3-pip python3-venv"
        echo "  Or visit: https://www.python.org/downloads/"
        pause
        return 1
    fi

    echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"

    # Check if venv already exists
    if [ -d "venv" ]; then
        echo -e "${GREEN}✓ Virtual environment already exists${NC}"
        echo ""
        read -p "Do you want to recreate it? (y/n): " confirm

        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo -e "${BLUE}Removing old virtual environment...${NC}"
            rm -rf venv
        else
            # Just install/update dependencies
            echo ""
            echo -e "${BLUE}Updating dependencies...${NC}"

            if [ -f "requirements/base.txt" ]; then
                venv/bin/python3 -m pip install --upgrade pip
                venv/bin/python3 -m pip install -r requirements/base.txt
            elif [ -f "requirements.txt" ]; then
                venv/bin/python3 -m pip install --upgrade pip
                venv/bin/python3 -m pip install -r requirements.txt
            fi

            EXEC_MODE="python"
            echo "python" > .exec_mode
            echo -e "${GREEN}✓ Dependencies updated${NC}"
            pause
            return 0
        fi
    fi

    # Create venv
    echo ""
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv

    # Install dependencies
    echo ""
    echo -e "${BLUE}Installing dependencies...${NC}"

    if [ -f "requirements/base.txt" ]; then
        venv/bin/python3 -m pip install --upgrade pip
        venv/bin/python3 -m pip install -r requirements/base.txt
    elif [ -f "requirements.txt" ]; then
        venv/bin/python3 -m pip install --upgrade pip
        venv/bin/python3 -m pip install -r requirements.txt
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python environment setup successfully${NC}"
        EXEC_MODE="python"
        echo "python" > .exec_mode
        echo ""
        echo -e "${GREEN}Python setup complete!${NC}"
    else
        echo -e "${RED}✗ Python setup failed${NC}"
    fi

    pause
}

###############################################################################
# 2. ML MODEL SELECTION
###############################################################################

menu_select_model() {
    show_banner
    echo -e "${YELLOW}═══ SELECT ML MODEL ═══${NC}"
    echo ""

    # Check if Ollama is installed and running
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}Error: Ollama not installed!${NC}"
        echo ""
        echo "Install Ollama:"
        echo "  macOS: brew install ollama"
        echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh"
        echo "  Or visit: https://ollama.com/download"
        pause
        return 1
    fi

    # Check what models are already downloaded
    echo -e "${CYAN}Checking installed models...${NC}"
    echo ""

    local installed_models=""
    local installed_models_array=()

    # Try to get list of models from running Ollama server
    if check_ollama; then
        installed_models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')
        if [ -n "$installed_models" ]; then
            while IFS= read -r line; do
                [ -n "$line" ] && installed_models_array+=("$line")
            done <<< "$installed_models"
        fi
    else
        # Fallback: Check filesystem for downloaded models if server isn't running
        local ollama_models_dir="$HOME/.ollama/models/manifests/registry.ollama.ai/library"
        if [ -d "$ollama_models_dir" ]; then
            echo -e "${YELLOW}Note: Ollama server not running. Checking filesystem for models...${NC}"
            echo ""

            for model_dir in "$ollama_models_dir"/*; do
                if [ -d "$model_dir" ]; then
                    local model_name=$(basename "$model_dir")
                    # Get the tags/versions for this model
                    for tag_file in "$model_dir"/*; do
                        if [ -f "$tag_file" ]; then
                            local tag=$(basename "$tag_file")
                            installed_models_array+=("${model_name}:${tag}")
                        fi
                    done
                fi
            done
        fi
    fi

    # Show currently configured model
    if [ -f ".model_config" ]; then
        local current_model=$(grep "OLLAMA_MODEL=" .model_config | cut -d'=' -f2)
        echo -e "${GREEN}Current Model: ${current_model}${NC}"
        echo ""
    fi

    # Section 1: Downloaded models on system
    if [ ${#installed_models_array[@]} -gt 0 ]; then
        echo -e "${CYAN}═══ DOWNLOADED MODELS (Ready to Use) ═══${NC}"
        echo ""
        local idx=1
        for model in "${installed_models_array[@]}"; do
            echo -e "  ${idx}) ${GREEN}${model}${NC} [READY]"
            ((idx++))
        done
        echo ""
        local downloaded_count=$((idx-1))
    else
        echo -e "${YELLOW}No models downloaded yet.${NC}"
        echo ""
        local downloaded_count=0
    fi

    # Section 2: Recommended models to download
    echo -e "${CYAN}═══ RECOMMENDED MODELS (Download & Use) ═══${NC}"
    echo ""
    echo "Choose a model based on your system's RAM:"
    echo ""

    local models=("qwen2.5:0.5b" "llama3.2:3b" "llama3.1:8b" "qwen2.5:14b-instruct")
    local descs=("Qwen2.5 0.5B  - ~1GB RAM   (0.5B params)  - Low-end systems" \
                 "Llama 3.2 3B  - ~4GB RAM   (3B params)    - Mid-range systems" \
                 "Llama 3.1 8B  - ~8GB RAM   (8B params)    - High-end systems (Recommended)" \
                 "Qwen2.5 14B   - ~14GB RAM  (14B params)   - Production systems")

    local download_start=$((downloaded_count + 1))
    for i in {0..3}; do
        local model="${models[$i]}"
        local desc="${descs[$i]}"
        local status=""
        local option_num=$((download_start + i))

        if echo "$installed_models" | grep -q "^$model"; then
            status=" ${GREEN}[ALREADY DOWNLOADED]${NC}"
        else
            status=" ${YELLOW}[NEEDS DOWNLOAD]${NC}"
        fi

        echo -e "  ${option_num}) $desc$status"
    done

    echo ""
    echo "  0) Back to main menu"
    echo ""

    local max_option=$((download_start + 3))
    read -p "Choose option [0-${max_option}]: " choice
    echo ""

    # Handle downloaded models selection
    if [ "$choice" -ge 1 ] && [ "$choice" -le "$downloaded_count" ]; then
        local selected_model="${installed_models_array[$((choice-1))]}"
        set_model "$selected_model"
        return
    fi

    # Handle recommended models download/selection
    local download_choice=$((choice - downloaded_count))
    case $download_choice in
        1) download_and_set_model "qwen2.5:0.5b" ;;
        2) download_and_set_model "llama3.2:3b" ;;
        3) download_and_set_model "llama3.1:8b" ;;
        4) download_and_set_model "qwen2.5:14b-instruct" ;;
        0) return ;;
        *)
            if [ "$choice" = "0" ]; then
                return
            else
                echo -e "${RED}Invalid option${NC}"
                pause
            fi
            ;;
    esac
}

set_model() {
    local model_name="$1"

    echo -e "${GREEN}Setting model to: ${model_name}${NC}"
    echo ""

    # Save model choice
    echo "OLLAMA_MODEL=$model_name" > .model_config

    echo -e "${GREEN}✓ Model configured successfully!${NC}"
    echo ""
    echo -e "${CYAN}You can now use this model for querying documentation.${NC}"

    pause
}

download_and_set_model() {
    local model_name="$1"

    echo -e "${GREEN}Selected model: ${model_name}${NC}"
    echo ""

    # Check if Ollama is running
    if ! check_ollama; then
        echo -e "${YELLOW}Ollama is not running.${NC}"
        echo ""
        echo "Please start Ollama in another terminal:"
        echo "  ollama serve"
        echo ""
        read -p "Press Enter once Ollama is running..."

        # Check again
        if ! check_ollama; then
            echo -e "${RED}Ollama still not running. Please start it first.${NC}"
            pause
            return 1
        fi
    fi

    # Check if model is already downloaded
    local installed_models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

    if echo "$installed_models" | grep -q "^$model_name"; then
        echo -e "${GREEN}✓ Model already installed!${NC}"
        echo ""
        read -p "Do you want to update/re-download it? (y/n): " confirm

        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            # Just set it as the active model
            echo "OLLAMA_MODEL=$model_name" > .model_config
            echo -e "${GREEN}Model set to: ${model_name}${NC}"
            pause
            return 0
        fi
    fi

    # Download/update model
    echo ""
    echo -e "${BLUE}Downloading model: ${model_name}${NC}"
    echo -e "${YELLOW}This may take several minutes depending on model size...${NC}"
    echo ""

    ollama pull "$model_name"

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Model downloaded successfully${NC}"

        # Save model choice
        echo "OLLAMA_MODEL=$model_name" > .model_config

        echo ""
        echo -e "${GREEN}Model set to: ${model_name}${NC}"
    else
        echo ""
        echo -e "${RED}✗ Model download failed${NC}"
    fi

    pause
}

###############################################################################
# 3. SCRAPE DOCUMENTATION
###############################################################################

menu_scrape_docs() {
    show_banner
    echo -e "${YELLOW}═══ SCRAPE DOCUMENTATION ═══${NC}"
    echo ""
    echo "This will download documentation from a website and prepare it for indexing."
    echo ""

    # Get documentation name
    read -p "Enter documentation name (e.g., 'xray_cloud'): " doc_name

    if [ -z "$doc_name" ]; then
        echo -e "${RED}Documentation name cannot be empty${NC}"
        pause
        return
    fi

    # Sanitize doc name
    doc_name=$(echo "$doc_name" | tr ' ' '_' | tr -cd '[:alnum:]_-')

    # Get starting URL
    echo ""
    read -p "Enter starting URL: " start_url

    if [ -z "$start_url" ]; then
        echo -e "${RED}URL cannot be empty${NC}"
        pause
        return
    fi

    # Get max depth
    echo ""
    read -p "Enter max crawl depth (default: 5): " max_depth
    max_depth=${max_depth:-5}

    # Create documentation folder
    local doc_folder="$DOCS_DIR/$doc_name"
    mkdir -p "$doc_folder"

    echo ""
    echo -e "${BLUE}Starting documentation scrape...${NC}"
    echo ""
    echo "  Name: $doc_name"
    echo "  URL: $start_url"
    echo "  Depth: $max_depth"
    echo "  Output: $doc_folder"
    echo ""

    # Run scraper
    run_command "python" "scripts/download_xray_docs_resume.py" "--url" "$start_url" "--output" "$doc_folder" "--depth" "$max_depth"

    echo ""
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Documentation scraped successfully${NC}"
        echo -e "${YELLOW}Next step: Index the documentation (option 4)${NC}"
    else
        echo -e "${RED}✗ Scraping failed${NC}"
    fi

    pause
}

###############################################################################
# 4. INDEX DOCUMENTATION
###############################################################################

menu_index_docs() {
    show_banner
    echo -e "${YELLOW}═══ INDEX DOCUMENTATION ═══${NC}"
    echo ""

    # Check if model is configured
    if [ ! -f ".model_config" ]; then
        echo -e "${RED}No model configured!${NC}"
        echo -e "${YELLOW}Please select a model first (option 2)${NC}"
        pause
        return
    fi

    # List available documentation folders
    echo "Available documentation folders:"
    echo ""

    local folders=()
    local i=1

    if [ -d "$DOCS_DIR" ]; then
        for folder in "$DOCS_DIR"/*; do
            if [ -d "$folder" ]; then
                folders+=("$folder")
                echo "  $i) $(basename "$folder")"
                ((i++))
            fi
        done
    fi

    if [ ${#folders[@]} -eq 0 ]; then
        echo -e "${YELLOW}No documentation folders found${NC}"
        echo -e "${YELLOW}Please scrape documentation first (option 3)${NC}"
        pause
        return
    fi

    echo ""
    echo "  0) Back to main menu"
    echo ""
    read -p "Choose folder to index [0-$((i-1))]: " choice

    if [ "$choice" = "0" ]; then
        return
    fi

    if [ "$choice" -ge 1 ] && [ "$choice" -lt "$i" ]; then
        local selected_folder="${folders[$((choice-1))]}"
        echo ""
        echo -e "${BLUE}Indexing: $(basename "$selected_folder")${NC}"
        echo ""

        # Run indexer
        run_command "python" "src/core/1_index_documents.py"

        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓ Documentation indexed successfully${NC}"
            echo -e "${YELLOW}You can now use the Web UI or CLI to query (options 6-7)${NC}"
        else
            echo -e "${RED}✗ Indexing failed${NC}"
        fi
    else
        echo -e "${RED}Invalid option${NC}"
    fi

    pause
}

###############################################################################
# 5. MANAGE DOCUMENTATION FOLDERS
###############################################################################

menu_manage_docs() {
    show_banner
    echo -e "${YELLOW}═══ MANAGE DOCUMENTATION ═══${NC}"
    echo ""

    # List folders
    echo "Documentation folders:"
    echo ""

    if [ -d "$DOCS_DIR" ]; then
        ls -lh "$DOCS_DIR"
    else
        echo -e "${YELLOW}No documentation folder found${NC}"
    fi

    echo ""
    echo "Options:"
    echo "  1) Delete a folder"
    echo "  2) View folder contents"
    echo "  0) Back"
    echo ""
    read -p "Choose option: " choice

    case $choice in
        1)
            read -p "Enter folder name to delete: " folder_name
            if [ -d "$DOCS_DIR/$folder_name" ]; then
                read -p "Are you sure? (yes/no): " confirm
                if [ "$confirm" = "yes" ]; then
                    rm -rf "$DOCS_DIR/$folder_name"
                    echo -e "${GREEN}✓ Folder deleted${NC}"
                fi
            else
                echo -e "${RED}Folder not found${NC}"
            fi
            ;;
        2)
            read -p "Enter folder name: " folder_name
            if [ -d "$DOCS_DIR/$folder_name" ]; then
                ls -lh "$DOCS_DIR/$folder_name" | less
            else
                echo -e "${RED}Folder not found${NC}"
            fi
            ;;
    esac

    pause
}

###############################################################################
# 6. LAUNCH WEB UI
###############################################################################

menu_launch_web() {
    show_banner
    echo -e "${YELLOW}═══ LAUNCH WEB UI ═══${NC}"
    echo ""

    # Check prerequisites
    if [ ! -f ".model_config" ]; then
        echo -e "${RED}No model configured!${NC}"
        echo -e "${YELLOW}Please select a model first (option 2)${NC}"
        pause
        return
    fi

    if [ ! -d "$CHROMA_DB_DIR" ] || [ -z "$(ls -A "$CHROMA_DB_DIR")" ]; then
        echo -e "${RED}No indexed documentation found!${NC}"
        echo -e "${YELLOW}Please index documentation first (option 4)${NC}"
        pause
        return
    fi

    if ! check_ollama; then
        echo -e "${RED}Ollama is not running!${NC}"
        echo ""
        echo "Please start Ollama in another terminal:"
        echo "  ollama serve"
        pause
        return
    fi

    echo -e "${GREEN}Starting Web UI...${NC}"
    echo ""
    echo -e "${CYAN}The UI will be available at: http://localhost:7860${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""

    # Load model config
    source .model_config
    export OLLAMA_MODEL

    # Run web UI
    run_command "python" "src/web/3_query_web.py"

    pause
}

###############################################################################
# 7. LAUNCH CLI
###############################################################################

menu_launch_cli() {
    show_banner
    echo -e "${YELLOW}═══ LAUNCH CLI INTERFACE ═══${NC}"
    echo ""

    # Check prerequisites
    if [ ! -f ".model_config" ]; then
        echo -e "${RED}No model configured!${NC}"
        echo -e "${YELLOW}Please select a model first (option 2)${NC}"
        pause
        return
    fi

    if [ ! -d "$CHROMA_DB_DIR" ] || [ -z "$(ls -A "$CHROMA_DB_DIR")" ]; then
        echo -e "${RED}No indexed documentation found!${NC}"
        echo -e "${YELLOW}Please index documentation first (option 4)${NC}"
        pause
        return
    fi

    if ! check_ollama; then
        echo -e "${RED}Ollama is not running!${NC}"
        echo ""
        echo "Please start Ollama in another terminal:"
        echo "  ollama serve"
        pause
        return
    fi

    echo -e "${GREEN}Starting CLI Interface...${NC}"
    echo ""

    # Load model config
    source .model_config
    export OLLAMA_MODEL

    # Run CLI
    run_command "python" "src/cli/2_query_cli.py"

    pause
}

###############################################################################
# 8. QUICK QUERY
###############################################################################

menu_quick_query() {
    show_banner
    echo -e "${YELLOW}═══ QUICK QUERY ═══${NC}"
    echo ""

    # Check prerequisites
    if [ ! -f ".model_config" ]; then
        echo -e "${RED}No model configured!${NC}"
        pause
        return
    fi

    if [ ! -d "$CHROMA_DB_DIR" ] || [ -z "$(ls -A "$CHROMA_DB_DIR")" ]; then
        echo -e "${RED}No indexed documentation found!${NC}"
        pause
        return
    fi

    if ! check_ollama; then
        echo -e "${RED}Ollama is not running!${NC}"
        pause
        return
    fi

    read -p "Enter your question: " question

    if [ -z "$question" ]; then
        echo -e "${RED}Question cannot be empty${NC}"
        pause
        return
    fi

    echo ""
    echo -e "${BLUE}Searching documentation...${NC}"
    echo ""

    # Load model config
    source .model_config
    export OLLAMA_MODEL

    # Run quick query
    run_command "python" "src/cli/quick_query.py" "$question"

    pause
}

###############################################################################
# 9. SYSTEM STATUS
###############################################################################

menu_system_status() {
    show_banner
    echo -e "${YELLOW}═══ SYSTEM STATUS ═══${NC}"
    echo ""

    # Execution mode
    echo -e "${CYAN}Execution Mode:${NC}"
    if [ -f ".exec_mode" ]; then
        echo "  $(cat .exec_mode | tr '[:lower:]' '[:upper:]')"
    else
        echo "  Not configured"
    fi
    echo ""

    # Docker status
    echo -e "${CYAN}Docker:${NC}"
    if check_docker; then
        echo -e "  ${GREEN}✓ Installed${NC}"
        docker --version
    else
        echo -e "  ${RED}✗ Not found${NC}"
    fi
    echo ""

    # Python status
    echo -e "${CYAN}Python Environment:${NC}"
    if check_python; then
        echo -e "  ${GREEN}✓ Virtual environment exists${NC}"
        venv/bin/python3 --version
    else
        echo -e "  ${RED}✗ Virtual environment not found${NC}"
    fi
    echo ""

    # Ollama status
    echo -e "${CYAN}Ollama Server:${NC}"
    if command -v ollama &> /dev/null; then
        echo -e "  ${GREEN}✓ Installed${NC}"
        echo "  Version: $(ollama --version 2>/dev/null || echo 'Unknown')"
        echo ""
        if check_ollama; then
            echo -e "  ${GREEN}✓ Server Running${NC}"
            echo "  URL: http://localhost:11434"
            echo ""
            echo "  Downloaded Models:"
            ollama list 2>/dev/null | tail -n +2 | sed 's/^/    /' || echo "    No models listed"
        else
            echo -e "  ${YELLOW}⚠ Server Not Running${NC}"
            echo "  Start with: option 10 or 'ollama serve'"
            echo ""
            # Check for models on filesystem even if server not running
            local models_dir="$HOME/.ollama/models/manifests/registry.ollama.ai/library"
            if [ -d "$models_dir" ] && [ -n "$(ls -A "$models_dir" 2>/dev/null)" ]; then
                echo "  Downloaded Models (from filesystem):"
                for model_dir in "$models_dir"/*; do
                    if [ -d "$model_dir" ]; then
                        local model_name=$(basename "$model_dir")
                        for tag_file in "$model_dir"/*; do
                            if [ -f "$tag_file" ]; then
                                local tag=$(basename "$tag_file")
                                echo "    - ${model_name}:${tag}"
                            fi
                        done
                    fi
                done
            else
                echo "  No models found"
            fi
        fi
    else
        echo -e "  ${RED}✗ Not installed${NC}"
    fi
    echo ""

    # Model configuration
    echo -e "${CYAN}ML Model:${NC}"
    if [ -f ".model_config" ]; then
        cat .model_config
    else
        echo "  Not configured"
    fi
    echo ""

    # Documentation folders
    echo -e "${CYAN}Documentation Folders:${NC}"
    if [ -d "$DOCS_DIR" ]; then
        local count=$(find "$DOCS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
        echo "  $count folder(s)"
        ls -1 "$DOCS_DIR" 2>/dev/null | sed 's/^/  - /'
    else
        echo "  None"
    fi
    echo ""

    # ChromaDB status
    echo -e "${CYAN}Vector Database:${NC}"
    if [ -d "$CHROMA_DB_DIR" ] && [ -n "$(ls -A "$CHROMA_DB_DIR" 2>/dev/null)" ]; then
        echo -e "  ${GREEN}✓ Initialized${NC}"
        du -sh "$CHROMA_DB_DIR" 2>/dev/null
    else
        echo "  Not initialized"
    fi
    echo ""

    pause
}

###############################################################################
# 10. START OLLAMA SERVER
###############################################################################

menu_start_ollama() {
    show_banner
    echo -e "${YELLOW}═══ START OLLAMA SERVER ═══${NC}"
    echo ""

    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        echo -e "${RED}Error: Ollama not installed!${NC}"
        echo ""
        echo "Install Ollama:"
        echo "  macOS: brew install ollama"
        echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh"
        pause
        return 1
    fi

    # Check if already running
    if check_ollama; then
        echo -e "${GREEN}✓ Ollama server is already running!${NC}"
        echo ""
        echo "Server URL: http://localhost:11434"
        pause
        return 0
    fi

    echo -e "${BLUE}Starting Ollama server...${NC}"
    echo ""
    echo -e "${YELLOW}The server will run in the background.${NC}"
    echo -e "${YELLOW}You can stop it using option 11 or with: killall ollama${NC}"
    echo ""

    # Start Ollama in background
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    local ollama_pid=$!

    # Wait a moment and check if it started
    sleep 2

    if check_ollama; then
        echo -e "${GREEN}✓ Ollama server started successfully!${NC}"
        echo ""
        echo "  PID: $ollama_pid"
        echo "  URL: http://localhost:11434"
        echo "  Logs: /tmp/ollama.log"
    else
        echo -e "${RED}✗ Failed to start Ollama server${NC}"
        echo ""
        echo "Check logs: tail -f /tmp/ollama.log"
    fi

    pause
}

###############################################################################
# 11. STOP OLLAMA SERVER
###############################################################################

menu_stop_ollama() {
    show_banner
    echo -e "${YELLOW}═══ STOP OLLAMA SERVER ═══${NC}"
    echo ""

    # Check if Ollama is running
    if ! check_ollama; then
        echo -e "${YELLOW}Ollama server is not running.${NC}"
        pause
        return 0
    fi

    echo -e "${BLUE}Stopping Ollama server...${NC}"
    echo ""

    # Stop Ollama
    if killall ollama 2>/dev/null; then
        sleep 1
        if ! check_ollama; then
            echo -e "${GREEN}✓ Ollama server stopped successfully!${NC}"
        else
            echo -e "${YELLOW}⚠ Server may still be running. Try: killall -9 ollama${NC}"
        fi
    else
        echo -e "${RED}✗ Failed to stop Ollama server${NC}"
        echo ""
        echo "Try manually: killall -9 ollama"
    fi

    pause
}

###############################################################################
# 12. VIEW LOGS
###############################################################################

menu_view_logs() {
    show_banner
    echo -e "${YELLOW}═══ VIEW LOGS ═══${NC}"
    echo ""

    echo "Available logs:"
    echo ""
    echo "  1) Application logs"
    echo "  2) Docker logs (if running)"
    echo "  3) Ollama server logs"
    echo "  4) List Ollama log files"
    echo "  0) Back"
    echo ""
    read -p "Choose option: " choice

    case $choice in
        1)
            if [ -f "app.log" ]; then
                tail -f app.log
            else
                echo "No application logs found"
                pause
            fi
            ;;
        2)
            if check_docker && docker ps | grep -q docai; then
                docker logs -f docai
            else
                echo "Docker not running"
                pause
            fi
            ;;
        3)
            if [ -f "/tmp/ollama.log" ]; then
                echo -e "${CYAN}Showing Ollama server logs (Ctrl+C to stop)${NC}"
                echo ""
                tail -f /tmp/ollama.log
            else
                echo "No Ollama server logs found at /tmp/ollama.log"
                echo ""
                echo "If Ollama was started manually, check: ~/.ollama/logs/"
                pause
            fi
            ;;
        4)
            echo -e "${CYAN}Ollama log files:${NC}"
            echo ""
            if [ -d "$HOME/.ollama/logs" ]; then
                ls -lh "$HOME/.ollama/logs/"
            else
                echo "No logs directory found at ~/.ollama/logs/"
            fi
            echo ""
            if [ -f "/tmp/ollama.log" ]; then
                echo "Server log: /tmp/ollama.log"
            fi
            pause
            ;;
    esac
}

###############################################################################
# 13. RESTART SERVICES
###############################################################################

menu_restart_services() {
    show_banner
    echo -e "${YELLOW}═══ RESTART SERVICES ═══${NC}"
    echo ""

    echo "What would you like to restart?"
    echo ""
    echo "  1) Ollama Server"
    echo "  2) Docker containers"
    echo "  3) Both"
    echo "  0) Back"
    echo ""
    read -p "Choose option: " choice

    case $choice in
        1)
            echo -e "${BLUE}Restarting Ollama server...${NC}"
            echo ""

            # Stop Ollama
            if killall ollama 2>/dev/null; then
                echo -e "${GREEN}✓ Ollama stopped${NC}"
                sleep 2
            fi

            # Start Ollama
            nohup ollama serve > /tmp/ollama.log 2>&1 &
            sleep 2

            if check_ollama; then
                echo -e "${GREEN}✓ Ollama server restarted successfully!${NC}"
            else
                echo -e "${RED}✗ Failed to restart Ollama server${NC}"
            fi
            pause
            ;;
        2)
            if check_docker; then
                docker-compose restart
                echo -e "${GREEN}✓ Docker containers restarted${NC}"
            else
                echo -e "${RED}Docker not available${NC}"
            fi
            pause
            ;;
        3)
            echo -e "${BLUE}Restarting all services...${NC}"
            echo ""

            # Restart Ollama
            if killall ollama 2>/dev/null; then
                echo -e "${GREEN}✓ Ollama stopped${NC}"
                sleep 2
            fi

            nohup ollama serve > /tmp/ollama.log 2>&1 &
            sleep 2

            if check_ollama; then
                echo -e "${GREEN}✓ Ollama server restarted${NC}"
            fi

            # Restart Docker
            if check_docker; then
                docker-compose restart
                echo -e "${GREEN}✓ Docker containers restarted${NC}"
            fi

            pause
            ;;
    esac
}

###############################################################################
# 14. CLEAN/RESET DATA
###############################################################################

menu_clean_data() {
    show_banner
    echo -e "${YELLOW}═══ CLEAN/RESET DATA ═══${NC}"
    echo ""
    echo -e "${RED}WARNING: This will delete data!${NC}"
    echo ""
    echo "What would you like to clean?"
    echo ""
    echo "  1) Vector database (ChromaDB) - Requires re-indexing"
    echo "  2) Downloaded documentation"
    echo "  3) All data (database + documentation)"
    echo "  4) Python cache files"
    echo "  0) Back"
    echo ""
    read -p "Choose option: " choice

    case $choice in
        1)
            read -p "Are you sure? This requires re-indexing. (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                rm -rf "$CHROMA_DB_DIR"/*
                echo -e "${GREEN}✓ Vector database cleaned${NC}"
            fi
            ;;
        2)
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                rm -rf "$DOCS_DIR"/*
                echo -e "${GREEN}✓ Documentation cleaned${NC}"
            fi
            ;;
        3)
            read -p "Are you ABSOLUTELY sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                rm -rf "$CHROMA_DB_DIR"/* "$DOCS_DIR"/*
                echo -e "${GREEN}✓ All data cleaned${NC}"
            fi
            ;;
        4)
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
            find . -type f -name "*.pyc" -delete 2>/dev/null
            echo -e "${GREEN}✓ Python cache cleaned${NC}"
            ;;
    esac

    pause
}

###############################################################################
# 15. DOCUMENTATION & GUIDES
###############################################################################

menu_documentation() {
    show_banner
    echo -e "${YELLOW}═══ DOCUMENTATION & GUIDES ═══${NC}"
    echo ""
    echo "Available documentation:"
    echo ""
    echo "  1) Getting Started Guide"
    echo "  2) README"
    echo "  3) API Documentation"
    echo "  4) Troubleshooting"
    echo "  0) Back"
    echo ""
    read -p "Choose option: " choice

    case $choice in
        1)
            if [ -f "docs/GETTING_STARTED.md" ]; then
                less docs/GETTING_STARTED.md
            else
                echo "Getting Started guide not found"
                pause
            fi
            ;;
        2)
            if [ -f "docs/README.md" ]; then
                less docs/README.md
            else
                echo "README not found"
                pause
            fi
            ;;
        3)
            if [ -f "docs/API.md" ]; then
                less docs/API.md
            else
                echo "API documentation not found"
                pause
            fi
            ;;
        4)
            echo -e "${CYAN}Common Issues:${NC}"
            echo ""
            echo "1. Ollama not running:"
            echo "   Run: ollama serve"
            echo ""
            echo "2. Model not found:"
            echo "   Run: ollama pull <model-name>"
            echo ""
            echo "3. Permission denied:"
            echo "   Run: chmod +x docai.sh"
            echo ""
            pause
            ;;
    esac
}

###############################################################################
# COMMAND EXECUTION HELPER
###############################################################################

run_command() {
    local mode="$1"
    shift

    # Load execution mode if not set
    if [ -z "$EXEC_MODE" ] && [ -f ".exec_mode" ]; then
        EXEC_MODE=$(cat .exec_mode)
    fi

    if [ "$EXEC_MODE" = "docker" ]; then
        docker-compose run --rm docai "$@"
    else
        # Python mode - check dependencies first
        if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
            # Ensure pip is available
            if [ ! -f "venv/bin/pip3" ]; then
                echo -e "${YELLOW}⚠ pip not found in venv, reinstalling...${NC}"
                venv/bin/python3 -m ensurepip --upgrade 2>/dev/null || \
                venv/bin/python3 -m pip install --upgrade pip 2>/dev/null
            fi

            # Check if dependencies are installed
            if ! check_python_deps; then
                echo -e "${YELLOW}⚠ Dependencies not fully installed!${NC}"
                echo ""
                echo "Installing dependencies..."
                echo ""

                if [ -f "requirements/base.txt" ]; then
                    venv/bin/python3 -m pip install -q -r requirements/base.txt
                elif [ -f "requirements.txt" ]; then
                    venv/bin/python3 -m pip install -q -r requirements.txt
                fi

                echo -e "${GREEN}✓ Dependencies installed${NC}"
                echo ""
            fi

            # Use venv's python directly
            venv/bin/python3 "$@"
        else
            python3 "$@"
        fi
    fi
}

###############################################################################
# AUTO SETUP WIZARD
###############################################################################

auto_setup_wizard() {
    clear
    show_banner
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}           Welcome to DocAI Auto Setup Wizard!           ${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}This wizard will guide you through the complete setup.${NC}"
    echo ""
    echo "Steps:"
    echo "  1. Choose execution mode (Python or Docker)"
    echo "  2. Install dependencies"
    echo "  3. Setup Ollama and download model"
    echo "  4. Check for documentation"
    echo "  5. Index documentation if needed"
    echo "  6. Launch interface (Web UI or CLI)"
    echo ""
    read -p "Press Enter to begin..."

    # Step 1: Execution Mode
    # Check if already configured
    if [ -f ".exec_mode" ] && [ -s ".exec_mode" ]; then
        EXEC_MODE=$(cat .exec_mode | tr -d '[:space:]')

        clear
        show_banner
        echo -e "${CYAN}Step 1/6: Check Execution Mode${NC}"
        echo ""
        echo -e "${GREEN}✓ Execution mode already configured: ${EXEC_MODE}${NC}"
        echo ""

        # Verify the setup is still valid
        if [ "$EXEC_MODE" = "python" ]; then
            if ! check_python; then
                echo -e "${YELLOW}⚠ Python environment not found, reconfiguring...${NC}"
                echo ""
                setup_python
            else
                echo -e "${GREEN}✓ Python environment ready${NC}"
            fi
        elif [ "$EXEC_MODE" = "docker" ]; then
            if ! check_docker; then
                echo -e "${YELLOW}⚠ Docker not found, reconfiguring...${NC}"
                echo ""
                setup_docker
            else
                echo -e "${GREEN}✓ Docker environment ready${NC}"
            fi
        fi

        echo ""
        read -p "Press Enter to continue..."
    else
        # No existing config, ask user
        clear
        show_banner
        echo -e "${CYAN}Step 1/6: Choose Execution Mode${NC}"
        echo ""
        echo "How would you like to run DocAI?"
        echo ""
        echo "  1) Python (Recommended)"
        echo "     - Direct execution"
        echo "     - Easier to debug"
        echo "     - Works on Mac, Linux, Windows (Git Bash/WSL)"
        echo ""
        echo "  2) Docker"
        echo "     - Isolated environment"
        echo "     - Easy deployment"
        echo "     - Requires Docker installed"
        echo ""
        read -p "Choose [1-2]: " exec_choice
        echo ""

        if [ "$exec_choice" = "2" ]; then
            echo -e "${BLUE}Setting up Docker mode...${NC}"
            setup_docker
            EXEC_MODE="docker"
        else
            echo -e "${BLUE}Setting up Python mode...${NC}"
            setup_python
            EXEC_MODE="python"
        fi

        echo ""
        read -p "Press Enter to continue..."
    fi

    # Step 2: Ollama Check
    clear
    show_banner
    echo -e "${CYAN}Step 2/6: Check Ollama${NC}"
    echo ""

    if ! command -v ollama &> /dev/null; then
        echo -e "${YELLOW}Ollama is not installed!${NC}"
        echo ""
        echo "Ollama is required to run the AI models locally."
        echo ""
        echo "Installation instructions:"
        echo ""

        # Detect OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "  ${CYAN}macOS:${NC}"
            echo "    brew install ollama"
            echo "    or download from: https://ollama.com/download"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "  ${CYAN}Linux:${NC}"
            echo "    curl -fsSL https://ollama.com/install.sh | sh"
        else
            echo "  ${CYAN}Windows:${NC}"
            echo "    Download from: https://ollama.com/download"
        fi

        echo ""
        read -p "Press Enter after installing Ollama..."

        # Check again
        if ! command -v ollama &> /dev/null; then
            echo -e "${RED}Ollama still not found. Please install it and run this script again.${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}✓ Ollama is installed${NC}"
    echo ""

    # Check if Ollama is running
    if ! check_ollama; then
        echo -e "${YELLOW}Ollama server is not running${NC}"
        echo ""
        echo "Starting Ollama server..."
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3

        if check_ollama; then
            echo -e "${GREEN}✓ Ollama server started${NC}"
        else
            echo -e "${YELLOW}⚠ Couldn't start Ollama automatically${NC}"
            echo ""
            echo "Please start Ollama manually in another terminal:"
            echo "  ollama serve"
            echo ""
            read -p "Press Enter when Ollama is running..."
        fi
    else
        echo -e "${GREEN}✓ Ollama server is running${NC}"
    fi

    echo ""
    read -p "Press Enter to continue..."

    # Step 3: Select Model
    # Check if model already configured
    if [ -f ".model_config" ] && [ -s ".model_config" ]; then
        local configured_model=$(grep "OLLAMA_MODEL=" .model_config | cut -d'=' -f2 | tr -d '[:space:]')

        clear
        show_banner
        echo -e "${CYAN}Step 3/6: Check AI Model${NC}"
        echo ""
        echo -e "${GREEN}✓ Model already configured: ${configured_model}${NC}"
        echo ""

        # Verify the model is available
        if check_ollama; then
            if ollama list 2>/dev/null | grep -q "^$configured_model"; then
                echo -e "${GREEN}✓ Model is downloaded and ready${NC}"
                echo ""
                selected_model="$configured_model"
                read -p "Press Enter to continue..."
            else
                echo -e "${YELLOW}⚠ Model not found locally, downloading...${NC}"
                echo ""
                ollama pull "$configured_model"
                if [ $? -eq 0 ]; then
                    echo ""
                    echo -e "${GREEN}✓ Model downloaded successfully${NC}"
                    selected_model="$configured_model"
                else
                    echo ""
                    echo -e "${RED}✗ Model download failed${NC}"
                    echo -e "${YELLOW}Please select a different model...${NC}"
                    echo ""
                    read -p "Press Enter to continue..."
                    # Fall through to model selection below
                fi
            fi
        else
            echo -e "${YELLOW}⚠ Ollama not running, cannot verify model${NC}"
            echo ""
            selected_model="$configured_model"
            read -p "Press Enter to continue..."
        fi
    fi

    # Only show model selection if not already configured or if there was an issue
    if [ -z "$selected_model" ]; then
        clear
        show_banner
        echo -e "${CYAN}Step 3/6: Select AI Model${NC}"
        echo ""

        # Get list of downloaded models
        local downloaded_models=()
        local downloaded_count=0

        if check_ollama; then
            echo -e "${BLUE}Checking downloaded models...${NC}"
            echo ""

            local model_list=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')
            if [ -n "$model_list" ]; then
                while IFS= read -r line; do
                    if [ -n "$line" ]; then
                        downloaded_models+=("$line")
                        ((downloaded_count++))
                    fi
                done <<< "$model_list"
            fi
        fi

    # Show downloaded models first
    local option_num=1
    if [ ${#downloaded_models[@]} -gt 0 ]; then
        echo -e "${GREEN}═══ DOWNLOADED MODELS (Ready to Use) ═══${NC}"
        echo ""
        for model in "${downloaded_models[@]}"; do
            echo -e "  ${option_num}) ${GREEN}${model}${NC} [READY]"
            ((option_num++))
        done
        echo ""
    fi

    # Show recommended models to download
    echo -e "${CYAN}═══ RECOMMENDED MODELS (Download if Needed) ═══${NC}"
    echo ""
    echo "Choose a model based on your system's RAM:"
    echo ""

    local rec_start=$option_num
    echo -e "  ${option_num}) Qwen2.5 0.5B  - ~1GB RAM  (fastest, basic quality)"
    ((option_num++))
    echo -e "  ${option_num}) Llama 3.2 3B  - ~4GB RAM  (balanced)"
    ((option_num++))
    echo -e "  ${option_num}) Llama 3.1 8B  - ~8GB RAM  (recommended, best quality)"
    ((option_num++))
    echo -e "  ${option_num}) Qwen2.5 14B   - ~14GB RAM (production, highest quality)"
    ((option_num++))
    echo ""
    echo -e "  ${option_num}) ${MAGENTA}Enter custom model name${NC}"
    echo ""

    local max_option=$option_num
    read -p "Choose model [1-${max_option}]: " model_choice
    echo ""

    # Handle selection
    selected_model=""

    # Check if selecting a downloaded model
    if [ "$model_choice" -ge 1 ] && [ "$model_choice" -le "$downloaded_count" ]; then
        selected_model="${downloaded_models[$((model_choice-1))]}"
        echo -e "${GREEN}Using downloaded model: ${selected_model}${NC}"
        echo ""

    # Check if selecting recommended models
    elif [ "$model_choice" -eq "$rec_start" ]; then
        selected_model="qwen2.5:0.5b"
    elif [ "$model_choice" -eq "$((rec_start+1))" ]; then
        selected_model="llama3.2:3b"
    elif [ "$model_choice" -eq "$((rec_start+2))" ]; then
        selected_model="llama3.1:8b"
    elif [ "$model_choice" -eq "$((rec_start+3))" ]; then
        selected_model="qwen2.5:14b-instruct"

    # Custom model
    elif [ "$model_choice" -eq "$max_option" ]; then
        echo -e "${CYAN}Enter custom model name${NC}"
        echo "(e.g., mistral:7b, codellama:13b, phi:2.7b)"
        echo ""
        read -p "Model name: " custom_model

        if [ -z "$custom_model" ]; then
            echo -e "${YELLOW}No model entered, using default: llama3.1:8b${NC}"
            selected_model="llama3.1:8b"
        else
            selected_model="$custom_model"
        fi
        echo ""

    # Invalid choice - use default
    else
        echo -e "${YELLOW}Invalid choice, using default: llama3.1:8b${NC}"
        selected_model="llama3.1:8b"
        echo ""
    fi

        echo -e "${BLUE}Selected model: ${selected_model}${NC}"
        echo ""

        # Check if model exists (for non-downloaded selections)
        if [ "$model_choice" -le "$downloaded_count" ]; then
            # Already downloaded, skip download check
            echo -e "${GREEN}✓ Model ready to use${NC}"
        else
            # Check if this recommended/custom model is downloaded
            if ! ollama list 2>/dev/null | grep -q "^$selected_model"; then
                echo -e "${YELLOW}Model not found locally, downloading...${NC}"
                echo "This may take several minutes depending on model size."
                echo ""
                ollama pull "$selected_model"

                if [ $? -eq 0 ]; then
                    echo ""
                    echo -e "${GREEN}✓ Model downloaded successfully${NC}"
                else
                    echo ""
                    echo -e "${RED}✗ Model download failed${NC}"
                    echo -e "${YELLOW}You can download manually later: ollama pull ${selected_model}${NC}"
                fi
            else
                echo -e "${GREEN}✓ Model already downloaded${NC}"
            fi
        fi
    fi  # End of "if [ -z "$selected_model" ]" block

    # Save model config (runs whether model was already configured or newly selected)
    echo "OLLAMA_MODEL=$selected_model" > .model_config

    # Update master config
    if command -v python3 &> /dev/null && [ -f "venv/bin/python3" ]; then
        venv/bin/python3 scripts/config_cli.py set --model "$selected_model" 2>/dev/null || true
    fi

    echo ""
    read -p "Press Enter to continue..."

    # Step 4: Check Documentation
    clear
    show_banner
    echo -e "${CYAN}Step 4/6: Check Documentation${NC}"
    echo ""

    # Count documentation folders
    doc_count=0
    if [ -d "$DOCS_DIR" ]; then
        doc_count=$(find "$DOCS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
    fi

    if [ "$doc_count" -gt 0 ]; then
        echo -e "${GREEN}✓ Found $doc_count documentation folder(s)${NC}"
        echo ""
        echo "Available documentation:"
        ls -1 "$DOCS_DIR" 2>/dev/null | sed 's/^/  - /'
        echo ""
    else
        echo -e "${YELLOW}No documentation found${NC}"
        echo ""
        echo "You can add documentation later using:"
        echo "  - Option 3: Scrape Documentation (from URL)"
        echo "  - Or manually place docs in: $DOCS_DIR"
        echo ""
        read -p "Continue without documentation? [y/n]: " skip_docs

        if [ "$skip_docs" != "y" ] && [ "$skip_docs" != "Y" ]; then
            echo ""
            echo "Please add documentation and run this wizard again."
            exit 0
        fi
    fi

    echo ""
    read -p "Press Enter to continue..."

    # Step 5: Index Documentation
    if [ "$doc_count" -gt 0 ]; then
        clear
        show_banner
        echo -e "${CYAN}Step 5/6: Index Documentation${NC}"
        echo ""

        # Check if ChromaDB exists and has data
        if [ -d "$CHROMA_DB_DIR" ] && [ -n "$(ls -A "$CHROMA_DB_DIR" 2>/dev/null)" ]; then
            echo -e "${GREEN}✓ Documentation index already exists${NC}"
            echo ""
            read -p "Re-index documentation? [y/n]: " reindex

            if [ "$reindex" = "y" ] || [ "$reindex" = "Y" ]; then
                echo ""
                echo -e "${BLUE}Indexing documentation...${NC}"
                echo ""
                run_command "python" "src/core/1_index_documents.py"
                echo ""
                echo -e "${GREEN}✓ Documentation indexed${NC}"
            fi
        else
            echo -e "${YELLOW}Documentation needs to be indexed${NC}"
            echo ""
            echo "This creates a searchable database from your documentation."
            echo "It only needs to be done once (takes 2-5 minutes)."
            echo ""
            read -p "Index documentation now? [y/n]: " do_index

            if [ "$do_index" = "y" ] || [ "$do_index" = "Y" ]; then
                echo ""
                echo -e "${BLUE}Indexing documentation...${NC}"
                echo ""
                run_command "python" "src/core/1_index_documents.py"
                echo ""
                echo -e "${GREEN}✓ Documentation indexed${NC}"
            else
                echo ""
                echo -e "${YELLOW}⚠ Skipping indexing. You can index later with Option 4.${NC}"
            fi
        fi

        echo ""
        read -p "Press Enter to continue..."
    fi

    # Step 6: Launch Interface
    clear
    show_banner
    echo -e "${CYAN}Step 6/6: Launch Interface${NC}"
    echo ""
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "How would you like to use DocAI?"
    echo ""
    echo "  1) Web UI (Recommended)"
    echo "     - Beautiful graphical interface"
    echo "     - Opens in your browser"
    echo "     - Best for extended use"
    echo ""
    echo "  2) CLI"
    echo "     - Terminal-based interface"
    echo "     - Interactive chat"
    echo "     - Good for quick queries"
    echo ""
    echo "  3) Exit (launch manually later)"
    echo ""
    read -p "Choose [1-3]: " launch_choice
    echo ""

    case $launch_choice in
        1)
            echo -e "${BLUE}Launching Web UI...${NC}"
            echo ""
            echo -e "${CYAN}The UI will open at: http://localhost:7860${NC}"
            echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
            echo ""
            sleep 2
            menu_launch_web
            ;;
        2)
            echo -e "${BLUE}Launching CLI...${NC}"
            echo ""
            sleep 1
            menu_launch_cli
            ;;
        3)
            echo -e "${GREEN}Setup complete!${NC}"
            echo ""
            echo "To use DocAI later, run:"
            echo "  ./docai.sh --manual"
            echo ""
            echo "Or run in auto mode:"
            echo "  ./docai.sh"
            echo ""
            exit 0
            ;;
    esac
}

###############################################################################
# MAIN LOOP (MANUAL MODE)
###############################################################################

manual_mode() {
    while true; do
        show_main_menu
        read -p "Choose option [0-15]: " choice
        echo ""

        case $choice in
            1) menu_initial_setup ;;
            2) menu_select_model ;;
            3) menu_scrape_docs ;;
            4) menu_index_docs ;;
            5) menu_manage_docs ;;
            6) menu_launch_web ;;
            7) menu_launch_cli ;;
            8) menu_quick_query ;;
            9) menu_system_status ;;
            10) menu_start_ollama ;;
            11) menu_stop_ollama ;;
            12) menu_view_logs ;;
            13) menu_restart_services ;;
            14) menu_clean_data ;;
            15) menu_documentation ;;
            0)
                show_banner
                echo -e "${GREEN}Thank you for using DocAI!${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please choose 0-15.${NC}"
                pause
                ;;
        esac
    done
}

###############################################################################
# MAIN
###############################################################################

main() {
    # Create necessary directories
    mkdir -p "$DATA_DIR" "$DOCS_DIR" "$CHROMA_DB_DIR"

    # Load execution mode if exists
    if [ -f ".exec_mode" ]; then
        EXEC_MODE=$(cat .exec_mode)
    fi

    # Check for --manual flag
    if [ "$1" = "--manual" ] || [ "$1" = "-m" ]; then
        manual_mode
    else
        # Auto mode
        auto_setup_wizard
    fi
}

# Run main with arguments
main "$@"

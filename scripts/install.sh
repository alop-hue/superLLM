#!/bin/sh
# ============================================================
# superLLM - Install Script
# Usage: curl -fsSL https://superllm.dev/install.sh | sh
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

REPO="superllm/superllm"
INSTALL_DIR="${SUPERLLM_DIR:-$HOME/.superllm}"
BIN_DIR="$HOME/.local/bin"

# --- Utility functions ---
info()  { printf "${BLUE}%s${NC}\n" "$*"; }
ok()    { printf "${GREEN}✓${NC} %s\n" "$*"; }
warn()  { printf "${YELLOW}⚠${NC} %s\n" "$*"; }
error() { printf "${RED}✗${NC} %s\n" "$*"; exit 1; }

# --- Header ---
echo ""
printf "${CYAN}
   _____ _____  _   ___  __  __ _     _ 
  / ____|  __ \| \ | \ \/ / |  \ \   / /
 | (___ | |__) |  \| |\  /| |   \ \_/ / 
  \___ \|  ___/| . \` |/  \| |    \   /  
  ____) | |    | |\  / /\ \ |____| |   
 |_____/|_|    |_| \_/_/  \_\_____/|_|   
                                         
${NC}"
echo "superLLM - Local-first and cloud-capable AI platform"
echo "===================================================="
echo ""

# --- OS Detection ---
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)   PLATFORM="linux" ;;
    Darwin)  PLATFORM="darwin" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)       error "Unsupported OS: $OS (only Linux, macOS, and Windows are supported)" ;;
esac

info "Detected: $PLATFORM ($ARCH)"
ok "Platform: $PLATFORM"
ok "Architecture: $ARCH"

# --- Python Check ---
info ""
info "Checking Python..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    error "Python not found! Please install Python 3.10 or later."
fi

PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    error "Python 3.10+ required (found $PY_VERSION)"
fi

ok "Python $PY_VERSION found at $(command -v $PYTHON)"

# --- Pip Check ---
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    info "Installing pip..."
    $PYTHON -m ensurepip --upgrade 2>/dev/null || \
        curl -fsSL https://bootstrap.pypa.io/get-pip.py | $PYTHON
fi
ok "pip is ready"

# --- Install superLLM ---
info ""
info "Installing superLLM..."

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Install from GitHub via pip
info "This may take a minute..."

# Try to install in a virtual environment first, fallback to user install
if $PYTHON -m venv "$INSTALL_DIR/venv" 2>/dev/null; then
    info "Creating isolated environment..."
    "$INSTALL_DIR/venv/bin/pip" install --quiet --upgrade pip 2>/dev/null || true
    "$INSTALL_DIR/venv/bin/pip" install --quiet "superllm[all]" 2>/dev/null || \
    "$INSTALL_DIR/venv/bin/pip" install --quiet superllm 2>/dev/null || {
        warn "PyPI package not found. Installing from GitHub..."
        "$INSTALL_DIR/venv/bin/pip" install --quiet "git+https://github.com/$REPO.git" 2>/dev/null || \
        error "Installation failed. Try: pip install superllm"
    }
    
    # Create wrapper script
    cat > "$BIN_DIR/superllm" << 'SCRIPT'
#!/bin/sh
export SUPERLLM_DATA_DIR="${SUPERLLM_DATA_DIR:-$HOME/.superllm}"
exec "$HOME/.superllm/venv/bin/superllm" "$@"
SCRIPT
    chmod +x "$BIN_DIR/superllm"
    SUPERLLM_CMD="$BIN_DIR/superllm"
else
    warn "Virtual environment creation failed, installing globally..."
    $PYTHON -m pip install --quiet --user "superllm[all]" 2>/dev/null || \
    $PYTHON -m pip install --quiet --user superllm 2>/dev/null || {
        warn "PyPI not available, installing from GitHub..."
        $PYTHON -m pip install --quiet --user "git+https://github.com/$REPO.git" 2>/dev/null || \
        error "Installation failed. Try: pip install superllm"
    }
    SUPERLLM_CMD="$PYTHON -m superllm"
fi

ok "superLLM installed!"

# --- Initialize ---
info ""
info "Initializing superLLM..."
$SUPERLLM_CMD init 2>/dev/null || true
ok "Configuration initialized at $INSTALL_DIR"

# --- Shell Completion ---
info ""
info "Setting up shell completion..."
SHELL_NAME=$(basename "${SHELL:-$0}")
case "$SHELL_NAME" in
    zsh)  COMP_FILE="$HOME/.zshrc";;
    bash) COMP_FILE="$HOME/.bashrc";;
    fish) COMP_FILE="$HOME/.config/fish/config.fish";;
    *)    COMP_FILE="";;
esac

if [ -n "$COMP_FILE" ]; then
    if ! grep -q "superllm" "$COMP_FILE" 2>/dev/null; then
        echo "" >> "$COMP_FILE"
        echo "# superLLM completion (added by installer)" >> "$COMP_FILE"
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$COMP_FILE"
        ok "Added superLLM to PATH in $COMP_FILE"
    fi
fi

# --- Print instructions ---
echo ""
printf "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}\n"
printf "${GREEN}║              superLLM installed successfully!               ║${NC}\n"
printf "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}\n"
echo ""
echo "  ${CYAN}Commands:${NC}"
echo "    superllm start       Start the server"
echo "    superllm pull <m>    Download a model"
echo "    superllm list        List installed models"
echo "    superllm chat        Start interactive chat"
echo "    superllm status      Show server status"
echo ""
echo "  ${CYAN}Quick start:${NC}"
echo "    superllm start &              # Start in background"
echo "    superllm pull llama-3.2-1b    # Download a tiny model"
echo "    curl http://localhost:8080     # API is live"
echo ""
echo "  ${CYAN}Web UI:${NC}"
echo "    Open http://localhost:8080 in your browser"
echo ""
echo "  ${CYAN}Documentation:${NC}"
echo "    https://github.com/$REPO"
echo ""

# --- Add to PATH warning ---
case ":${PATH}:" in
    *:"$BIN_DIR":*) ;;
    *) warn "Add $BIN_DIR to your PATH: export PATH=\"\$PATH:$BIN_DIR\"" ;;
esac

# --- Install local deps hint ---
info ""
info "Optional dependencies:"
echo "  For local inference:  superllm install --local"
echo "  For cloud inference:  superllm install --cloud"
echo ""

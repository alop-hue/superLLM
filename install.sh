#!/bin/sh
set -eu

REPO="alop-hue/superLLM"
APP="superllm"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { printf "${CYAN}::${NC} %s\n" "$1"; }
ok()    { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
fail()  { printf "${RED}✗${NC} %s\n" "$1"; exit 1; }

# --- detect OS ---
OS="$(uname -s)"
case "$OS" in
  Linux)  OS="linux"   ;;
  Darwin) OS="macos"   ;;
  *)      fail "Unsupported OS: $OS. Linux, macOS, and Windows WSL are supported." ;;
esac

ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64) ARCH="x86_64" ;;
  aarch64|arm64) ARCH="arm64"  ;;
  *) warn "Architecture '$ARCH' not well-tested, proceeding anyway..." ;;
esac

info "Detected: $OS ($ARCH)"
info "Installing $APP..."

# --- check Python ---
PYTHON=""
for cmd in python3 python; do
  if command -v "$cmd" >/dev/null 2>&1; then
    VER="$($cmd --version 2>&1 | cut -d' ' -f2 | cut -d. -f1)"
    if [ "$VER" -ge 3 ] 2>/dev/null; then
      PYTHON="$cmd"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  fail "Python 3 not found. Install Python >= 3.10 from https://python.org"
fi

PY_VER="$($PYTHON --version 2>&1 | cut -d' ' -f2 | cut -d. -f1,2)"
info "Python $PY_VER found: $PYTHON"

MINOR="${PY_VER#*.}"
if [ "$MINOR" -lt 10 ] 2>/dev/null; then
  fail "Python >= 3.10 required (found $PY_VER)"
fi

# --- check pip ---
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
  fail "pip not found. Install pip: $PYTHON -m ensurepip --upgrade"
fi

# --- detect externally-managed-environment (PEP 668) ---
VENV_DIR=""
PY_MARKER="/usr/lib/python${PY_VER}/EXTERNALLY-MANAGED"
if [ -f "$PY_MARKER" ]; then
  warn "System pip is restricted (PEP 668). Creating a virtual environment..."
  VENV_DIR="$HOME/.local/share/$APP-venv"
  if [ ! -d "$VENV_DIR" ]; then
    $PYTHON -m venv "$VENV_DIR"
  fi
  PYTHON="$VENV_DIR/bin/python"
  info "Using virtual environment: $VENV_DIR"
fi

# --- install ---
info "Installing $APP from GitHub..."
$PYTHON -m pip install --upgrade pip -q

TMP="$(mktemp -d)"
info "Downloading $APP..."
git clone --depth 1 "https://github.com/$REPO.git" "$TMP/$APP" 2>&1

cd "$TMP/$APP"

if $PYTHON -m pip install -e ".[all]" 2>&1; then
  ok "Installed $APP with all features (local + cloud + audio)"
else
  warn "llama-cpp-python build failed (needs gcc/cmake). Installing without local inference..."
  $PYTHON -m pip install -e ".[cloud,audio,tts,embeddings,agents]" 2>&1 || \
    $PYTHON -m pip install -e "." 2>&1
  warn "To enable local models, install build tools and run: pip install 'superllm[local]'"
fi

cd "$OLDPWD"
rm -rf "$TMP"
ok "Installed $APP"

# --- add venv to PATH if used ---
if [ -n "$VENV_DIR" ]; then
  USER_BIN="$VENV_DIR/bin"
else
  USER_BIN="$($PYTHON -c 'import sysconfig; print(sysconfig.get_paths()["scripts"])')"
fi

# --- verify ---
if ! command -v "$APP" >/dev/null 2>&1; then
  warn "$APP not in PATH. Adding..."
  printf 'export PATH="$PATH:%s"\n' "$USER_BIN" >> "$HOME/.bashrc"
  export PATH="$PATH:$USER_BIN"
fi

info "Running $APP init..."
$PYTHON -m "$APP" init 2>/dev/null || true

printf "\n"
ok "${APP} installed!"
printf "\n"
printf "  ${GREEN}superllm --help${NC}     — Show commands\n"
printf "  ${GREEN}superllm pull qwen2.5-0.5b${NC}  — Download a model\n"
printf "  ${GREEN}superllm open${NC}       — Open web UI\n"
printf "  ${GREEN}superllm run qwen2.5-0.5b${NC}   — Chat in terminal\n"
printf "\n"

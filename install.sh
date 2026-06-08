#!/usr/bin/env bash
set -euo pipefail

REPO="alop-hue/superLLM"
APP="superllm"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}::${NC} $1"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "${RED}✗${NC} $1"; exit 1; }

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
  if command -v "$cmd" &>/dev/null; then
    VER="$($cmd --version 2>&1 | grep -oP '\d+\.\d+\.?\d*' | head -1 | cut -d. -f1)"
    if [ "$VER" -ge 3 ] 2>/dev/null; then
      PYTHON="$cmd"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  fail "Python 3 not found. Install Python >= 3.10 from https://python.org"
fi

PY_VER="$($PYTHON --version 2>&1 | grep -oP '\d+\.\d+')"
info "Python $PY_VER found: $PYTHON"

MINOR="${PY_VER#*.}"
if [ "$MINOR" -lt 10 ] 2>/dev/null; then
  fail "Python >= 3.10 required (found $PY_VER)"
fi

# --- check pip ---
if ! $PYTHON -m pip --version &>/dev/null; then
  fail "pip not found. Install pip: $PYTHON -m ensurepip --upgrade"
fi

# --- install ---
info "Installing $APP from GitHub..."
$PYTHON -m pip install --upgrade pip -q

if $PYTHON -m pip install "git+https://github.com/$REPO.git" 2>&1; then
  ok "Installed $APP from GitHub"
elif $PYTHON -m pip install "https://github.com/$REPO/archive/main.tar.gz" 2>&1; then
  ok "Installed $APP (fallback)"
else
  warn "Installing from GitHub failed. Trying from source..."
  TMP="$(mktemp -d)"
  git clone --depth 1 "https://github.com/$REPO.git" "$TMP/$APP"
  cd "$TMP/$APP"
  $PYTHON -m pip install -e ".[dev]" 2>&1
  cd "$OLDPWD"
  rm -rf "$TMP"
  ok "Installed $APP from source"
fi

# --- verify ---
if ! command -v "$APP" &>/dev/null; then
  warn "$APP not in PATH. Adding..."
  USER_BIN="$("$PYTHON" -c 'import sysconfig; print(sysconfig.get_paths()["scripts"])')"
  echo "export PATH=\"\$PATH:$USER_BIN\"" >> "$HOME/.bashrc"
  export PATH="$PATH:$USER_BIN"
fi

info "Running $APP init..."
$PYTHON -m "$APP" init 2>/dev/null || true

echo ""
ok "${APP} installed!"
echo ""
echo -e "  ${GREEN}superllm --help${NC}     — Show commands"
echo -e "  ${GREEN}superllm pull qwen2.5-0.5b${NC}  — Download a model"
echo -e "  ${GREEN}superllm open${NC}       — Open web UI"
echo -e "  ${GREEN}superllm run qwen2.5-0.5b${NC}   — Chat in terminal"
echo ""

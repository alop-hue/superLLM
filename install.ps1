#!/usr/bin/env pwsh
# superLLM Windows Installer
param()

$ErrorActionPreference = "Stop"
$Repo = "alop-hue/superLLM"
$App = "superllm"

function Write-Info  { Write-Host ":: $_" -ForegroundColor Cyan }
function Write-Ok    { Write-Host "✓ $_" -ForegroundColor Green }
function Write-Warn  { Write-Host "⚠ $_" -ForegroundColor Yellow }
function Write-Fail  { Write-Host "✗ $_" -ForegroundColor Red; exit 1 }

Write-Info "Installing $App for Windows..."

# --- check Python ---
$py = $null
foreach ($cmd in @("python3", "python", "py")) {
  try {
    $v = & $cmd --version 2>&1
    if ($v -match "(\d+)\.(\d+)") {
      $py = $cmd
      break
    }
  } catch {}
}

if (-not $py) {
  Write-Fail "Python 3 not found. Install Python >= 3.10 from https://python.org"
}

$ver = & $py -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Info "Python $ver found: $py"

$major, $minor = $ver.Split('.')
if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 10)) {
  Write-Fail "Python >= 3.10 required (found $ver)"
}

# --- check pip ---
try {
  & $py -m pip --version 2>&1 | Out-Null
} catch {
  Write-Fail "pip not found. Run: $py -m ensurepip --upgrade"
}

# --- install ---
Write-Info "Installing $App from GitHub..."
& $py -m pip install --upgrade pip -q

$installed = $false
try {
  & $py -m pip install "git+https://github.com/$Repo.git" 2>&1
  if ($LASTEXITCODE -eq 0) { $installed = $true }
} catch {}

if (-not $installed) {
  Write-Warn "GitHub install failed. Installing from local source..."
  $tmp = Join-Path $env:TEMP "superllm-install"
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
  git clone --depth 1 "https://github.com/$Repo.git" $tmp 2>&1
  Set-Location $tmp
  & $py -m pip install -e ".[dev]" 2>&1
  Set-Location $env:USERPROFILE
  Remove-Item -Recurse -Force $tmp
}

Write-Ok "$App installed!"

Write-Info "Running $App init..."
try { & $py -m $App init 2>&1 | Out-Null } catch {}

Write-Ok ""
Write-Host "  superllm --help           — Show commands" -ForegroundColor Green
Write-Host "  superllm pull qwen2.5-0.5b — Download a model" -ForegroundColor Green
Write-Host "  superllm open              — Open web UI" -ForegroundColor Green
Write-Host "  superllm run qwen2.5-0.5b  — Chat in terminal" -ForegroundColor Green

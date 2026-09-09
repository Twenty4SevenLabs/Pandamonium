# Install OpenCode fleet config on Windows (247Laptop).
# Run in PowerShell on the laptop — not over SSH to Linux.
#
#   cd \\path\to\pandamonium   # or your clone
#   .\scripts\install-opencode-fleet-windows.ps1
#
# Reads API keys from .env in the repo (gitignored) and writes:
#   %USERPROFILE%\.config\opencode\opencode.json
#   User environment variables for UNSLOTH_*_API_KEY
#
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$ConfigDir = Join-Path $env:USERPROFILE ".config\opencode"
$SourceJson = Join-Path $RepoRoot "opencode.windows.json"
$EnvFile = Join-Path $RepoRoot ".env"

if (-not (Test-Path $SourceJson)) {
    Write-Error "Missing $SourceJson — run scripts/sync-opencode-unsloth-fleet.py on the cluster first."
}

New-Item -ItemType Directory -Force -Path $ConfigDir | Out-Null
Copy-Item -Force $SourceJson (Join-Path $ConfigDir "opencode.json")
Write-Host "Installed OpenCode config -> $ConfigDir\opencode.json"

$keys = @(
    "UNSLOTH_M1_API_KEY",
    "UNSLOTH_M2_API_KEY",
    "UNSLOTH_A1_API_KEY",
    "UNSLOTH_IMAC_API_KEY",
    "UNSLOTH_MINI_API_KEY",
    "UNSLOTH_LAPTOP_API_KEY",
    "UNSLOTH_API_KEY"
)

if (Test-Path $EnvFile) {
    foreach ($line in Get-Content $EnvFile) {
        if ($line -match '^\s*#' -or $line -notmatch '=') { continue }
        $name, $value = $line.Split('=', 2)
        $name = $name.Trim()
        $value = $value.Trim()
        if ($keys -contains $name -and $value) {
            [Environment]::SetEnvironmentVariable($name, $value, "User")
            Write-Host "Set user env $name"
        }
    }
} else {
    Write-Warning ".env not found at $EnvFile — set UNSLOTH_*_API_KEY in Windows User env manually."
}

Write-Host ""
Write-Host "Restart OpenCode Desktop, then /model — you should see Unsloth M1/M2/A1/iMac/mini/laptop providers."
Write-Host "Default uses Tailscale Serve URLs when on the tailnet."

@'
param(
  [string]$InstallDir = "$env:LOCALAPPDATA\Pandamonium\pc-cursor-bridge",
  [string]$ProjectsRoot = "$env:USERPROFILE\.cursor\projects",
  [string]$BindHost = "0.0.0.0",
  [int]$Port = 8051,
  [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

function Resolve-Python {
  foreach ($candidate in @("python", "python3", "py")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  throw "Python 3 is required but was not found on PATH."
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RepoRoot) {
  $RepoRoot = (Resolve-Path (Join-Path $scriptRoot "..\..")).Path
}

$python = Resolve-Python
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Force (Join-Path $RepoRoot "services\pc-cursor-bridge\pc_cursor_bridge.py") $InstallDir
Copy-Item -Force (Join-Path $RepoRoot "services\pc-cursor-bridge\transcript_io.py") $InstallDir

$tokenDir = Join-Path $env:USERPROFILE ".config\jarvis"
New-Item -ItemType Directory -Force -Path $tokenDir | Out-Null
$tokenFile = Join-Path $tokenDir "cursor-bridge-token"
if (-not (Test-Path $tokenFile)) {
  $bytes = New-Object byte[] 32
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  $token = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
  Set-Content -Path $tokenFile -Value $token -NoNewline -Encoding ascii
}

$runner = Join-Path $InstallDir "run-companion.ps1"
@'
param(
  [string]$BindHost = "0.0.0.0",
  [int]$Port = 8051
)
$installDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:JARVIS_CURSOR_BRIDGE_ALLOW_LAN = "1"
$env:JARVIS_CURSOR_BRIDGE_HOST = $BindHost
$env:JARVIS_CURSOR_BRIDGE_PORT = "$Port"
$env:JARVIS_CURSOR_BRIDGE_HOSTS = $BindHost
$env:JARVIS_CURSOR_BRIDGE_TOKEN_FILE = Join-Path $env:USERPROFILE ".config\jarvis\cursor-bridge-token"
$env:JARVIS_CURSOR_PROJECTS_ROOT = Join-Path $env:USERPROFILE ".cursor\projects"
Set-Location $installDir
& python pc_cursor_bridge.py
'@ | Set-Content -Path $runner -Encoding UTF8

$taskName = "PandamoniumPcCursorBridge"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`" -BindHost $BindHost -Port $Port"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

Write-Host "Installed PC Cursor bridge to $InstallDir"
Write-Host "Token file: $tokenFile"
Write-Host "Bind: http://${BindHost}:$Port"
Write-Host "Copy this token into Panda (.env):"
Get-Content $tokenFile

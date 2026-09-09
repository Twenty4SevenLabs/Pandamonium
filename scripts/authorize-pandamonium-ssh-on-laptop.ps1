# Allow the cluster (pve-prod / Pandamonium) to SSH into this Windows laptop as open2.
# Run once on 247Laptop in PowerShell (Admin not required):
#   .\scripts\authorize-pandamonium-ssh-on-laptop.ps1
#
$ErrorActionPreference = "Stop"
$SshDir = Join-Path $env:USERPROFILE ".ssh"
$AuthKeys = Join-Path $SshDir "authorized_keys"
$PubKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIInLW8Mb+c6SuCnUVTB5HIQFSZdlYbMoh26aU2YJunSx pandamonium-cookbook@prod"

New-Item -ItemType Directory -Force -Path $SshDir | Out-Null
$existing = @()
if (Test-Path $AuthKeys) {
    $existing = Get-Content $AuthKeys
}
if ($existing -contains $PubKey) {
    Write-Host "Already authorized: pandamonium-cookbook@prod"
    exit 0
}
Add-Content -Path $AuthKeys -Value $PubKey
Write-Host "Added cluster key to $AuthKeys"
Write-Host "Ensure OpenSSH Server is running and open2@247laptop accepts key auth."

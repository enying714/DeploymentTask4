$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (Test-Path .env) { throw '.env already exists. Edit it directly if a change is needed.' }
$DockerHubUser = Read-Host 'Your Docker Hub username (lowercase)'
if ($DockerHubUser -notmatch '^[a-z0-9][a-z0-9_-]+$') { throw 'Enter a valid Docker Hub username.' }
$RandomBytes = New-Object byte[] 32
$RandomGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $RandomGenerator.GetBytes($RandomBytes) } finally { $RandomGenerator.Dispose() }
$AppSecret = -join ($RandomBytes | ForEach-Object { $_.ToString('x2') })
@("DOCKERHUB_USER=$DockerHubUser", "SECRET_KEY=$AppSecret") | Set-Content .env -Encoding ascii
Write-Host 'Created local .env. Keep it private; do not include it in screenshots or source uploads.'

# Run elevated on finprint-host. The shared Caddy process serves immutable exports.
[CmdletBinding()]
param(
    [string]$Archive,
    [ValidatePattern('^[a-f0-9]{40}$')][string]$Version,
    [ValidatePattern('^[a-f0-9]{64}$')][string]$Sha256,
    [switch]$Rollback,
    [switch]$MigrateDns
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Root = 'C:\ProgramData\CORA'
$Releases = Join-Path $Root 'releases'
$SiteFile = Join-Path $Root 'Caddyfile'
$StateFile = Join-Path $Root 'state.json'
$Logs = Join-Path $Root 'logs'
$Main = 'C:\Users\ethan\finprint\scripts\selfhost\Caddyfile'
$Caddy = 'C:\Users\ethan\AppData\Local\Microsoft\WinGet\Links\caddy.exe'
$Tar = Join-Path $env:SystemRoot 'System32\tar.exe'
$Curl = Join-Path $env:SystemRoot 'System32\curl.exe'
$Utf8 = New-Object Text.UTF8Encoding $false
$ReleasePattern = '^\d{17}-[a-f0-9]{12}$'
$lock = $null
$changedConfig = $false
$dnsChanged = $false

function Invoke-Native([string]$File, [string[]]$Arguments) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $output = & $File @Arguments 2>&1 | Out-String; $code = $LASTEXITCODE }
    finally { $ErrorActionPreference = $saved }
    if ($code -ne 0) { throw "$File failed ($code): $output" }
    return $output.Trim()
}

function Reload-Caddy {
    foreach ($verb in 'validate', 'reload') {
        $output = Invoke-Native $Caddy @($verb, '--config', $Main, '--adapter', 'caddyfile')
        [IO.File]::AppendAllText((Join-Path $Logs 'caddy.log'), "[$([DateTime]::UtcNow.ToString('o'))] $verb`r`n$output`r`n", $Utf8)
    }
}

function Release-Path([string]$Name) {
    if ($Name -notmatch $ReleasePattern) { throw 'Invalid release name.' }
    $path = [IO.Path]::GetFullPath((Join-Path $Releases $Name))
    if (-not $path.StartsWith($Releases + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Release is outside deployment root.' }
    return $path
}

try {
    $admin = (New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $admin) { throw 'An elevated SSH session is required to update Caddy.' }
    if ($Rollback -and $MigrateDns) { throw 'Cannot migrate DNS during a rollback.' }
    New-Item -ItemType Directory -Force -Path $Releases, $Logs | Out-Null
    $lock = [IO.File]::Open((Join-Path $Root 'deploy.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
    $state = if (Test-Path -LiteralPath $StateFile) { Get-Content $StateFile -Raw | ConvertFrom-Json } else { $null }
    if ($Rollback) {
        if (-not $state -or -not $state.previous) { throw 'No previous CORA release is recorded.' }
        $name = $state.previous
        $release = Release-Path $name
        $Version = [IO.File]::ReadAllText((Join-Path $release 'version.txt')).Trim()
    } else {
        if (-not $Version -or -not $Sha256 -or -not $Archive) { throw 'Archive, Version and Sha256 are required.' }
        $archivePath = [IO.Path]::GetFullPath($Archive)
        if (-not $archivePath.StartsWith($Root + '\incoming\', [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Archive must be under CORA/incoming.'
        }
        $stream = [IO.File]::OpenRead($archivePath)
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $actualHash = [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
        finally { $stream.Dispose(); $hasher.Dispose() }
        if ($actualHash -ne $Sha256) { throw 'Archive checksum mismatch.' }
        $entries = Invoke-Native $Tar @('-tzf', $archivePath)
        foreach ($entry in ($entries -split '\r?\n')) {
            if ($entry -match '^[\\/]|^[a-zA-Z]:|(^|[\\/])\.\.([\\/]|$)') { throw 'Unsafe archive path.' }
        }
        $name = [DateTime]::UtcNow.ToString('yyyyMMddHHmmssfff') + '-' + $Version.Substring(0, 12)
        $release = Release-Path $name
        New-Item -ItemType Directory -Path $release | Out-Null
        $null = Invoke-Native $Tar @('-xzf', $archivePath, '-C', $release)
        Remove-Item -LiteralPath $archivePath -Force
    }
    foreach ($file in 'index.html', '404.html', 'version.txt', 'img/cora-screenshot.png') {
        if (-not (Test-Path -LiteralPath (Join-Path $release $file))) { throw "Incomplete release: $file" }
    }
    if (@(Get-ChildItem -LiteralPath $release -Recurse -Force | Where-Object {
        $_.Attributes -band [IO.FileAttributes]::ReparsePoint
    }).Count) { throw 'Release must contain ordinary files and directories only.' }
    if ([IO.File]::ReadAllText((Join-Path $release 'version.txt')).Trim() -ne $Version) { throw 'Release version mismatch.' }
    $oldMain = [IO.File]::ReadAllText($Main)
    $oldSite = if (Test-Path -LiteralPath $SiteFile) { [IO.File]::ReadAllText($SiteFile) } else { $null }
    $import = "# BEGIN CORA (managed)`r`nimport C:/ProgramData/CORA/Caddyfile`r`n# END CORA (managed)"
    $newMain = $oldMain
    if (-not $oldMain.Contains('# BEGIN CORA (managed)')) {
        $newMain = $oldMain.TrimEnd() + "`r`n`r`n$import`r`n"
    } elseif (-not ($oldMain -replace "`r", '').Contains(($import -replace "`r", ''))) {
        throw 'Existing CORA import differs; inspect it before changing configuration.'
    }
    $rootPath = $release.Replace('\', '/')
    $config = @"
# Managed by web/deploy/host.ps1.
cora.ethanyanxu.com {
    root * "$rootPath"
    encode zstd gzip
    header {
        Strict-Transport-Security "max-age=63072000"
        X-Content-Type-Options nosniff
        X-CORA-Host finprint-host
    }
    @hashed path /_next/static/*
    header @hashed Cache-Control "public, max-age=31536000, immutable"
    @unhashed not path /_next/static/*
    header @unhashed Cache-Control "public, max-age=0, must-revalidate"
    file_server
    handle_errors 404 {
        rewrite * /404.html
        file_server
    }
    log {
        output file C:/ProgramData/CORA/logs/access.log {
            roll_size 10MB
            roll_keep 3
        }
    }
}

# A private preflight endpoint verifies the files before the first DNS cutover.
http://127.0.0.1:4186 {
    bind 127.0.0.1
    root * "$rootPath"
    file_server
}
"@
    Copy-Item -LiteralPath $Main -Destination (Join-Path $Logs "Caddyfile-before-$name")
    if ([IO.File]::ReadAllText($Main) -ne $oldMain) { throw 'Shared Caddy configuration changed during preflight; retry.' }
    $changedConfig = $true
    [IO.File]::WriteAllText($SiteFile, $config, $Utf8)
    if ($newMain -ne $oldMain) { [IO.File]::WriteAllText($Main, $newMain, $Utf8) }
    Reload-Caddy
    $probe = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:4186/version.txt' -TimeoutSec 15
    if ($probe.Content.Trim() -ne $Version) { throw 'Caddy preflight returned the wrong release.' }
    $page = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:4186/' -TimeoutSec 15
    if (-not $page.Content.Contains('Coastal Risk Analyzer')) { throw 'Caddy preflight did not return CORA.' }
    Write-Host "Caddy preflight passed for $Version"
    if ($MigrateDns) { $dnsChanged = & (Join-Path $Root 'dns.ps1') -ExpectedVersion $Version }
    $deadline = (Get-Date).AddSeconds(180)
    $verified = $false
    do {
        try {
            $served = Invoke-Native $Curl @('--silent', '--show-error', '--fail', '--max-time', '10',
                '--ssl-revoke-best-effort', '--resolve', 'cora.ethanyanxu.com:443:127.0.0.1', 'https://cora.ethanyanxu.com/version.txt')
            $verified = $served -eq $Version
        } catch { $lastError = $_.Exception.Message }
        if (-not $verified) { Start-Sleep -Seconds 3 }
    } while (-not $verified -and (Get-Date) -lt $deadline)
    if (-not $verified) { throw "HTTPS did not serve the release with a trusted certificate: $lastError" }
    $previous = if ($state) { $state.active } else { $null }
    $newState = [ordered]@{ active = $name; previous = $previous; commit = $Version; activatedAt = [DateTime]::UtcNow.ToString('o') }
    [IO.File]::WriteAllText($StateFile, ($newState | ConvertTo-Json), $Utf8)
    $changedConfig = $false
    Write-Host "Activated CORA $Version with verified HTTPS."
} catch {
    $failure = $_.Exception.Message
    if ($dnsChanged) {
        try { $null = & (Join-Path $Root 'dns.ps1') -Rollback }
        catch { Write-Host "DNS rollback requires attention: $($_.Exception.Message)" }
    }
    if ($changedConfig) {
        if ($newMain -ne $oldMain) {
            $currentMain = [IO.File]::ReadAllText($Main)
            # Preserve any other site's import added while certificate issuance ran.
            $restoredMain = if ($currentMain -eq $newMain) { $oldMain } else { $currentMain.Replace($import, '') }
            [IO.File]::WriteAllText($Main, $restoredMain, $Utf8)
        }
        if ($null -ne $oldSite) { [IO.File]::WriteAllText($SiteFile, $oldSite, $Utf8) }
        elseif (Test-Path -LiteralPath $SiteFile) { Remove-Item -LiteralPath $SiteFile -Force }
        try { Reload-Caddy } catch { Write-Host "Caddy recovery requires attention: $($_.Exception.Message)" }
    }
    Write-Host "CORA activation failed: $failure"
    exit 1
} finally { if ($lock) { $lock.Dispose() } }

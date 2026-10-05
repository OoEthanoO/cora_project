# Build on the development PC, then upload only static files to finprint-host.
[CmdletBinding()]
param(
    [switch]$Rollback,
    [switch]$MigrateDns,
    [ValidatePattern('^[a-zA-Z0-9.-]+$')][string]$SshHost = 'finprint-host'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$WebRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$RemoteRoot = 'C:\ProgramData\CORA'
$Domain = 'cora.ethanyanxu.com'
$Tar = Join-Path $env:SystemRoot 'System32\tar.exe'
$Utf8 = New-Object Text.UTF8Encoding $false

function Invoke-Checked([string]$File, [string[]]$Arguments) {
    # Windows PowerShell treats native stderr as an error record.
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $File @Arguments | Out-Host; $code = $LASTEXITCODE }
    finally { $ErrorActionPreference = $saved }
    if ($code -ne 0) { throw "$File failed (exit $code)." }
}

function Invoke-Remote([string]$Script) {
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Script))
    Invoke-Checked 'ssh.exe' @('-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', $SshHost,
        "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand $encoded")
}

$previousSite = $env:NEXT_PUBLIC_SITE_URL
$previousDownload = $env:NEXT_PUBLIC_DOWNLOAD_URL
$archive = $null
Push-Location $WebRoot
try {
    if ($Rollback -and $MigrateDns) { throw 'Use -Rollback or -MigrateDns, not both.' }
    if ($Rollback) {
        Invoke-Remote "& '$RemoteRoot\host.ps1' -Rollback"
    } else {
        $version = (& git.exe rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0 -or $version -notmatch '^[a-f0-9]{40}$') { throw 'Cannot identify the Git commit.' }
        $status = & git.exe status --porcelain
        if ($LASTEXITCODE -ne 0 -or $status) { throw 'Commit changes before deploying so version.txt identifies the exact source.' }
        $manifest = Get-Content src\lib\release.json -Raw | ConvertFrom-Json
        $download = "https://github.com/OoEthanoO/cora_project/releases/download/v$($manifest.version)/$($manifest.filename)"
        $asset = Invoke-RestMethod -Uri "https://api.github.com/repos/OoEthanoO/cora_project/releases/tags/v$($manifest.version)" -TimeoutSec 30
        $match = @($asset.assets | Where-Object { $_.name -eq $manifest.filename })
        if ($match.Count -ne 1 -or $match[0].size -ne $manifest.sizeBytes -or
            $match[0].digest -ne ('sha256:' + $manifest.sha256)) {
            throw 'GitHub installer does not match the checked-in release manifest.'
        }
        $env:NEXT_PUBLIC_SITE_URL = "https://$Domain"
        $env:NEXT_PUBLIC_DOWNLOAD_URL = $download
        Write-Host "Building CORA $version"
        Invoke-Checked 'npm.cmd' @('ci', '--no-audit', '--no-fund')
        Invoke-Checked 'npm.cmd' @('run', 'lint')
        # Clear only the resolved export directory, never arbitrary paths.
        $out = [IO.Path]::GetFullPath((Join-Path $WebRoot 'out'))
        if ($out -ne ($WebRoot + '\out')) { throw 'Unexpected export directory.' }
        if (Test-Path -LiteralPath $out) {
            if ((Get-Item -LiteralPath $out).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'out/ must not be a link.' }
            Remove-Item -LiteralPath $out -Recurse -Force
        }
        Invoke-Checked 'npm.cmd' @('run', 'build')
        foreach ($file in 'index.html', '404.html', 'img/cora-icon.png', 'img/cora-screenshot.png') {
            if (-not (Test-Path -LiteralPath (Join-Path $out $file))) { throw "Missing export file: $file" }
        }
        $html = [IO.File]::ReadAllText((Join-Path $out 'index.html'))
        if (-not $html.Contains($download) -or -not $html.Contains("https://$Domain/img/cora-screenshot.png") -or
            $html.Contains('/_next/image?') -or $html.Contains('http://localhost:3000')) {
            throw 'Export has an invalid download, metadata origin, or server-dependent image URL.'
        }
        [IO.File]::WriteAllText((Join-Path $out 'version.txt'), $version, $Utf8)
        $archiveName = 'cora-' + [Guid]::NewGuid().ToString('N') + '.tgz'
        $archive = Join-Path $env:TEMP $archiveName
        Invoke-Checked $Tar @('-czf', $archive, '-C', $out, '.')
        $stream = [IO.File]::OpenRead($archive)
        $hasher = [Security.Cryptography.SHA256]::Create()
        try { $hash = [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
        finally { $stream.Dispose(); $hasher.Dispose() }
        Invoke-Remote @"
`$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path '$RemoteRoot' | Out-Null
& icacls.exe '$RemoteRoot' /inheritance:r /grant:r '*S-1-5-18:(OI)(CI)F' '*S-1-5-32-544:(OI)(CI)F' | Out-Null
if (`$LASTEXITCODE -ne 0) { throw 'Failed to secure the deployment directory.' }
New-Item -ItemType Directory -Force -Path '$RemoteRoot\incoming' | Out-Null
"@
        foreach ($name in 'host.ps1', 'dns.ps1') {
            Invoke-Checked 'scp.exe' @('-q', '-o', 'BatchMode=yes', (Join-Path $PSScriptRoot $name), "${SshHost}:C:/ProgramData/CORA/$name")
        }
        Invoke-Checked 'scp.exe' @('-q', '-o', 'BatchMode=yes', $archive, "${SshHost}:C:/ProgramData/CORA/incoming/$archiveName")
        $dnsFlag = if ($MigrateDns) { ' -MigrateDns' } else { '' }
        Invoke-Remote "& '$RemoteRoot\host.ps1' -Archive '$RemoteRoot\incoming\$archiveName' -Version '$version' -Sha256 '$hash'$dnsFlag"
    }
    # Read the host's active version, then require the same value over public DNS.
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes(
        "(Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:4186/version.txt').Content.Trim()"))
    # The remote login shell emits a harmless profile-policy error on stderr.
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $expected = & ssh.exe -o BatchMode=yes $SshHost "powershell -NoProfile -NonInteractive -EncodedCommand $encoded" 2>$null
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $saved }
    if ($code -ne 0) { throw 'Cannot read the active release.' }
    $expected = "$expected".Trim()
    $response = Invoke-WebRequest -UseBasicParsing -Uri "https://$Domain/version.txt" -TimeoutSec 30
    if ($response.Content.Trim() -ne $expected -or $response.Headers['X-CORA-Host'] -ne 'finprint-host') {
        throw 'Host activation succeeded, but public DNS is not serving the expected CORA release yet.'
    }
    Write-Host "Verified https://$Domain on finprint-host at $expected"
} catch {
    Write-Host "Deploy failed: $($_.Exception.Message)"
    exit 1
} finally {
    $env:NEXT_PUBLIC_SITE_URL = $previousSite
    $env:NEXT_PUBLIC_DOWNLOAD_URL = $previousDownload
    if ($archive -and (Test-Path -LiteralPath $archive)) { Remove-Item -LiteralPath $archive -Force }
    Pop-Location
}

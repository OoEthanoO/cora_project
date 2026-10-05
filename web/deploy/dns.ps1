# One-time DNS migration. The shared credential remains protected on the host.
[CmdletBinding()]
param([string]$ExpectedVersion, [switch]$Rollback)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$hostname = 'cora.ethanyanxu.com'
$target = 'finprint.ethanyanxu.com'
$backupPath = 'C:\ProgramData\CORA\dns-migration.json'
$Utf8 = New-Object Text.UTF8Encoding $false
$settings = Get-Content 'C:\ProgramData\YanLearn\secrets\cloudflare-ddns.json' -Raw | ConvertFrom-Json

function Invoke-CoraDns([string]$Method, [string]$Path, $Body = $null) {
    $request = @{
        Uri = ('https://api.cloudflare.com/client/v4/zones/' + $settings.ZoneId + $Path)
        Method = $Method; Headers = $script:coraDnsHeaders; TimeoutSec = 30
    }
    if ($null -ne $Body) { $request.Body = $Body | ConvertTo-Json -Compress; $request.ContentType = 'application/json' }
    try { $response = Invoke-RestMethod @request }
    catch { throw 'Cloudflare request failed; check the protected credential and connectivity on the host.' }
    if (-not $response.success) { throw 'Cloudflare did not accept the DNS request.' }
    return $response.result
}

try {
    Add-Type -AssemblyName System.Security
    $plain = [Security.Cryptography.ProtectedData]::Unprotect(
        [Convert]::FromBase64String([IO.File]::ReadAllText($settings.TokenPath)), $null,
        [Security.Cryptography.DataProtectionScope]::LocalMachine)
    $script:coraDnsHeaders = @{ Authorization = ('Bearer ' + [Text.Encoding]::UTF8.GetString($plain)) }
    [Array]::Clear($plain, 0, $plain.Length)
    $current = @(Invoke-CoraDns 'GET' ('/dns_records?name=' + $hostname))
    $backup = if (Test-Path $backupPath) { Get-Content $backupPath -Raw | ConvertFrom-Json } else { $null }
    # Recover the record ID if a prior POST succeeded but its response was lost.
    $comment = 'CORA on finprint-host; follows the existing home-server DDNS record.'
    if ($backup -and -not $backup.recordId -and $backup.hostname -eq $hostname -and
        @($backup.previousExplicitRecords).Count -eq 0 -and $current.Count -eq 1 -and
        $current[0].type -eq 'CNAME' -and $current[0].content -eq $target -and
        -not $current[0].proxied -and $current[0].comment -eq $comment) {
        $backup.recordId = $current[0].id
        [IO.File]::WriteAllText($backupPath, ($backup | ConvertTo-Json -Depth 8), $Utf8)
    }
    if ($Rollback) {
        if (-not $backup) { throw 'No CORA DNS migration backup exists.' }
        if ($current.Count -eq 0) { return $false }
        if ($current.Count -ne 1 -or $current[0].id -ne $backup.recordId -or
            $current[0].type -ne 'CNAME' -or $current[0].content -ne $target -or $current[0].proxied) {
            throw 'CORA DNS has changed since migration; refusing to remove it.'
        }
        $null = Invoke-CoraDns 'DELETE' ('/dns_records/' + $backup.recordId)
        if (@(Invoke-CoraDns 'GET' ('/dns_records?name=' + $hostname)).Count -ne 0) { throw 'DNS rollback verification failed.' }
        Write-Host 'Removed only the CORA override; the previous wildcard applies again.'
        return $true
    }
    $probe = Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:4186/version.txt' -TimeoutSec 15
    if ($ExpectedVersion -notmatch '^[a-f0-9]{40}$' -or $probe.Content.Trim() -ne $ExpectedVersion) {
        throw 'A verified CORA release must be served locally before DNS changes.'
    }
    if ($current.Count -eq 1 -and $current[0].type -eq 'CNAME' -and $current[0].content -eq $target -and -not $current[0].proxied) {
        Write-Host 'CORA DNS already follows finprint-host.'
        return $false
    }
    if ($current.Count -ne 0) { throw 'An unexpected explicit CORA DNS record exists; inspect it before migrating.' }
    $wildcard = @(Invoke-CoraDns 'GET' '/dns_records?name=%2A.ethanyanxu.com')
    if ($wildcard.Count -ne 1 -or $wildcard[0].type -ne 'CNAME' -or $wildcard[0].content -ne 'cname.vercel-dns-017.com') {
        throw 'The expected Vercel wildcard has changed; inspect DNS before migrating.'
    }
    $backup = [ordered]@{
        hostname = $hostname; target = $target; previousExplicitRecords = @()
        wildcard = $wildcard[0]; changedAt = [DateTime]::UtcNow.ToString('o'); recordId = $null
    }
    [IO.File]::WriteAllText($backupPath, ($backup | ConvertTo-Json -Depth 8), $Utf8)
    $created = Invoke-CoraDns 'POST' '/dns_records' @{
        type = 'CNAME'; name = $hostname; content = $target; ttl = 60; proxied = $false
        comment = $comment
    }
    $backup.recordId = $created.id
    [IO.File]::WriteAllText($backupPath, ($backup | ConvertTo-Json -Depth 8), $Utf8)
    $verified = @(Invoke-CoraDns 'GET' ('/dns_records?name=' + $hostname))
    if ($verified.Count -ne 1 -or $verified[0].id -ne $created.id -or $verified[0].content -ne $target -or $verified[0].proxied) {
        throw 'DNS cutover verification failed.'
    }
    Write-Host 'cora.ethanyanxu.com now follows finprint.ethanyanxu.com (DNS only, TTL 60).'
    return $true
} finally { $script:coraDnsHeaders = $null }

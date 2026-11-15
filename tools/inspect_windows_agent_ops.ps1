#requires -Version 7.0
[CmdletBinding()]
param(
    [ValidateRange(1, 30)][int]$TimeoutSeconds = 5,
    [ValidatePattern('^[\w -]{1,80}$')][string]$RelayTaskName,
    [ValidatePattern('^[\w -]{1,80}$')][string]$AssetsTaskName,
    [ValidatePattern('^\\[\w \\-]*\\$|^\\$')][string]$TaskPath = '\'
)

# Every child is this same trusted PowerShell executable, with a fixed query body.
# No profile, external CLI startup, credentials, remote sessions or file output.
function Invoke-OpsProcess {
    param([string]$Code, [int]$Seconds)
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = [Environment]::ProcessPath
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.ArgumentList.Add('-NoLogo')
    $info.ArgumentList.Add('-NoProfile')
    $info.ArgumentList.Add('-NonInteractive')
    $info.ArgumentList.Add('-EncodedCommand')
    $info.ArgumentList.Add([Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Code)))
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    try {
        $null = $process.Start()
        $out = $process.StandardOutput.ReadToEndAsync()
        $err = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($Seconds * 1000)) {
            # Terminate only the query process tree created immediately above.
            $process.Kill($true)
            return @{ Status = 'unknown'; Reason = 'timeout'; Value = $null }
        }
        if ($process.ExitCode -ne 0) { throw 'query-failed' }
        return ($out.GetAwaiter().GetResult() | ConvertFrom-Json -AsHashtable -ErrorAction Stop)
    } catch {
        return @{ Status = 'unknown'; Reason = 'query-failed'; Value = $null }
    } finally { $process.Dispose() }
}

function Get-OpsReport {
    $queries = [ordered]@{
        sleep_ac = "`$r = & powercfg.exe /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE; if (`$LASTEXITCODE -ne 0) { throw 'query-failed' }; `$v = [regex]::Matches((`$r -join ' '), '0x[0-9a-fA-F]{8}'); if (`$v.Count -ne 2) { throw 'format' }; [Convert]::ToUInt32(`$v[0].Value.Substring(2),16)"
        sleep_dc = "`$r = & powercfg.exe /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE; if (`$LASTEXITCODE -ne 0) { throw 'query-failed' }; `$v = [regex]::Matches((`$r -join ' '), '0x[0-9a-fA-F]{8}'); if (`$v.Count -ne 2) { throw 'format' }; [Convert]::ToUInt32(`$v[1].Value.Substring(2),16)"
        scheduler = "(Get-CimInstance -ClassName Win32_Service -Filter `"Name='Schedule'`" -Property State -OperationTimeoutSec 2 -ErrorAction Stop).State"
        tailscale_service = "(Get-CimInstance -ClassName Win32_Service -Filter `"Name='Tailscale'`" -Property State -OperationTimeoutSec 2 -ErrorAction Stop).State"
    }
    foreach ($name in @('claude', 'codex', 'tailscale', 'pwsh')) {
        # Read executable metadata; never run a vendor CLI or a package-manager shim.
        $queries["version_$name"] = "`$c = Get-Command '$name' -CommandType Application -ErrorAction Stop | Select-Object -First 1; if (`$c.Path -notmatch '\.exe$') { throw 'metadata-unavailable' }; [Diagnostics.FileVersionInfo]::GetVersionInfo(`$c.Path).ProductVersion"
    }
    $slots = @{ relay_task = $RelayTaskName; assets_task = $AssetsTaskName }
    foreach ($slot in $slots.Keys) {
        if ($slots[$slot]) {
            $queries[$slot] = "(Get-ScheduledTask -TaskName '$($slots[$slot])' -TaskPath '$TaskPath' -ErrorAction Stop).State.ToString()"
        }
    }
    $report = [ordered]@{}
    foreach ($key in $queries.Keys) {
        $body = @"
try {
    `$v = & { $($queries[$key]) }
    if (`$null -eq `$v -or [string]::IsNullOrWhiteSpace([string]`$v)) { throw 'empty' }
    @{Status='ok';Reason='none';Value=[string]`$v} | ConvertTo-Json -Compress
} catch [System.Management.Automation.CommandNotFoundException] {
    @{Status='not-installed';Reason='missing-command';Value=`$null} | ConvertTo-Json -Compress
} catch {
    @{Status='unknown';Reason='unavailable';Value=`$null} | ConvertTo-Json -Compress
}
"@
        $raw = Invoke-OpsProcess -Code $body -Seconds $TimeoutSeconds
        $row = @{ status = 'unknown'; reason = 'unavailable'; value = $null }
        if ($raw.Status -eq 'not-installed') { $row.status = 'not-installed'; $row.reason = 'missing-command' }
        elseif ($raw.Reason -in @('timeout', 'query-failed')) { $row.reason = $raw.Reason }
        elseif ($raw.Status -eq 'ok') {
            $value = [string]$raw.Value
            $valid = if ($key -like 'sleep_*') { $value -match '^\d{1,10}$' -and [decimal]$value -le 4294967295 }
            elseif ($key -like 'version_*') { $value -match '^\d+(\.\d+){1,3}$' -and $value.Length -le 40 }
            else { $value -cin @('Running', 'Stopped', 'Paused', 'Ready', 'Disabled', 'Queued', 'Unknown') }
            if ($valid) { $row = @{ status = 'ok'; reason = 'none'; value = $value } }
        }
        $report[$key] = $row
    }
    foreach ($slot in $slots.Keys) {
        if (-not $slots[$slot]) { $report[$slot] = @{ status = 'unknown'; reason = 'not-configured'; value = $null } }
    }
    return $report
}

if ($MyInvocation.InvocationName -ne '.') {
    Get-OpsReport | ConvertTo-Json -Depth 4
}

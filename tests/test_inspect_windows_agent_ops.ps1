#requires -Version 7.0
$ErrorActionPreference = 'Stop'
$target = Join-Path $PSScriptRoot '../tools/inspect_windows_agent_ops.ps1'
. $target -RelayTaskName 'FakeRelay' -AssetsTaskName 'FakeAssets'
$script:checks = 0
function Assert-True($Condition, $Label) {
    if (-not $Condition) { throw "FAIL: $Label" }
    $script:checks++
}

# Closed command allowlist, also applied to every generated child query below.
$allowed = @('Invoke-OpsProcess','Get-OpsReport','ConvertFrom-Json','ConvertTo-Json',
    'Get-Command','Select-Object','Get-CimInstance','Get-ScheduledTask','powercfg.exe')
function Assert-QueryAst([string]$Code) {
    $tokens = $null; $errors = $null
    $ast = [Management.Automation.Language.Parser]::ParseInput($Code, [ref]$tokens, [ref]$errors)
    Assert-True ($errors.Count -eq 0) 'parse'
    foreach ($cmd in $ast.FindAll({param($n) $n -is [Management.Automation.Language.CommandAst]}, $true)) {
        $name = $cmd.GetCommandName()
        # The only scriptblock invocation is the literal query inside the wrapper.
        if ($cmd.CommandElements[0] -is [Management.Automation.Language.ScriptBlockExpressionAst]) { continue }
        Assert-True ($name -in $allowed) "allowlisted command: $name"
        if ($name -eq 'powercfg.exe') {
            Assert-True ($cmd.Extent.Text -eq '& powercfg.exe /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE') 'powercfg query only'
        }
        if ($name -eq 'Get-ScheduledTask') {
            Assert-True ($cmd.Extent.Text -match '-TaskName ''Fake(Relay|Assets)'' -TaskPath ''\\''') 'exact local task selector'
        }
        if ($name -eq 'Get-CimInstance') {
            Assert-True ($cmd.Extent.Text -match 'Win32_Service -Filter "Name=''(?:Schedule|Tailscale)''" -Property State -OperationTimeoutSec 2') 'filtered service query'
        }
    }
    Assert-True ($Code -notmatch '(?i)-(ComputerName|CimSession|Credential)\b|HKLM:|HKCU:|Get-Content|Invoke-Expression') 'no remote or credential access'
    foreach ($call in $ast.FindAll({param($n) $n -is [Management.Automation.Language.InvokeMemberExpressionAst]}, $true)) {
        Assert-True ($call.Member.Value -in @('new','Add','Start','ReadToEndAsync','WaitForExit','Kill',
            'GetAwaiter','GetResult','Dispose','ToBase64String','GetBytes','Matches','ToUInt32',
            'Substring','GetVersionInfo','ToString','IsNullOrWhiteSpace')) 'method allowlist'
    }
    Assert-True ($ast.FindAll({param($n) $n -is [Management.Automation.Language.RedirectionAst]}, $true).Count -eq 0) 'stdout only'
}
Assert-QueryAst ([IO.File]::ReadAllText($target))
foreach ($bad in @('Set-Service -Name Schedule -StartupType Disabled',
    '& powercfg.exe /change standby-timeout-ac 0',
    'Get-CimInstance -ComputerName example -ClassName Win32_Service',
    'Get-ScheduledTask -TaskName *', '[IO.File]::WriteAllText("example", "x")')) {
    $rejected = $false
    try { Assert-QueryAst $bad } catch { $rejected = $true }
    Assert-True $rejected 'AST guard rejects mutation or broad query'
}
$script:mode = 'ok'; $script:seen = 0
function Invoke-OpsProcess {
    param([string]$Code, [int]$Seconds)
    Assert-QueryAst $Code
    $script:seen++
    if ($Code -match "Name='Schedule'") { $script:serviceBody = $Code }
    switch ($script:mode) {
        ok {
            $v = if ($Code -match 'powercfg') {'0'} elseif ($Code -match 'Get-Command') {'1.2.3'} else {'Running'}
            return @{Status='ok';Reason='none';Value=$v}
        }
        missing { return @{Status='not-installed';Reason='missing-command';Value=$null} }
        denied { return @{Status='unknown';Reason='unavailable';Value='host-Fake user-Fake 192.0.2.1 token-Fake'} }
        timeout { return @{Status='unknown';Reason='timeout';Value=$null} }
        hostile { return @{Status='ok';Reason='none';Value='host-Fake user-Fake 192.0.2.1 token-Fake'} }
    }
}
foreach ($mode in @('ok','missing','denied','timeout','hostile')) {
    $script:mode = $mode
    $r = Get-OpsReport
    Assert-True ($r.Count -eq 10) "$mode fields"
    foreach ($row in $r.Values) {
        $expected = if ($mode -eq 'ok') {'ok'} elseif ($mode -eq 'missing') {'not-installed'} else {'unknown'}
        Assert-True ($row.status -eq $expected) "$mode status"
        if ($mode -eq 'timeout') { Assert-True ($row.reason -eq 'timeout') 'timeout reason' }
    }
    $json = $r | ConvertTo-Json -Depth 4
    Assert-True ($json -notmatch 'host-Fake|user-Fake|192\.0\.2\.1|token-Fake|FakeRelay|FakeAssets') "$mode privacy"
}
Assert-True ($script:seen -eq 50) 'all ten queries tested in five modes'
Remove-Variable RelayTaskName, AssetsTaskName
$r = Get-OpsReport
Assert-True ($r.relay_task.reason -eq 'not-configured' -and $r.assets_task.reason -eq 'not-configured') 'no task enumeration by default'

# Exercise the real process timeout and exception conversion, without system queries.
. $target
$r = Invoke-OpsProcess -Code 'while ($true) {}' -Seconds 1
Assert-True ($r.Reason -eq 'timeout') 'real bounded child timeout'
$r = Invoke-OpsProcess -Code 'throw "private error"' -Seconds 5
Assert-True ($r.Reason -eq 'query-failed' -and $null -eq $r.Value) 'real child error redacted'
$r = Invoke-OpsProcess -Code ('function Get-CimInstance { throw [UnauthorizedAccessException]::new("private-host") }; ' + $script:serviceBody) -Seconds 5
Assert-True ($r.Status -eq 'unknown' -and $r.Reason -eq 'unavailable' -and $null -eq $r.Value) 'query wrapper catches mocked access denied'
$r = Invoke-OpsProcess -Code ('function Get-CimInstance { throw [Management.Automation.CommandNotFoundException]::new("private-host") }; ' + $script:serviceBody) -Seconds 5
Assert-True ($r.Status -eq 'not-installed' -and $null -eq $r.Value) 'query wrapper catches mocked missing command'
Write-Output "PASS: $script:checks assertions; five mock modes; real child timeout/error"

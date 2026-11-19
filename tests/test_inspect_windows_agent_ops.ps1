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
# DisabledRule is used only by the in-memory mutation tests below. Never execute
# counterexamples: they are input to Parser.ParseInput, not ScriptBlock.Create.
function Assert-GuardRule($Rule, $Condition, $DisabledRule) {
    if ($Rule -ne $DisabledRule) { Assert-True $Condition "AST rule: $Rule" }
}
function Assert-QueryAst([string]$Code, [string]$DisabledRule = '') {
    $tokens = $null; $errors = $null
    $ast = [Management.Automation.Language.Parser]::ParseInput($Code, [ref]$tokens, [ref]$errors)
    Assert-True ($errors.Count -eq 0) 'parse'
    foreach ($cmd in $ast.FindAll({param($n) $n -is [Management.Automation.Language.CommandAst]}, $true)) {
        $name = $cmd.GetCommandName()
        # The only scriptblock invocation is the literal query inside the wrapper.
        if ($cmd.CommandElements[0] -is [Management.Automation.Language.ScriptBlockExpressionAst]) { continue }
        Assert-True ($name -in ($allowed + 'New-Object')) "allowlisted command: $name"
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
    # Compare full receivers, not just method names. This is a finite source
    # regression contract for this script, not a sandbox for arbitrary PowerShell.
    $calls = @(
        '$process.Start()', '$process.StandardOutput.ReadToEndAsync()',
        '$process.StandardError.ReadToEndAsync()', '$process.WaitForExit($Seconds * 1000)',
        '$process.Kill($true)', '$out.GetAwaiter().GetResult()', '$out.GetAwaiter()',
        '$process.Dispose()', '[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Code))',
        '[Text.Encoding]::Unicode.GetBytes($Code)',
        "[regex]::Matches((`$r -join ' '), '0x[0-9a-fA-F]{8}')",
        '[Convert]::ToUInt32($v[$v.Count - 2].Value.Substring(2),16)',
        '[Convert]::ToUInt32($v[$v.Count - 1].Value.Substring(2),16)',
        '$v[$v.Count - 2].Value.Substring(2)', '$v[$v.Count - 1].Value.Substring(2)',
        '[Diagnostics.FileVersionInfo]::GetVersionInfo($c.Path)',
        "(Get-ScheduledTask -TaskName 'FakeRelay' -TaskPath '\' -ErrorAction Stop).State.ToString()",
        "(Get-ScheduledTask -TaskName 'FakeAssets' -TaskPath '\' -ErrorAction Stop).State.ToString()",
        '[string]::IsNullOrWhiteSpace([string]$v)'
    )
    $argumentCalls = @(
        "`$info.ArgumentList.Add('-NoLogo')", "`$info.ArgumentList.Add('-NoProfile')",
        "`$info.ArgumentList.Add('-NonInteractive')", "`$info.ArgumentList.Add('-EncodedCommand')",
        '$info.ArgumentList.Add([Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Code)))'
    )
    $memberWrites = @(
        '$info.FileName', '$info.UseShellExecute', '$info.CreateNoWindow',
        '$info.RedirectStandardOutput', '$info.RedirectStandardError', '$process.StartInfo'
    )
    $settings = @(
        '$info.FileName = [Environment]::ProcessPath', '$info.UseShellExecute = $false',
        '$info.CreateNoWindow = $true', '$info.RedirectStandardOutput = $true',
        '$info.RedirectStandardError = $true', '$process.StartInfo = $info'
    )
    $assignments = @($ast.FindAll({param($n) $n -is [Management.Automation.Language.AssignmentStatementAst]}, $true))
    foreach ($assignment in $assignments) {
        $members = @($assignment.Left.FindAll({param($n) $n -is [Management.Automation.Language.MemberExpressionAst]}, $true))
        if ($members.Count) {
            Assert-GuardRule 'member-write' (($assignment.Left.Extent.Text -cin $memberWrites -and $assignment.Operator -eq 'Equals') -or
                $assignment.Extent.Text -cin @("`$row.status = 'not-installed'", "`$row.reason = 'missing-command'", '$row.reason = $raw.Reason')) $DisabledRule
            if ($assignment.Left.Extent.Text -cin $memberWrites) {
                $rule = if ($assignment.Left.Extent.Text -eq '$info.FileName') { 'executable' } else { 'arguments' }
                Assert-GuardRule $rule ($assignment.Extent.Text -cin $settings) $DisabledRule
            }
        }
    }
    foreach ($unary in $ast.FindAll({param($n) $n -is [Management.Automation.Language.UnaryExpressionAst]}, $true)) {
        if ($unary.TokenKind -in @('PlusPlus','MinusMinus','PostfixPlusPlus','PostfixMinusMinus')) {
            Assert-GuardRule 'member-write' ($unary.Child.FindAll({param($n) $n -is [Management.Automation.Language.MemberExpressionAst]}, $true).Count -eq 0) $DisabledRule
        }
    }
    # One finite dangerous-type list for all three construction paths. Compare
    # names syntactically: never resolve a type or execute a counterexample.
    $dangerousTypes = @('IO.StreamWriter', 'IO.StreamReader', 'IO.FileStream',
        'IO.FileInfo', 'IO.DirectoryInfo', 'Diagnostics.ProcessStartInfo', 'Diagnostics.Process')
    $constructors = @('[Diagnostics.ProcessStartInfo]::new()', '[Diagnostics.Process]::new()')
    foreach ($node in $ast.FindAll({param($n)
        $n -is [Management.Automation.Language.ConvertExpressionAst] -or
        ($n -is [Management.Automation.Language.CommandAst] -and $n.GetCommandName() -eq 'New-Object') -or
        ($n -is [Management.Automation.Language.InvokeMemberExpressionAst] -and $n.Member.Value -eq 'new')
    }, $true)) {
        $isConversion = $node -is [Management.Automation.Language.ConvertExpressionAst]
        $typeNames = if ($isConversion) { $node.Type.TypeName.FullName }
        elseif ($node -is [Management.Automation.Language.CommandAst]) {
            # Includes positional and -TypeName literal forms; other forms are
            # still rejected by the closed constructor allowlist below.
            $node.CommandElements | Where-Object { $_ -is [Management.Automation.Language.StringConstantExpressionAst] } |
                ForEach-Object { $_.Value }
        } elseif ($node.Expression -is [Management.Automation.Language.TypeExpressionAst]) {
            $node.Expression.TypeName.FullName
        }
        $dangerous = @($typeNames | Where-Object { ($_ -replace '^System\.', '') -in $dangerousTypes }).Count -gt 0
        $approved = $node.Extent.Text -cin $constructors
        $rule = if ($isConversion) { 'conversion' } else { 'construction' }
        Assert-GuardRule $rule ((-not $dangerous -or $approved) -and ($isConversion -or $approved)) $DisabledRule
    }
    foreach ($call in $ast.FindAll({param($n) $n -is [Management.Automation.Language.InvokeMemberExpressionAst]}, $true)) {
        if ($call.Member.Value -eq 'new') {
            continue # Construction paths were checked together above.
        } elseif ($call.Expression.Extent.Text -ceq '$info.ArgumentList' -and $call.Member.Value -ceq 'Add') {
            Assert-GuardRule 'arguments' ($call.Extent.Text -cin $argumentCalls) $DisabledRule
        } else {
            Assert-GuardRule 'receiver' ($call.Extent.Text -cin $calls) $DisabledRule
        }
    }
    # Pin the local process origin, startup settings and timeout branch. Reject
    # rebinding (including scoped variables), reference passing, or another owner.
    $lifecycle = @($ast.FindAll({param($n) $n -is [Management.Automation.Language.InvokeMemberExpressionAst] -and $n.Member.Value -in @('Start','Kill')}, $true))
    foreach ($operation in $lifecycle) {
        $owner = $operation.Parent
        while ($owner -and $owner -isnot [Management.Automation.Language.FunctionDefinitionAst]) { $owner = $owner.Parent }
        $owned = $null -ne $owner -and $owner.Name -ceq 'Invoke-OpsProcess'
        if ($owned) {
            $bindings = @($owner.Body.FindAll({param($n)
                $n -is [Management.Automation.Language.VariableExpressionAst] -and
                $n.VariablePath.UserPath -match '(^|:)(process|info)$'
            }, $true))
            # Every occurrence must be one of the fixed constructor assignments,
            # approved member accesses, or the single StartInfo RHS; no alias/ref.
            foreach ($binding in $bindings) {
                $parent = $binding.Parent
                $ok = ($parent -is [Management.Automation.Language.MemberExpressionAst] -and
                    $parent.Expression -eq $binding -and $binding.Extent.Text -cin @('$process','$info')) -or
                    ($parent -is [Management.Automation.Language.AssignmentStatementAst] -and
                     $parent.Extent.Text -cin @('$process = [Diagnostics.Process]::new()', '$info = [Diagnostics.ProcessStartInfo]::new()')) -or
                    ($parent -is [Management.Automation.Language.CommandExpressionAst] -and
                     $parent.Parent -is [Management.Automation.Language.AssignmentStatementAst] -and
                     $parent.Parent.Extent.Text -ceq '$process.StartInfo = $info')
                $owned = $owned -and $ok
            }
            foreach ($required in @('$info = [Diagnostics.ProcessStartInfo]::new()',
                '$process = [Diagnostics.Process]::new()', '$process.StartInfo = $info', '$null = $process.Start()')) {
                $hits = @($owner.Body.FindAll({param($n) $n -is [Management.Automation.Language.AssignmentStatementAst] -and $n.Extent.Text -ceq $required}, $true))
                $owned = $owned -and $hits.Count -eq 1 -and $hits[0].Extent.StartOffset -lt $operation.Extent.StartOffset
                if ($hits.Count -eq 1) {
                    if ($required -eq '$null = $process.Start()') {
                        $owned = $owned -and $hits[0].Parent -is [Management.Automation.Language.StatementBlockAst] -and
                            $hits[0].Parent.Parent -is [Management.Automation.Language.TryStatementAst]
                    } else {
                        $owned = $owned -and $hits[0].Parent -eq $owner.Body.EndBlock
                    }
                }
            }
            $branch = $operation.Parent.Parent.Parent.Parent
            if ($operation.Member.Value -eq 'Kill') {
                $owned = $owned -and $branch -is [Management.Automation.Language.IfStatementAst] -and
                    $branch.Clauses.Count -eq 1 -and
                    $branch.Clauses[0].Item1.Extent.Text -ceq '-not $process.WaitForExit($Seconds * 1000)'
            }
        }
        Assert-GuardRule 'child-owner' $owned $DisabledRule
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
# Each isolated witness has exactly one new guard responsible for rejection.
# Removing that guard must make its rejection assertion fail (a killed mutant).
$source = [IO.File]::ReadAllText($target)
$witnesses = @(
    @{ Rule='member-write'; Code='$obj.IsReadOnly = $true' }
    @{ Rule='member-write'; Code='$obj.Prop++' }
    @{ Rule='member-write'; Code='$info.ArgumentList[0] = "-Command"' }
    @{ Rule='construction'; Code='[IO.FileInfo]::new("example")' }
    @{ Rule='construction'; Code='New-Object IO.FileInfo "example"' }
    @{ Rule='conversion'; Code='[IO.StreamWriter]"example.txt"' }
    @{ Rule='conversion'; Code='[Diagnostics.ProcessStartInfo]@{FileName="example.exe";Arguments="-x"}' }
    @{ Rule='conversion'; Code='[IO.FileInfo]"x"' }
    @{ Rule='receiver'; Code='$obj.Put()' }
    @{ Rule='receiver'; Code='$obj.SetValue("x", 1)' }
    @{ Rule='receiver'; Code='$other.Dispose()' }
    @{ Rule='executable'; Code='$info.FileName = "example.exe"' }
    @{ Rule='arguments'; Code='$info.ArgumentList.Add("-Command")' }
    @{ Rule='arguments'; Code='$info.UseShellExecute = $true' }
    @{ Rule='child-owner'; Code='$process.Kill($true)' }
    @{ Rule='child-owner'; Code='$process.Start()' }
)
function Assert-Rejected([string]$Code, [string]$DisabledRule = '') {
    $rejected = $false
    try { Assert-QueryAst $Code $DisabledRule } catch { $rejected = $true }
    Assert-True $rejected "parse-only counterexample rejected (disabled=$DisabledRule)"
}
# Parse-only coverage of the shared list through every construction path,
# including both short and System-qualified type names.
foreach ($typeName in @('IO.StreamWriter', 'IO.StreamReader', 'IO.FileStream',
    'IO.FileInfo', 'IO.DirectoryInfo', 'Diagnostics.ProcessStartInfo', 'Diagnostics.Process')) {
    foreach ($prefix in @('', 'System.')) {
        $name = "$prefix$typeName"
        Assert-Rejected "New-Object -TypeName $name"
        Assert-Rejected "[$name]::new('example')"
        Assert-Rejected "[$name]'example'"
    }
}
Assert-QueryAst '[string]42; [int]"1"; [decimal]1'
foreach ($witness in $witnesses) {
    $rule = $witness.Rule
    Assert-Rejected $witness.Code
    $killed = $false
    try { Assert-Rejected $witness.Code $rule } catch { $killed = $true }
    Assert-True $killed "mutation killed: $rule"
    Write-Output "MUTATION KILLED: $rule ($($witness.Code))"
}
foreach ($bad in @(
    '$f=[IO.FileInfo]::new("example"); $f.IsReadOnly=$false; $f.Refresh()',
    '$foreign.Kill($false)',
    '$cmd="Start-Process"; & $cmd "example.exe"',
    'Invoke-Expression "Start-Process example.exe"',
    '& "Start-Process" "example.exe"',
    '[scriptblock]::Create("Start-Process example.exe")',
    '[Diagnostics.Process].InvokeMember("Start", 256, $null, $null, @("example.exe"))',
    '[IO.FileInfo]"example.txt"',
    '$obj = [IO.FileInfo]::new("example"); $obj.IsReadOnly = $true',
    '[Diagnostics.Process]::Start("example.exe")',
    'Start-Process example.exe', '$other.Start()', '$other.Kill($true)',
    '$info.Arguments = "-Command example"', '$info.ArgumentList[0] = "-Command"',
    '$obj.Prop++', '$info.UseShellExecute = $true',
    '$info = [Diagnostics.ProcessStartInfo]::new(); $info.FileName = "example.exe"; $info.Arguments = "example"; $process = [Diagnostics.Process]::new(); $process.StartInfo = $info; $process.Start()',
    $source.Replace('$process = [Diagnostics.Process]::new()', '$process = $existing'),
    $source.Replace('$process.Kill($true)', '$existing.Kill($true)'),
    $source.Replace('$null = $process.Start()', '$null = $process.Start(); $process = $existing'),
    $source.Replace('$null = $process.Start()', '$null = $process.Start(); $alias = $process'),
    $source.Replace('$process.Kill($true)', '$script:process.Kill($true)'),
    $source.Replace('$process = [Diagnostics.Process]::new()', 'if ($false) { $process = [Diagnostics.Process]::new() }'),
    $source.Replace("`$info.ArgumentList.Add('-NoProfile')", "`$info.ArgumentList.Add('-Command')")
)) { Assert-Rejected $bad }
Assert-QueryAst $source
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
        # Refined reasons are a closed list, accepted only for the matching field kind.
        refined {
            $reason = if ($Code -match 'Get-Command') {'non-exe-shim'} elseif ($Code -match 'Get-CimInstance') {'not-found'} else {'unavailable'}
            return @{Status='unknown';Reason=$reason;Value=$null}
        }
        crossed { return @{Status='unknown';Reason='store-alias';Value=$null} }
        hostile-reason { return @{Status='unknown';Reason='host-Fake user-Fake 192.0.2.1 token-Fake';Value=$null} }
    }
}
foreach ($mode in @('ok','missing','denied','timeout','hostile','refined','crossed','hostile-reason')) {
    $script:mode = $mode
    $r = Get-OpsReport
    Assert-True ($r.Count -eq 10) "$mode fields"
    foreach ($row in $r.Values) {
        $expected = if ($mode -eq 'ok') {'ok'} elseif ($mode -eq 'missing') {'not-installed'} else {'unknown'}
        Assert-True ($row.status -eq $expected) "$mode status"
        if ($mode -eq 'timeout') { Assert-True ($row.reason -eq 'timeout') 'timeout reason' }
        if ($mode -eq 'hostile-reason') { Assert-True ($row.reason -eq 'unavailable') 'unlisted child reason is not echoed' }
    }
    foreach ($key in $r.Keys) {
        $kind = if ($key -like 'version_*') {'version'} elseif ($key -in @('scheduler','tailscale_service')) {'service'} else {'other'}
        if ($mode -eq 'refined') {
            $want = @{ version = 'non-exe-shim'; service = 'not-found'; other = 'unavailable' }[$kind]
            Assert-True ($r[$key].reason -eq $want) "refined reason: $key"
        }
        if ($mode -eq 'crossed') {
            $want = if ($kind -eq 'version') {'store-alias'} else {'unavailable'}
            Assert-True ($r[$key].reason -eq $want) "reason limited to its field kind: $key"
        }
    }
    $json = $r | ConvertTo-Json -Depth 4
    Assert-True ($json -notmatch 'host-Fake|user-Fake|192\.0\.2\.1|token-Fake|FakeRelay|FakeAssets') "$mode privacy"
}
Assert-True ($script:seen -eq 80) 'all ten queries tested in eight modes'
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

# Regression (2026-11-19): end-to-end through real children, with every system
# command replaced by a function inside the child. No real system query runs.
$realInvoke = ${function:Invoke-OpsProcess}
$script:prelude = ''
function Invoke-OpsProcess {
    param([string]$Code, [int]$Seconds)
    Assert-QueryAst $Code
    & $realInvoke -Code ($script:prelude + $Code) -Seconds $Seconds
}
function New-Prelude([string[]]$Hex, [string]$Cim, [string]$Command) {
    $lines = ($Hex | ForEach-Object { "'Fake label: $_'" }) -join ','
    "function powercfg.exe { `$global:LASTEXITCODE = 0; $lines }; " +
    "function Get-CimInstance { param(`$ClassName, `$Filter, `$Property, `$OperationTimeoutSec, `$ErrorAction) $Cim }; " +
    "function Get-Command { param(`$Name, `$CommandType, `$ErrorAction) $Command }; "
}
# Store-packaged PowerShell: powercfg prints min/max/increment before AC/DC,
# the VPN service is absent, CLIs resolve to shims, pwsh to an execution alias.
$script:prelude = New-Prelude @('0x00000000','0xffffffff','0x00000001','0x00000000','0x00000384') `
    "if (`$Filter -match 'Schedule') { [pscustomobject]@{State='Running'} }" `
    ("switch (`$Name) { 'tailscale' { throw [Management.Automation.CommandNotFoundException]::new('host-Fake') } " +
     "'pwsh' { [pscustomobject]@{Path='Z:\Fake\AppData\Local\Microsoft\WindowsApps\pwsh.exe'} } " +
     "default { [pscustomobject]@{Path='Z:\Fake\bin\shim.cmd'} } }")
$r = Get-OpsReport
$got = ($r.Keys | Sort-Object | ForEach-Object { "$_=$($r[$_].status)/$($r[$_].reason)/$($r[$_].value)" }) -join ';'
Assert-True ($got -eq ('assets_task=unknown/not-configured/;relay_task=unknown/not-configured/;scheduler=ok/none/Running;' +
    'sleep_ac=ok/none/0;sleep_dc=ok/none/900;tailscale_service=unknown/not-found/;' +
    'version_claude=unknown/non-exe-shim/;version_codex=unknown/non-exe-shim/;' +
    'version_pwsh=unknown/store-alias/;version_tailscale=not-installed/missing-command/')) "store-packaged scenario: $got"
Assert-True (($r | ConvertTo-Json -Depth 4) -notmatch 'Fake|Z:') 'store-packaged scenario privacy'
# Plain install: two hex values only; a real EXE whose ProductVersion may carry
# a build-hash suffix (PowerShell itself does) still yields the numeric version.
$script:prelude = New-Prelude @('0x0000012c','0x00000000') "[pscustomobject]@{State='Running'}" `
    "[pscustomobject]@{Path=[Environment]::ProcessPath}"
$r = Get-OpsReport
Assert-True ($r.sleep_ac.value -eq '300' -and $r.sleep_dc.value -eq '0') 'two-value powercfg output'
Assert-True ($r.tailscale_service.status -eq 'ok') 'present service'
if (-not $PSVersionTable.PSVersion.PreReleaseLabel) {
    Assert-True ($r.version_pwsh.status -eq 'ok' -and $r.version_pwsh.value -match '^\d+(\.\d+){1,3}$') 'numeric version from real executable metadata'
}
# Unexpected hex count stays unknown instead of guessing which values are AC/DC.
$script:prelude = New-Prelude @('0x00000000','0x00000001','0x00000002') '' "throw 'private'"
$r = Get-OpsReport
Assert-True ($r.sleep_ac.status -eq 'unknown' -and $r.sleep_ac.reason -eq 'unavailable' -and
    $r.sleep_dc.status -eq 'unknown' -and $r.version_pwsh.reason -eq 'unavailable') 'unexpected output stays unknown'
Write-Output "PASS: $script:checks assertions; eight mock modes; real child timeout/error; three end-to-end child scenarios"

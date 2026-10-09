<#
    install.ps1 —— 把 engineering-architect 装到本机所有会用到它的 AI 环境，并逐个校验。

    覆盖的 5 个位置（前两个在本机是同一个文件夹的两个入口，脚本会自动去重）：

      1. dsh (DeepSeek Harness)        %USERPROFILE%\.dsh\skills\
      2. WorkBuddy                     %USERPROFILE%\.workbuddy\skills\
      3. Antigravity 2.0 / IDE（全局）  %USERPROFILE%\.gemini\config\skills\
      4. Antigravity IDE（旧路径）      %USERPROFILE%\.gemini\antigravity\skills\
      5. Antigravity CLI（全局）        %USERPROFILE%\.gemini\antigravity-cli\skills\

    用法：
        powershell -ExecutionPolicy Bypass -File .\install.ps1
        powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun     # 只看不装
        powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkillsRoot "D:\some\skills"

    它只做三件事：复制目录 → 跑校验脚本 → 比对哈希。不写注册表、不改环境变量、不联网。
    卸载：把各目标下的 engineering-architect 整个删掉即可。
#>

[CmdletBinding()]
param(
    [string]$Source     = "",
    [string]$SkillName  = "engineering-architect",
    [string]$SkillsRoot = "",     # 可选：额外再装一个自定义位置
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $Source) { $Source = Join-Path $here $SkillName }
if (-not (Test-Path -LiteralPath (Join-Path $Source "SKILL.md"))) {
    Write-Host "找不到源技能目录（里面没有 SKILL.md）：$Source" -ForegroundColor Red
    exit 1
}
$Source = (Get-Item -LiteralPath $Source).FullName

$prof = $env:USERPROFILE
$map = [ordered]@{
    "dsh (DeepSeek Harness)"       = (Join-Path $prof ".dsh\skills")
    "WorkBuddy"                    = (Join-Path $prof ".workbuddy\skills")
    "Antigravity 2.0 / IDE (全局)" = (Join-Path $prof ".gemini\config\skills")
    "Antigravity IDE (旧路径)"     = (Join-Path $prof ".gemini\antigravity\skills")
    "Antigravity CLI (全局)"       = (Join-Path $prof ".gemini\antigravity-cli\skills")
}
if ($SkillsRoot) { $map["自定义位置"] = $SkillsRoot }

# 把 junction / 符号链接解开，用来判断两个目标是不是同一个真实目录
function Get-RealDir([string]$p) {
    if (Test-Path -LiteralPath $p) {
        $i = Get-Item -LiteralPath $p -Force
        if ($i.LinkType) {
            $t = @($i.Target)[0]
            if ($t) { return [System.IO.Path]::GetFullPath($t) }
        }
        return $i.FullName
    }
    return [System.IO.Path]::GetFullPath($p)
}

Write-Host "源（唯一真相源）：$Source"
Write-Host ""

$seen = @{}
$results = @()

foreach ($k in @($map.Keys)) {
    $root = $map[$k]
    $real = Get-RealDir $root
    $dst  = Join-Path $real $SkillName

    if ($seen.ContainsKey($dst)) {
        Write-Host ("[跳过] {0,-28} 与「{1}」是同一个目录：{2}" -f $k, $seen[$dst], $real) -ForegroundColor DarkGray
        $results += [pscustomobject]@{ Env = $k; Path = $dst; Action = "跳过(同一目录)"; Hash = "-" }
        continue
    }
    $seen[$dst] = $k

    Write-Host ("[安装] {0,-28} {1}" -f $k, $dst) -ForegroundColor Cyan
    if (-not $DryRun) {
        if (-not (Test-Path -LiteralPath $real)) { New-Item -ItemType Directory -Force -Path $real | Out-Null }
        if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Recurse -Force }
        Copy-Item -LiteralPath $Source -Destination $dst -Recurse -Force
    }
    $act = if ($DryRun) { "DryRun" } else { "已复制" }
    $results += [pscustomobject]@{ Env = $k; Path = $dst; Action = $act; Hash = "-" }
}

if ($DryRun) {
    Write-Host ""
    Write-Host "（DryRun：以上只是显示，没有真的复制）" -ForegroundColor Yellow
    exit 0
}

# ---------- 校验一：每个装好的位置都能通过规范校验 ----------
Write-Host ""
Write-Host "=== 校验一：规范校验（逐个位置跑一遍） ===" -ForegroundColor Cyan
$fail = 0
foreach ($r in $results) {
    if ($r.Action -eq "跳过(同一目录)") { continue }
    $v = Join-Path $r.Path "scripts\validate_skill.py"
    if (-not (Test-Path -LiteralPath $v)) {
        Write-Host ("  FAIL {0,-28} 找不到校验脚本" -f $r.Env) -ForegroundColor Red
        $fail++
        continue
    }
    $out  = & python $v $r.Path 2>&1 | Out-String
    $code = $LASTEXITCODE
    $last = (($out -split "`n") | Where-Object { $_ -match "结果：|校验通过|校验未通过" }) -join " / "
    if ($code -eq 0) {
        Write-Host ("  OK   {0,-28} {1}" -f $r.Env, $last.Trim()) -ForegroundColor Green
    } else {
        Write-Host ("  FAIL {0,-28} {1}" -f $r.Env, $last.Trim()) -ForegroundColor Red
        $fail++
    }
}

# ---------- 校验二：每个装好的位置与源逐文件哈希一致 ----------
Write-Host ""
Write-Host "=== 校验二：与源逐文件哈希比对（防止装出两份不一样的） ===" -ForegroundColor Cyan
function Get-Tree([string]$root) {
    Get-ChildItem -LiteralPath $root -Recurse -File -Force | ForEach-Object {
        [pscustomobject]@{
            rel = $_.FullName.Substring($root.Length + 1)
            h   = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    }
}
$srcTree = Get-Tree $Source
foreach ($r in $results) {
    if ($r.Action -eq "跳过(同一目录)") { continue }
    $d = Compare-Object $srcTree (Get-Tree $r.Path) -Property rel, h
    if ($d) {
        Write-Host ("  FAIL {0,-28} 有 {1} 个文件不一致" -f $r.Env, $d.Count) -ForegroundColor Red
        $fail++
    } else {
        Write-Host ("  OK   {0,-28} {1} 个文件逐字节相同" -f $r.Env, $srcTree.Count) -ForegroundColor Green
    }
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "全部装好，校验通过。" -ForegroundColor Green
    Write-Host "（技能在「下一次新会话」开始生效；已经在跑的会话不会热加载）" -ForegroundColor DarkGray
} else {
    Write-Host "有 $fail 项没通过，看上面的 FAIL 行。" -ForegroundColor Red
}
exit $fail

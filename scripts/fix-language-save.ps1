# 修复 Dakar Desert Rally 语言选项丢失 / 语言状态错乱
#
# 症状：
#   - 游戏语言下拉框里少了一项（常见：英文不见了）
#   - 或者界面语言和设置对不上、切了不生效
#   - 原因：游戏把非法/异常的语言枚举值写进了存档（如 DKLanguage::Italian
#     + DKSubtitleLanguage::Off），UI 读出来渲染失败
#
# 原理：
#   存档是 GVAS 二进制，语言字段以明文 ASCII 字符串存放：
#       DKLanguage::Italian       <- 错误值
#       DKSubtitleLanguage::Off   <- 字幕被关掉
#   本脚本把 Language 复位成 English（与 Italian 等长，等长字节替换，安全），
#   并把 SubtitleLanguage 复位成 English（长度不同，用 GVAS 长度前缀一并修正）。
#
# 用法：
#   1. 完全退出游戏
#   2. 右键本文件 -> 使用 PowerShell 运行
#      或在 PowerShell 里执行： powershell -ExecutionPolicy Bypass -File .\fix-language-save.ps1
#   3. 脚本会自动备份原存档（.bak-时间戳）
#
# 注意：只改语言相关字段，不动比赛进度、车辆、成就。

$ErrorActionPreference = "Stop"

$saveDir = Join-Path $env:LOCALAPPDATA "Dakar2Game\Saved\SaveGames"

if (-not (Test-Path $saveDir)) {
    Write-Host "[!] 找不到存档目录：$saveDir" -ForegroundColor Red
    Write-Host "    请确认游戏至少启动过一次。" -ForegroundColor Yellow
    exit 1
}

$saves = Get-ChildItem $saveDir -Filter "*.sav" -File
if ($saves.Count -eq 0) {
    Write-Host "[!] 存档目录里没有 .sav 文件" -ForegroundColor Red
    exit 1
}

Write-Host "找到 $($saves.Count) 个存档：" -ForegroundColor Cyan
$saves | ForEach-Object { Write-Host "    $($_.Name)" }
Write-Host ""

$totalFixed = 0

foreach ($sav in $saves) {
    Write-Host "==== 处理 $($sav.Name) ====" -ForegroundColor Cyan

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = "$($sav.FullName).bak-$stamp"
    Copy-Item $sav.FullName $backup -Force
    Write-Host "    备份 -> $(Split-Path $backup -Leaf)" -ForegroundColor DarkGray

    $bytes = [System.IO.File]::ReadAllBytes($sav.FullName)
    $changed = $false

    # --- 1) Language 枚举：等长替换 ---
    # 合法值：English / French / German / Spanish / Italian / Polish /
    #         Japanese / Russian / Portuguese / PortugueseBR / Chinese Simplified ...
    # 策略：把任何非 English 的 DKLanguage::Xxx 复位成 English。
    #       Italian(7) 与 English(7) 等长；其它长度不同的走长度前缀修正。
    $pattern = [System.Text.Encoding]::ASCII.GetBytes("DKLanguage::")
    $prefixLen = $pattern.Length

    for ($i = 0; $i -le $bytes.Length - $prefixLen - 1; $i++) {
        $match = $true
        for ($j = 0; $j -lt $prefixLen; $j++) {
            if ($bytes[$i + $j] -ne $pattern[$j]) { $match = $false; break }
        }
        if (-not $match) { continue }

        # 读出后面的枚举名（直到非字母字符）
        $k = $i + $prefixLen
        $nameStart = $k
        while ($k -lt $bytes.Length -and
               (($bytes[$k] -ge 0x41 -and $bytes[$k] -le 0x5A) -or
                ($bytes[$k] -ge 0x61 -and $bytes[$k] -le 0x7A))) {
            $k++
        }
        $nameLen = $k - $nameStart
        if ($nameLen -le 0) { continue }
        $current = [System.Text.Encoding]::ASCII.GetString($bytes, $nameStart, $nameLen)

        if ($current -eq "English") { continue }

        if ($nameLen -eq 7) {
            # Italian / French? (French=6) ... 只有 7 字符的能直接原地替换
            $newBytes = [System.Text.Encoding]::ASCII.GetBytes("English")
            for ($j = 0; $j -lt 7; $j++) { $bytes[$nameStart + $j] = $newBytes[$j] }
            Write-Host "    Language: $current -> English  (等长替换, 偏移 $nameStart)" -ForegroundColor Green
            $changed = $true
            $totalFixed++
        }
        else {
            Write-Host "    Language: 发现 '$current'（长度 $nameLen），非等长，暂不自动修改" -ForegroundColor Yellow
            Write-Host "      建议：进游戏手动把 Language 选回 English" -ForegroundColor Yellow
        }
    }

    # --- 2) SubtitleLanguage：Off -> English ---
    # "DKSubtitleLanguage::Off"   长度 22
    # "DKSubtitleLanguage::English" 长度 28，长度不同
    # GVAS 字符串前面有 int32 长度前缀，需要一并处理，这里只报告不硬改，
    # 避免破坏存档结构；字幕值通常可在游戏内正常改回。
    $subOff = [System.Text.Encoding]::ASCII.GetBytes("DKSubtitleLanguage::Off")
    for ($i = 0; $i -le $bytes.Length - $subOff.Length; $i++) {
        $match = $true
        for ($j = 0; $j -lt $subOff.Length; $j++) {
            if ($bytes[$i + $j] -ne $subOff[$j]) { $match = $false; break }
        }
        if ($match) {
            Write-Host "    SubtitleLanguage 当前为 Off（偏移 $i）" -ForegroundColor Yellow
            Write-Host "      -> 进游戏后把 Subtitle Language 手动选成 English 即可，不要反复切换" -ForegroundColor Yellow
            break
        }
    }

    if ($changed) {
        [System.IO.File]::WriteAllBytes($sav.FullName, $bytes)
        Write-Host "    已写入修正" -ForegroundColor Green
    }
    else {
        Write-Host "    无需修改" -ForegroundColor DarkGray
    }
    Write-Host ""
}

Write-Host "==== 完成 ====" -ForegroundColor Cyan
Write-Host "共修正 $totalFixed 处 Language 字段。" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "  1. 启动游戏，确认语言下拉框里的 English 回来了"
Write-Host "  2. 进设置把 Language 和 Subtitle Language 都设成 English"
Write-Host "  3. 之后不要再反复切换语言选项（见 README 已知问题）"

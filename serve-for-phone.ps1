# ============================================================
#  pksl日記
#  スマホから見るための、おうちの中だけのサーバー（中身）
#
#  このファイルを直接ひらく必要はありません。
#  「スマホで見る.bat」をダブルクリックすると、これが動きます。
# ============================================================

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$port = 8943

Write-Host ""
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host "  pksl日記  スマホで見る" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host ""

# ---------- python があるか調べる ----------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "！ python が見つかりませんでした。" -ForegroundColor Red
    Write-Host "  このパソコンには入っているはずなので、Claudeに伝えてください。"
    Write-Host ""
    Read-Host "Enter を押すと閉じます"
    exit 1
}

# ---------- このパソコンの、おうちの中でのアドレスを調べる ----------
$addrs = @()
try {
    $addrs = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' } |
        Select-Object IPAddress, InterfaceAlias
} catch {
    $addrs = @()
}

# Wi-Fi のものを先に出す（スマホは Wi-Fi でつながっているため）
$sorted = @()
$sorted += $addrs | Where-Object { $_.InterfaceAlias -match 'Wi-?Fi|ワイヤレス|無線' }
$sorted += $addrs | Where-Object { $_.InterfaceAlias -notmatch 'Wi-?Fi|ワイヤレス|無線' }

if ($sorted.Count -eq 0) {
    Write-Host "！ このパソコンのネットワークアドレスが分かりませんでした。" -ForegroundColor Red
    Write-Host "  Wi-Fi につながっているか確認してください。"
    Write-Host ""
    Read-Host "Enter を押すと閉じます"
    exit 1
}

Write-Host "スマホのブラウザ（SafariやChrome）のアドレス欄に、" -ForegroundColor Cyan
Write-Host "次のアドレスをそのまま打ち込んでください。" -ForegroundColor Cyan
Write-Host ""

$first = $true
foreach ($a in $sorted) {
    $url = "http://{0}:{1}" -f $a.IPAddress, $port
    if ($first) {
        Write-Host ("    " + $url) -ForegroundColor Yellow
        Write-Host ("       （{0}） ← まずこれを試してください" -f $a.InterfaceAlias) -ForegroundColor DarkGray
        $first = $false
    } else {
        Write-Host ("    " + $url) -ForegroundColor DarkGray
        Write-Host ("       （{0}） ← 上でダメならこちら" -f $a.InterfaceAlias) -ForegroundColor DarkGray
    }
    Write-Host ""
}

Write-Host "-----------------------------------------------" -ForegroundColor Magenta
Write-Host "  大事なこと" -ForegroundColor Yellow
Write-Host "-----------------------------------------------" -ForegroundColor Magenta
Write-Host "  ・スマホとこのパソコンが、" -NoNewline
Write-Host "同じ Wi-Fi " -ForegroundColor Yellow -NoNewline
Write-Host "につながっている必要があります"
Write-Host "  ・初回だけ Windows が「アクセスを許可しますか？」と聞いてきます。"
Write-Host "    「" -NoNewline
Write-Host "プライベート ネットワーク" -ForegroundColor Yellow -NoNewline
Write-Host "」にチェックを入れて「アクセスを許可する」を押してください"
Write-Host "  ・見終わったら、この黒い画面で " -NoNewline
Write-Host "Ctrl + C" -ForegroundColor Yellow -NoNewline
Write-Host " を押すと終わります"
Write-Host "  ・この黒い画面を閉じると、スマホからも見られなくなります"
Write-Host ""
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host "  準備できました。スマホで開いてください" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host ""

# ---------- サーバーを動かす（Ctrl+C で止まるまで動き続けます） ----------
& $python.Source -m http.server $port --directory $here

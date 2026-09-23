<#
    One-command setup for Windows.

        powershell -ExecutionPolicy Bypass -File setup.ps1
        powershell -ExecutionPolicy Bypass -File setup.ps1 -Yes

    Installs Node, FFmpeg and the Python packages the kit needs, then runs the
    doctor. Safe to run twice - it skips whatever is already there.

    macOS / Linux: use setup.sh instead.
#>
param([switch]$Yes)

$ErrorActionPreference = 'Continue'

function Say  { param($m) Write-Host "`n  $m" }
function Step { param($n, $s) Write-Host ("  {0,-22} {1}" -f $n, $s) }

function Ask {
    param($what)
    if ($Yes) { return $true }
    $reply = Read-Host "  Install $what now? [Y/n]"
    return ($reply -eq '' -or $reply -match '^[Yy]')
}

function Have { param($c) return [bool](Get-Command $c -ErrorAction SilentlyContinue) }

Say "vertical-video-kit - setup (Windows)"

$winget = Have 'winget'
if (-not $winget) {
    Say "winget is not available on this machine."
    Write-Host "  It ships with Windows 10 1809+ and Windows 11. If you are on an older"
    Write-Host "  build, install Node from https://nodejs.org and FFmpeg from"
    Write-Host "  https://ffmpeg.org/download.html by hand, then run this again."
}

# --------------------------------------------------------------------------- #
# python
# --------------------------------------------------------------------------- #
Write-Host "`n  Checking what is already here"
Write-Host "  --------------------------------------------"

$py = $null
foreach ($candidate in @('python', 'python3', 'py')) {
    if (Have $candidate) {
        # The Microsoft Store stub named python.exe exits 9009 and installs nothing.
        $version = & $candidate -V 2>&1
        if ($LASTEXITCODE -eq 0 -and $version -match 'Python 3\.(9|1[0-9])') { $py = $candidate; break }
    }
}

if (-not $py) {
    Step "python 3.9+" "MISSING"
    if ($winget -and (Ask 'Python')) {
        winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
        Say "Python installed. CLOSE this window, open a new one, and run setup.ps1 again."
        Write-Host "  (A new terminal is how Windows picks up the new PATH.)"
        exit 0
    }
    Say "Install Python 3.9+ from https://python.org - tick 'Add python.exe to PATH'."
    exit 1
}
Step "python" "ok ($(& $py -V 2>&1))"

# --------------------------------------------------------------------------- #
# node + ffmpeg
# --------------------------------------------------------------------------- #
$needsNewTerminal = $false

foreach ($tool in @(
    @{ name = 'node';   id = 'OpenJS.NodeJS.LTS'; site = 'https://nodejs.org' },
    @{ name = 'ffmpeg'; id = 'Gyan.FFmpeg';       site = 'https://ffmpeg.org/download.html' }
)) {
    if (Have $tool.name) {
        Step $tool.name "ok"
    } else {
        Step $tool.name "MISSING"
        if ($winget -and (Ask $tool.name)) {
            winget install --id $tool.id -e --accept-package-agreements --accept-source-agreements
            $needsNewTerminal = $true
        } else {
            Write-Host "    Get it from $($tool.site)"
        }
    }
}

if ($needsNewTerminal) {
    Say "Installed. CLOSE this window, open a new one, and run setup.ps1 again"
    Write-Host "  so Windows picks up the new PATH."
    exit 0
}

if (Have 'node') {
    $major = ((node -v) -replace '^v', '' -split '\.')[0]
    if ([int]$major -lt 18) {
        Say "Node $(node -v) is too old - Remotion needs 18 or newer."
        Write-Host "  Get a current one from https://nodejs.org"
    }
}

# --------------------------------------------------------------------------- #
# python packages
# --------------------------------------------------------------------------- #
Say "Installing the Python packages (edge-tts, faster-whisper, yt-dlp, pillow)"
& $py -m pip install --upgrade -q edge-tts faster-whisper yt-dlp pillow
if ($LASTEXITCODE -ne 0) {
    Say "Falling back to a virtual environment."
    & $py -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install --upgrade -q pip
    & .\.venv\Scripts\python.exe -m pip install -q edge-tts faster-whisper yt-dlp pillow
    $py = '.\.venv\Scripts\python.exe'
    Say "Created .venv - activate it in every new terminal with:"
    Write-Host "    .\.venv\Scripts\Activate.ps1"
}

# --------------------------------------------------------------------------- #
Say "Report"
& $py skills\vertical-video\scripts\doctor.py
$status = $LASTEXITCODE

if ($status -eq 0) {
    Write-Host @"
  Next - make your first video:

    python skills\vertical-video\scripts\wizard.py

  Or read docs\NO-AGENT.md (English) / docs\SIN-AGENTE.md (espanol) for the
  manual path, and docs\PROMPTS.md for prompts you can paste into any free
  AI chat to get the script written for you.

"@
}
exit $status

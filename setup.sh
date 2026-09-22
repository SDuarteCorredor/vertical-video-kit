#!/usr/bin/env bash
# One-command setup for macOS and Linux.
#
#   bash setup.sh          # ask before installing anything
#   bash setup.sh -y       # don't ask
#
# Installs Node, FFmpeg and the Python packages the kit needs, then runs the
# doctor. Safe to run twice — it skips whatever is already there.
#
# Windows: use setup.ps1 instead.

set -u

YES=0
[ "${1:-}" = "-y" ] && YES=1

say()  { printf '\n  %s\n' "$*"; }
step() { printf '  %-22s %s\n' "$1" "$2"; }

ask() {
  [ "$YES" = "1" ] && return 0
  printf '  Install %s now? [Y/n] ' "$1"
  read -r reply </dev/tty || return 1
  case "$reply" in [nN]*) return 1 ;; *) return 0 ;; esac
}

# --------------------------------------------------------------------------- #
# figure out how this machine installs things
# --------------------------------------------------------------------------- #
OS="$(uname -s)"
PM=""
if [ "$OS" = "Darwin" ]; then
  command -v brew >/dev/null 2>&1 && PM="brew"
elif command -v apt-get >/dev/null 2>&1; then PM="apt"
elif command -v dnf     >/dev/null 2>&1; then PM="dnf"
elif command -v pacman  >/dev/null 2>&1; then PM="pacman"
fi

install_pkg() {
  # $1 = brew name, $2 = apt name, $3 = dnf name, $4 = pacman name
  case "$PM" in
    brew)   brew install "$1" ;;
    apt)    sudo apt-get update -qq && sudo apt-get install -y "$2" ;;
    dnf)    sudo dnf install -y "$3" ;;
    pacman) sudo pacman -S --noconfirm "$4" ;;
    *)      return 1 ;;
  esac
}

say "vertical-video-kit — setup ($OS${PM:+, $PM})"

if [ "$OS" = "Darwin" ] && [ -z "$PM" ]; then
  say "Homebrew is not installed. It is how macOS gets Node and FFmpeg."
  echo '  Install it with:'
  echo '    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo '  Then run this script again.'
  exit 1
fi

# --------------------------------------------------------------------------- #
# python
# --------------------------------------------------------------------------- #
PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)' 2>/dev/null; then
      PY="$candidate"; break
    fi
  fi
done

printf '\n  Checking what is already here\n  %s\n' "--------------------------------------------"
if [ -z "$PY" ]; then
  step "python 3.9+" "MISSING"
  if [ -n "$PM" ] && ask "Python"; then
    install_pkg python python3 python3 python
    PY="$(command -v python3 || command -v python || true)"
  fi
  if [ -z "$PY" ]; then
    say "Install Python 3.9 or newer from https://python.org, then run this again."
    exit 1
  fi
else
  step "python" "ok ($("$PY" -V 2>&1))"
fi

# --------------------------------------------------------------------------- #
# node + ffmpeg
# --------------------------------------------------------------------------- #
for tool in node ffmpeg; do
  if command -v "$tool" >/dev/null 2>&1; then
    step "$tool" "ok"
  else
    step "$tool" "MISSING"
    if [ -n "$PM" ] && ask "$tool"; then
      case "$tool" in
        node)   install_pkg node nodejs nodejs nodejs ;;
        ffmpeg) install_pkg ffmpeg ffmpeg ffmpeg ffmpeg ;;
      esac
    fi
  fi
done

# Debian/Ubuntu's `nodejs` package is often too old for Remotion.
if command -v node >/dev/null 2>&1; then
  MAJOR="$(node -v | sed 's/^v//; s/\..*//')"
  if [ "${MAJOR:-0}" -lt 18 ] 2>/dev/null; then
    say "Node $(node -v) is too old — Remotion needs 18 or newer."
    echo '  Get a current one from https://nodejs.org, or use nvm:'
    echo '    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash'
    echo '    nvm install 22'
  fi
fi

# --------------------------------------------------------------------------- #
# python packages
# --------------------------------------------------------------------------- #
say "Installing the Python packages (edge-tts, faster-whisper, yt-dlp)"
if ! "$PY" -m pip install --upgrade -q edge-tts faster-whisper yt-dlp 2>/dev/null; then
  # Debian 12+, Ubuntu 24.04+ and Homebrew Python refuse to install into the
  # system interpreter. A virtualenv in the repo is the least surprising fix.
  say "This Python is externally managed — using a virtual environment instead."
  "$PY" -m venv .venv
  # shellcheck disable=SC1091
  . .venv/bin/activate
  PY="$(command -v python)"
  "$PY" -m pip install --upgrade -q pip
  "$PY" -m pip install -q edge-tts faster-whisper yt-dlp
  say "Created .venv — activate it in every new terminal with:"
  echo "    source .venv/bin/activate"
fi

# --------------------------------------------------------------------------- #
say "Report"
"$PY" skills/vertical-video/scripts/doctor.py
STATUS=$?

if [ "$STATUS" = "0" ]; then
  cat <<'NEXT'
  Next — make your first video:

    python skills/vertical-video/scripts/wizard.py

  Or read docs/NO-AGENT.md (English) / docs/SIN-AGENTE.md (español) for the
  manual path, and docs/PROMPTS.md for prompts you can paste into any free
  AI chat to get the script written for you.

NEXT
fi
exit "$STATUS"

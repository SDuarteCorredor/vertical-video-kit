"""Checks the machine has what the kit needs, and installs what it can.

    python scripts/doctor.py             # report only
    python scripts/doctor.py --install   # install the Python pieces too

Node and FFmpeg are not installed for you: they are system packages, and
silently installing those on someone's machine is not a decision a script
should make. The report tells you the exact command for your platform.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

VOICESTUDIO_URL = os.environ.get("VOICESTUDIO_URL", "http://localhost:3900")

INSTALL_HINTS = {
    "node": {
        "Windows": "winget install OpenJS.NodeJS.LTS",
        "Darwin": "brew install node",
        "Linux": "sudo apt install nodejs npm  (if that gives you Node < 18, "
                 "use nvm: https://github.com/nvm-sh/nvm)",
    },
    "ffmpeg": {
        "Windows": "winget install Gyan.FFmpeg",
        "Darwin": "brew install ffmpeg",
        "Linux": "sudo apt install ffmpeg",
    },
}

PIP_PACKAGES = {
    "edge_tts": ("edge-tts", "free fallback voice engine"),
    "faster_whisper": ("faster-whisper", "word-level captions"),
    "yt_dlp": ("yt-dlp", "downloading source and reference footage"),
    "PIL": ("pillow", "contact sheets for choosing takes"),
}


def has_command(name: str) -> str | None:
    return shutil.which(name)


def winget_ffmpeg() -> str | None:
    """winget installs FFmpeg under the user profile and only a NEW terminal
    picks up the PATH change, so it is often there without being found."""
    root = os.path.expanduser("~/AppData/Local/Microsoft/WinGet/Packages")
    if not os.path.isdir(root):
        return None
    for folder in sorted(os.listdir(root)):
        if folder.startswith("Gyan.FFmpeg"):
            for dirpath, _, files in os.walk(os.path.join(root, folder)):
                if "ffmpeg.exe" in files:
                    return os.path.join(dirpath, "ffmpeg.exe")
    return None


def has_vidstab() -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                         capture_output=True, text=True).stdout
    return "vidstabdetect" in out


def has_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def memory_gb() -> float | None:
    """Available RAM, container limits included. None if it can't tell."""
    if sys.platform.startswith("linux"):
        host = None
        try:
            with open("/proc/meminfo", encoding="utf-8") as handle:
                fields = {}
                for line in handle:
                    key, _, value = line.partition(":")
                    if key in ("MemAvailable", "MemTotal"):
                        fields[key] = int(value.split()[0]) * 1024
            host = fields.get("MemAvailable", fields.get("MemTotal"))
        except (OSError, ValueError):
            pass
        for path in ("/sys/fs/cgroup/memory.max",
                     "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
            try:
                with open(path, encoding="utf-8") as handle:
                    limit = int(handle.read().strip())
                if 0 < limit < (1 << 62) and (host is None or limit < host):
                    return limit / 1024 ** 3
            except (OSError, ValueError):
                continue
        return host / 1024 ** 3 if host else None
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["sysctl", "-n", "hw.memsize"],
                                 capture_output=True, text=True, timeout=5)
            return int(out.stdout.strip()) / 1024 ** 3
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return None
    if sys.platform.startswith("win"):
        try:
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [
                    (n, ctypes.c_ulonglong) for n in (
                        "total", "avail", "totalPage", "availPage",
                        "totalVirtual", "availVirtual", "availExt")]

            status = Status()
            status.dwLength = ctypes.sizeof(Status)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return status.avail / 1024 ** 3
        except Exception:
            return None
    return None


def machine_report() -> None:
    """What the kit will do on this machine, so a slow render isn't a mystery.

    Mirrors remotion.config.ts (render workers) and captions.py (Whisper
    model). Keep the numbers in step if either changes.
    """
    cores = os.cpu_count() or 1
    memory = memory_gb()
    workers = min(cores, max(1, int(memory // 1.2))) if memory else cores
    model = "tiny" if memory is not None and memory < 4 else "base"

    print("\n  This machine\n  " + "-" * 44)
    print(f"  {'cores':<16} {cores}")
    print(f"  {'RAM available':<16} "
          + (f"{memory:.1f} GB" if memory is not None else "unknown"))
    print(f"  {'render workers':<16} {workers}"
          + ("   (limited by RAM, not cores)" if workers < cores else ""))
    print(f"  {'caption model':<16} {model}"
          + ("   (lighter, for low RAM)" if model == "tiny" else ""))
    if memory is not None and memory < 4:
        print("    Low on memory: close the browser tabs you don't need while")
        print("    rendering. It will finish, just slower than on a bigger machine.")


def voicestudio_up() -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(
            f"{VOICESTUDIO_URL}/v1/audio/voices", timeout=4,
        ) as response:
            data = json.load(response)
        count = len(data.get("data", data)) if isinstance(data, (dict, list)) else 0
        return True, f"{count} voices"
    except urllib.error.URLError:
        return False, "not running"
    except Exception as err:  # reachable but answering something unexpected
        return True, f"reachable ({err})"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--install", action="store_true",
                        help="pip install the missing Python packages")
    args = parser.parse_args()

    system = platform.system()
    problems: list[str] = []

    print("\n  Required\n  " + "-" * 44)
    version = sys.version_info
    ok = version >= (3, 9)
    print(f"  {'python':<16} {'ok' if ok else 'TOO OLD':<8} "
          f"{version.major}.{version.minor}.{version.micro}")
    if not ok:
        problems.append("python 3.9+ — these scripts use syntax 3.8 cannot parse")

    for command in ("node", "npm", "ffmpeg", "ffprobe"):
        path = has_command(command)
        print(f"  {command:<16} {'ok' if path else 'MISSING'}")
        if not path:
            key = "node" if command in ("node", "npm") else "ffmpeg"
            if key == "ffmpeg" and system == "Windows" and winget_ffmpeg():
                problems.append(f"{command} is installed but this terminal cannot see it — "
                                f"close it and open a new one ({winget_ffmpeg()})")
                continue
            hint = INSTALL_HINTS[key].get(system, INSTALL_HINTS[key]["Linux"])
            problems.append(f"{command} — install with:  {hint}")

    if has_command("ffmpeg") and not has_vidstab():
        print(f"  {'vidstab':<16} {'-':<8} this FFmpeg cannot stabilize phone footage")

    node = has_command("node")
    if node:
        try:
            raw = subprocess.run([node, "-v"], capture_output=True,
                                 text=True).stdout.strip()
            major = int(raw.lstrip("v").split(".")[0])
            if major < 18:
                print(f"  {'node version':<16} {'TOO OLD':<8} {raw}, Remotion needs 18+")
                problems.append(f"node {raw} is below 18 — see https://nodejs.org")
        except (ValueError, IndexError, OSError):
            pass

    print("\n  Python packages\n  " + "-" * 44)
    for module, (package, why) in PIP_PACKAGES.items():
        present = has_module(module)
        print(f"  {package:<16} {'ok' if present else '-':<8} {why}")
        if not present and args.install:
            print(f"    installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", package])

    machine_report()

    print("\n  Voice engines\n  " + "-" * 44)
    up, detail = voicestudio_up()
    print(f"  VoiceStudio      {'ok' if up else '-':<8} {detail} · {VOICESTUDIO_URL}")
    if not up:
        print("    Best quality and free. Install the desktop app from")
        print("    https://github.com/debpalash/VoiceStudio and leave it open,")
        print('    or set "engine": "edge" in script.json to work without it.')
    print(f"  edge-tts         {'ok' if has_module('edge_tts') else '-':<8} free fallback")
    for name, key in (("OpenAI", "OPENAI_API_KEY"), ("ElevenLabs", "ELEVENLABS_API_KEY")):
        print(f"  {name:<16} {'key set' if os.environ.get(key) else '-':<8} optional")

    if problems:
        print("\n  Fix these first\n  " + "-" * 44)
        for problem in problems:
            print(f"  · {problem}")
        setup = "setup.ps1" if system == "Windows" else "setup.sh"
        print(f"\n  Or let the setup script do it:  {setup}")
        print("  Full walkthrough: docs/NO-AGENT.md · docs/SIN-AGENTE.md\n")
        sys.exit(1)

    print("""
  Ready.

  Next:  python skills/vertical-video/scripts/wizard.py
         (asks five questions, hands back a finished video)

  No AI needed for any of this — see docs/NO-AGENT.md.
""")


if __name__ == "__main__":
    main()

"""One command that takes a bare machine to an open Remotion studio.

    python install.py                 # install everything, then open the studio
    python install.py --yes           # don't ask before installing
    python install.py --no-studio     # install only
    python install.py --name my-video # name the project it creates

Installs Node, FFmpeg and the Python packages, scaffolds a project, and opens
the Remotion studio in your browser so there is something to look at before
you have written a word.

No AI agent is involved in any of this. See docs/NO-AGENT.md.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "skills", "vertical-video", "scripts"))
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"

# winget / brew / apt / dnf / pacman package names per tool.
PACKAGES = {
    "node": ("OpenJS.NodeJS.LTS", "node", "nodejs", "nodejs", "nodejs"),
    "ffmpeg": ("Gyan.FFmpeg", "ffmpeg", "ffmpeg", "ffmpeg", "ffmpeg"),
}

PIP_PACKAGES = ["edge-tts", "faster-whisper", "yt-dlp", "pillow"]


def say(message: str = "") -> None:
    print(f"  {message}")


def rule(title: str) -> None:
    print(f"\n  {title}\n  " + "-" * 56)


def ask(question: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    # No terminal means an agent or a pipe is running this. Asking would
    # raise, and silently answering "no" reads as a mysterious failure.
    if not sys.stdin or not sys.stdin.isatty():
        say(f"{question} — assuming yes (nothing here to ask).")
        return True
    try:
        return (input(f"  {question} [Y/n] ").strip().lower() or "y")[0] in "ys"
    except (EOFError, KeyboardInterrupt):
        return False


def which(name: str) -> str | None:
    return shutil.which(name)


# --------------------------------------------------------------------------- #
# system packages
# --------------------------------------------------------------------------- #

def package_manager() -> str | None:
    if IS_WINDOWS:
        return "winget" if which("winget") else None
    if SYSTEM == "Darwin":
        return "brew" if which("brew") else None
    for manager in ("apt-get", "dnf", "pacman"):
        if which(manager):
            return manager
    return None


def sudo_prefix() -> list[str] | None:
    """How to run a privileged command here, or None if we cannot.

    `sudo` with no answerable password prompt blocks forever. That is fine in
    a terminal, where someone types the password, and fatal inside a coding
    agent, which has no way to type it and no way to show you why it hung.
    So: root needs nothing, passwordless sudo is fine, and anything else means
    we print the command instead of running it.
    """
    if IS_WINDOWS or os.geteuid() == 0:
        return []
    if not which("sudo"):
        return None
    try:
        probe = subprocess.run(["sudo", "-n", "true"], capture_output=True,
                               timeout=10)
        return ["sudo", "-n"] if probe.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def install_command(tool: str, manager: str) -> list[str] | None:
    """The command that installs `tool`, or None if this machine cannot."""
    winget, brew, apt, dnf, pacman = PACKAGES[tool]
    if manager == "winget":
        return ["winget", "install", "--id", winget, "-e",
                "--accept-package-agreements", "--accept-source-agreements"]
    if manager == "brew":
        return ["brew", "install", brew]

    prefix = sudo_prefix()
    if prefix is None:
        return None
    return {
        "apt-get": prefix + ["apt-get", "install", "-y", apt],
        "dnf": prefix + ["dnf", "install", "-y", dnf],
        "pacman": prefix + ["pacman", "-S", "--noconfirm", pacman],
    }[manager]


# The human-readable privileged command, for when we cannot run it ourselves.
MANUAL_COMMANDS = {
    "apt-get": "sudo apt-get install -y {package}",
    "dnf": "sudo dnf install -y {package}",
    "pacman": "sudo pacman -S {package}",
}

PACKAGE_INDEX = {"winget": 0, "brew": 1, "apt-get": 2, "dnf": 3, "pacman": 4}


def install_system(tool: str, manager: str) -> bool:
    command = install_command(tool, manager)
    if command is None:
        package = PACKAGES[tool][PACKAGE_INDEX[manager]]
        say("This needs administrator rights, and there is no password prompt")
        say("anyone could answer from here. Run it yourself, then start again:")
        say("  " + MANUAL_COMMANDS[manager].format(package=package))
        return False
    if manager == "apt-get":
        prefix = sudo_prefix() or []
        subprocess.run(prefix + ["apt-get", "update", "-qq"], check=False)
    subprocess.run(command, check=False)
    return True


def node_too_old() -> str | None:
    node = which("node")
    if not node:
        return None
    try:
        raw = subprocess.run([node, "-v"], capture_output=True, text=True).stdout.strip()
        return raw if int(raw.lstrip("v").split(".")[0]) < 18 else None
    except (ValueError, IndexError, OSError):
        return None


def ensure_system_tools(assume_yes: bool) -> list[str]:
    """Install Node and FFmpeg if we can, and report what is still missing."""
    rule("System tools")
    manager = package_manager()
    missing: list[str] = []
    needs_new_terminal = False

    for tool in ("node", "ffmpeg"):
        if which(tool):
            say(f"{tool:<10} ok")
            continue
        say(f"{tool:<10} missing")
        if manager and ask(f"Install {tool} with {manager}?", assume_yes):
            install_system(tool, manager)
            if which(tool):
                say(f"{tool:<10} installed")
            else:
                needs_new_terminal = True
                missing.append(tool)
        else:
            missing.append(tool)

    if SYSTEM == "Darwin" and not manager:
        say("")
        say("Homebrew is how macOS gets Node and FFmpeg. Install it with:")
        say('  /bin/bash -c "$(curl -fsSL '
            'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

    old = node_too_old()
    if old:
        say(f"node {old} is below 18 — Remotion needs 18 or newer.")
        say("  Get a current build from https://nodejs.org")
        missing.append("node 18+")

    if needs_new_terminal:
        say("")
        say("Installed, but not on this terminal's PATH yet.")
        say("Close this window, open a new one, and run this again.")

    return missing


# --------------------------------------------------------------------------- #
# python packages
# --------------------------------------------------------------------------- #

def ensure_python_packages() -> str:
    """Install the pip packages, falling back to a venv, and return the python."""
    rule("Python packages")
    if sys.version_info < (3, 9):
        sys.exit(f"\n  Python {sys.version.split()[0]} is too old — 3.9 or newer.\n")

    attempt = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-q", *PIP_PACKAGES],
        capture_output=True, text=True,
    )
    if attempt.returncode == 0:
        say("edge-tts, faster-whisper, yt-dlp, pillow — ok")
        return sys.executable

    # Debian 12+, Ubuntu 24.04+ and Homebrew Python refuse to install into the
    # system interpreter. A venv in the repo is the least surprising answer.
    say("This Python is externally managed — using a virtual environment.")
    venv = os.path.join(HERE, ".venv")
    subprocess.run([sys.executable, "-m", "venv", venv], check=False)
    python = os.path.join(venv, "Scripts" if IS_WINDOWS else "bin",
                          "python.exe" if IS_WINDOWS else "python")
    if not os.path.exists(python):
        say("Could not create a virtual environment. The error was:")
        say((attempt.stderr or "").strip()[:400])
        return sys.executable

    subprocess.run([python, "-m", "pip", "install", "--upgrade", "-q", "pip"], check=False)
    subprocess.run([python, "-m", "pip", "install", "-q", *PIP_PACKAGES], check=False)
    say("Installed into .venv")
    activate = ".venv\\Scripts\\activate" if IS_WINDOWS else "source .venv/bin/activate"
    say("Activate it in new terminals with:  " + activate)
    return python


# --------------------------------------------------------------------------- #
# project + studio
# --------------------------------------------------------------------------- #

def create_project(python: str, name: str) -> str | None:
    rule("Creating your first project")
    target = os.path.join(HERE, name)
    if os.path.isdir(target):
        say(f"{name}/ already exists — using it.")
        if not os.path.isdir(os.path.join(target, "node_modules")):
            npm = which("npm")
            if npm:
                subprocess.run([npm, "install", "--no-audit", "--no-fund"],
                               cwd=target, check=False)
        return target

    result = subprocess.run(
        [python, os.path.join("skills", "vertical-video", "scripts", "new_project.py"),
         name],
        cwd=HERE, check=False,
    )
    return target if result.returncode == 0 and os.path.isdir(target) else None


# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--yes", "-y", action="store_true",
                        help="don't ask before installing system packages")
    parser.add_argument("--no-studio", action="store_true",
                        help="install only, don't open the studio")
    parser.add_argument("--name", default="my-video",
                        help="folder for the project it creates")
    args = parser.parse_args()

    print(f"""
  vertical-video-kit — install

  {SYSTEM} · Python {sys.version.split()[0]}
""")

    missing = ensure_system_tools(args.yes)
    python = ensure_python_packages()

    if missing:
        rule("Not finished")
        for item in missing:
            say(f"· {item} is still missing")
        say("")
        say("Install those, then run this again. Step by step, per platform:")
        say("  docs/NO-AGENT.md   (English)")
        say("  docs/SIN-AGENTE.md (español)")
        sys.exit(1)

    project = create_project(python, args.name)
    if not project:
        sys.exit("\n  Could not create the project.\n")

    opened = False
    if not args.no_studio:
        rule("Opening the Remotion studio")
        from studio import open_studio
        opened = open_studio(project)
    studio_line = "" if opened else "    npm run dev                  open the studio\n"

    rule("Done")
    print(f"""  Your project:  {project}

  Two files hold everything you write:

    script.json      what is SAID out loud
    src/content.ts   what is SEEN on screen

  Then, from inside {args.name}/:

    python scripts/voice.py      narration, and how long each scene runs
    python scripts/captions.py   word-by-word captions
    npm run render               output/video.mp4
    python scripts/publish.py    upload/video.mp4, ready for the platforms
{studio_line}
  Rather be asked questions than edit files?

    python skills/vertical-video/scripts/wizard.py

  Want an AI to write the script? docs/PROMPTS.md has prompts that work in
  any free chat — no subscription, nothing else to install.
""")


if __name__ == "__main__":
    main()

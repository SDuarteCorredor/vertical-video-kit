"""Opens the Remotion studio — the live preview — for a project.

    python skills/vertical-video/scripts/studio.py my-video
    python skills/vertical-video/scripts/studio.py my-video --port 4000
    python skills/vertical-video/scripts/studio.py my-video --wait

`npm run dev` inside the project does the same thing. This exists because it
starts the studio detached, waits until it is actually answering, and opens a
browser at it — so the command finishes with a visible studio instead of
holding the terminal open, and works the same whether a person or an agent
ran it.

Use --wait to keep it in the foreground instead (Ctrl+C to stop).
"""
from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

IS_WINDOWS = sys.platform.startswith("win")


def free_port(preferred: int = 3000) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred


def answering(url: str) -> bool:
    """Is the studio serving its page yet?

    A 200 and nothing less. While the bundler is still working the server is
    already listening and answers 5xx, so accepting any response means opening
    a browser on an error page and calling it success.
    """
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def open_studio(project: str, port: int | None = None,
                wait: bool = False, quiet: bool = False) -> bool:
    """Start the studio for `project`. Returns whether it came up."""
    def say(message: str = "") -> None:
        if not quiet:
            print(f"  {message}")

    npx = shutil.which("npx")
    if not npx:
        say("npx not found — Node is not installed, or not on this PATH.")
        say(f"Once it is:  cd {os.path.basename(project)} && npm run dev")
        return False

    if not os.path.isdir(os.path.join(project, "node_modules")):
        npm = shutil.which("npm")
        if npm:
            say("Installing the project's dependencies first (a minute or two)...")
            subprocess.run([npm, "install", "--no-audit", "--no-fund"],
                           cwd=project, check=False)

    index = os.path.join("src", "index.ts")

    if wait:
        say("Starting the studio. Ctrl+C to stop it.")
        subprocess.run([npx, "remotion", "studio", index], cwd=project, check=False)
        return True

    chosen = port or free_port()
    url = f"http://localhost:{chosen}"
    log_path = os.path.join(project, "studio.log")

    # Detached on purpose: this should finish and leave the studio running.
    detach: dict = {"start_new_session": True}
    if IS_WINDOWS:
        detach = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP
                  | getattr(subprocess, "DETACHED_PROCESS", 0)}

    with open(log_path, "w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [npx, "remotion", "studio", index, "--port", str(chosen), "--no-open"],
            cwd=project, stdout=log, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, **detach,
        )

    say("Starting it — the first build takes up to a minute.")
    for _ in range(120):
        if process.poll() is not None:
            say("The studio stopped on its own. The end of its log:")
            with open(log_path, encoding="utf-8") as handle:
                for line in handle.read().splitlines()[-12:]:
                    say(f"  {line}")
            return False
        if answering(url):
            break
        time.sleep(1)
    else:
        say(f"It did not answer on {url} in time. Check {log_path}.")
        return False

    try:
        webbrowser.open(url)
    except Exception:
        pass

    stop = ("taskkill /PID %d /F" % process.pid) if IS_WINDOWS \
        else ("kill %d" % process.pid)
    if not quiet:
        print(f"""
  The studio is open at  {url}

  If your browser did not open by itself, paste that address into it.
  It reloads by itself every time you save a file.

  To stop it later:  {stop}
""")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project", nargs="?", default=".",
                        help="the project folder (default: the current one)")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--wait", action="store_true",
                        help="hold the terminal instead of detaching")
    args = parser.parse_args()

    project = os.path.abspath(args.project)
    if not os.path.exists(os.path.join(project, "src", "index.ts")):
        sys.exit(f"\n  {project} is not a vertical-video project.\n"
                 f"  Make one with:  python skills/vertical-video/scripts/"
                 f"new_project.py my-video\n")

    sys.exit(0 if open_studio(project, args.port, args.wait) else 1)


if __name__ == "__main__":
    main()

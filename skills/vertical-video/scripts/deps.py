"""One Remotion install for every project, instead of one per project.

Node looks for packages in ./node_modules and then in every parent folder's
node_modules. So a single `npm install` at the kit root serves every project
created inside the kit: a new video is a small folder of text files, not
another ~400 MB copy of Remotion.

Projects created OUTSIDE the kit still get their own node_modules, exactly as
before. So does any project whose Remotion version differs from the shared
one: mixing versions inside one render fails, and a local install is the
safe way out.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Callable

HERE = os.path.dirname(os.path.abspath(__file__))
# skills/vertical-video/scripts/ -> up three
KIT_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _remotion_version(package_json: str) -> str | None:
    try:
        with open(package_json, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    for key in ("dependencies", "devDependencies"):
        version = data.get(key, {}).get("remotion")
        if version:
            return version
    return data.get("version") if data.get("name") == "remotion" else None


def installed_remotion(start: str) -> tuple[str, str] | None:
    """The nearest node_modules/remotion Node would resolve from `start`,
    as (folder that holds node_modules, version)."""
    folder = os.path.abspath(start)
    while True:
        package = os.path.join(folder, "node_modules", "remotion", "package.json")
        if os.path.exists(package):
            return folder, _remotion_version(package) or "?"
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def is_workspace(folder: str) -> bool:
    """A folder whose package.json exists to share dependencies downward."""
    try:
        with open(os.path.join(folder, "package.json"), encoding="utf-8") as handle:
            return bool(json.load(handle).get("vvkWorkspace"))
    except (OSError, ValueError):
        return False


def workspace_for(project: str) -> str | None:
    """The shared workspace above `project`, if it sits inside one."""
    folder = os.path.dirname(os.path.abspath(project))
    while True:
        if is_workspace(folder):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def npm_install(folder: str, say: Callable[[str], None]) -> bool:
    npm = shutil.which("npm")
    if not npm:
        say("npm not found — run 'npm install' yourself once Node is set up.")
        return False
    lock = os.path.exists(os.path.join(folder, "package-lock.json"))
    # `npm ci` installs exactly what the lockfile says, which is what makes
    # the shared install identical on every machine.
    command = [npm, "ci" if lock else "install", "--no-audit", "--no-fund"]
    return subprocess.run(command, cwd=folder, check=False).returncode == 0


def ensure_dependencies(project: str, say: Callable[[str], None] = print) -> str | None:
    """Make Remotion resolvable from `project`. Returns where it is installed."""
    wanted = _remotion_version(os.path.join(project, "package.json"))
    found = installed_remotion(project)
    if found and (not wanted or found[1] == wanted):
        return found[0]

    workspace = workspace_for(project)
    if workspace:
        shared = _remotion_version(os.path.join(workspace, "package.json"))
        if not wanted or shared == wanted:
            if not (found and found[0] == workspace):
                say("Installing the shared Remotion for every project (once, a minute or two)...")
                npm_install(workspace, say)
            found = installed_remotion(project)
            if found and (not wanted or found[1] == wanted):
                return found[0]
        else:
            say(f"This project pins Remotion {wanted}; the shared one is {shared}.")

    say("Installing this project's own dependencies (a minute or two)...")
    npm_install(project, say)
    found = installed_remotion(project)
    return found[0] if found else None


def main() -> int:
    """Checks the shared versions still match the template's."""
    template = os.path.join(KIT_ROOT, "template", "remotion-vertical", "package.json")
    root = os.path.join(KIT_ROOT, "package.json")
    with open(template, encoding="utf-8") as a, open(root, encoding="utf-8") as b:
        t, r = json.load(a), json.load(b)
    drift = [
        f"{section}.{name}: template {version}, kit root {r.get(section, {}).get(name)}"
        for section in ("dependencies", "devDependencies")
        for name, version in t.get(section, {}).items()
        if r.get(section, {}).get(name) != version
    ]
    for line in drift:
        print(f"  {line}")
    print("  Versions match." if not drift else
          "  Update both package.json files together, then run npm install at the kit root.")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())

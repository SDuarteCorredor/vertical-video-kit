"""Downloads source footage with yt-dlp.

Only download what you have the right to use. A platform's terms and the
creator's copyright both still apply — this script makes the mechanics easy,
it does not make the permission appear.

    python scripts/download.py <url>
    python scripts/download.py <url> --audio-only
    python scripts/download.py <url> --subs --out downloads/
    python scripts/download.py <url> --browser chrome   # for content you can
                                                        # only see signed in
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--out", default="downloads")
    parser.add_argument("--audio-only", action="store_true")
    parser.add_argument("--subs", action="store_true",
                        help="also grab subtitles, including auto-generated ones")
    parser.add_argument("--browser", help="load cookies from this browser "
                                          "(chrome, firefox, edge...)")
    args = parser.parse_args()

    binary = shutil.which("yt-dlp")
    if not binary:
        sys.exit("\n  yt-dlp is missing.  pip install yt-dlp\n")

    os.makedirs(args.out, exist_ok=True)
    command = [binary, "--no-playlist", "--restrict-filenames",
               "-o", os.path.join(args.out, "%(title)s.%(ext)s")]

    if args.audio_only:
        command += ["-x", "--audio-format", "mp3"]
    else:
        # Force mp4/h264 so FFmpeg and Remotion can both read it without a
        # remux step; the "best" default often lands on VP9 or AV1.
        command += ["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
                    "--merge-output-format", "mp4"]

    if args.subs:
        command += ["--write-subs", "--write-auto-subs", "--sub-format", "vtt"]
    if args.browser:
        command += ["--cookies-from-browser", args.browser]

    command.append(args.url)
    raise SystemExit(subprocess.run(command).returncode)


if __name__ == "__main__":
    main()

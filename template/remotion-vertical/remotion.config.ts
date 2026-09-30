import { Config } from "@remotion/cli/config";
import { cpus, totalmem } from "node:os";
import { readFileSync } from "node:fs";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// CRF 17 is visually lossless for text on a 1080x1920 canvas.
// Never export short-form video at a low fixed bitrate: the platforms
// re-encode your upload, so anything you lose here is lost twice.
Config.setCrf(17);

/**
 * Render concurrency, sized to the machine — not just the CPU.
 *
 * Remotion defaults to one worker per CPU core, and each worker is its own
 * headless Chrome tab. That is right for a 16-core workstation and wrong for
 * the laptop or free-tier VM most people actually render on: eight cores and
 * 8GB of RAM means eight tabs fighting over memory the OS does not have, so
 * it starts swapping and a render that should take a minute takes twenty —
 * or dies with an out-of-memory error that names Chrome, not Remotion.
 *
 * ~1.2GB per concurrent tab is the safe budget for a 1080x1920 text-and-image
 * composition like this one. Override with REMOTION_CONCURRENCY=<n> if you
 * know the machine better than this guess does.
 */
function availableMemoryBytes(): number {
  // os.totalmem() reports the HOST's memory, which overstates what is really
  // available inside a container or a memory-capped VM — a common case for
  // a render (CI, a free-tier cloud box, a locked-down office laptop). Linux
  // cgroups expose the real limit when there is one.
  const cgroupLimits = [
    "/sys/fs/cgroup/memory.max", // cgroup v2
    "/sys/fs/cgroup/memory/memory.limit_in_bytes", // cgroup v1
  ];
  for (const path of cgroupLimits) {
    try {
      const raw = readFileSync(path, "utf8").trim();
      const bytes = Number(raw);
      // cgroup v2 writes the literal string "max" for "no limit" — Number()
      // turns that into NaN, which correctly falls through to the host total.
      if (Number.isFinite(bytes) && bytes > 0 && bytes < totalmem()) {
        return bytes;
      }
    } catch {
      // File doesn't exist (not in a cgroup) or isn't readable — fine.
    }
  }
  return totalmem();
}

const GB = 1024 ** 3;
const cores = Math.max(1, cpus().length);
const byMemory = Math.max(1, Math.floor(availableMemoryBytes() / (1.2 * GB)));
const concurrency = Math.min(cores, byMemory);

const override = process.env.REMOTION_CONCURRENCY;
Config.setConcurrency(override || concurrency);

console.log(
  `  [remotion.config] concurrency ${override ?? concurrency} ` +
    `(${cores} cores, ~${(availableMemoryBytes() / GB).toFixed(1)}GB available)` +
    (override ? " — from REMOTION_CONCURRENCY" : ""),
);

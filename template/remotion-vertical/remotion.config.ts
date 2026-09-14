import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// CRF 17 is visually lossless for text on a 1080x1920 canvas.
// Never export short-form video at a low fixed bitrate: the platforms
// re-encode your upload, so anything you lose here is lost twice.
Config.setCrf(17);

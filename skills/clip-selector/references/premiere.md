# Premiere and Adobe's own tools

Researched November 2026. Since version 26.0 (January 2026) the app is called
**Adobe Premiere**, no longer "Premiere Pro". Where a claim could only be
checked through search summaries and not the page itself, it says so.

## How the selection gets into Premiere

**FCP 7 XML (`xmeml`), imported with File > Import.** It is the one route
that needs nothing installed, works in every Premiere version, and carries
what a selection is made of: in/out points, clip names, and markers with a
name and a comment. Premiere writes the same format when it exports, which is
where the details in `scripts/selects.py` come from:

| Detail | Rule |
|---|---|
| Frame rate | `<timebase>30</timebase><ntsc>TRUE</ntsc>` is 29.97; `ntsc FALSE` is a true 30. Writing 30 for 29.97 footage slides every cut by a frame each ~33 s. |
| Times | Whole frames. `in`/`out` count the clip's source frames; `start`/`end` count the sequence's. `duration` is the whole media file, not the clip. |
| Files | Defined once in full, referenced by id afterwards. |
| Paths | Windows `file://localhost/D%3a/Folder/clip.mov` (colon as `%3a`, as Premiere exports it); macOS `file://localhost/Users/...` or `/Volumes/...`. |
| Markers | `<out>-1</out>` is a point marker. On the sequence they count sequence frames, inside a clip source frames. **No documented way to set marker colour**, so the role goes in the marker name: `03 HOOK – "nadie te dice esto"`. |
| Clip labels | `<labels><label2>Forest</label2></labels>`: Premiere writes these, so the rating colour on each clip should come through. |

Not used, and why:

- **OTIO** (`.otio`). Premiere opens it natively since 25.6/26.0, and Adobe's
  own Firefly Reframe API hands timelines over this way. It also has known
  import bugs, so `selects.py` writes it only as a second copy, and only
  when `opentimelineio` is installed.
- **EDL**. It carries no file paths, limits reel names to 8 characters, and
  drops sequence markers.
- **FCPXML** (Final Cut X). Premiere can't import it.
- **Marker CSV**. Premiere exports marker CSVs but can't import them.
- **Subclips through XML** are undocumented. The editor can make them in one
  click (right-click > Make Subclip).

**Not yet verified:** an import of this kit's XML into a real Premiere 26 on
Windows and on macOS. Every file it writes is read back with OpenTimelineIO's
FCP XML reader before it is handed over. The first time, import a two-clip
test and check three things: the markers are there, the colour labels are
there, and the media is linked.

## Footage from a phone

Phones record **variable frame rate**. Premiere's own product team lists
drift, stutter and audio misalignment on VFR footage as known issues
([community thread, Feb 2026][vfr], search summary). `log_footage.py` and
`selects.py` both flag it. The fix is to conform to a constant rate before
selecting, and select from the copies:

```bash
ffmpeg -i IMG_1043.mov -fps_mode cfr -r 30000/1001 -c:v libx264 -crf 14 -c:a aac -b:a 256k IMG_1043_cfr.mov
```

## What each Adobe tool is for here

| Tool | Use it for selection? |
|---|---|
| **Adobe for creativity** connector (`video_create_quick_cut`, `media_summarize`, `video_resize`, …) | **No.** Quick Cut returns one rendered MP4 with no in/out list, needs the footage uploaded to Creative Cloud, and spends generative credits. Adobe's two descriptions of how it picks moments contradict each other: the tool definition says visual engagement only, while Adobe's skill says it uses the transcript when there is speech. At most it is a baseline to compare against. None of the tools opens a Premiere project, sequence or marker. |
| **AI Assistant in Premiere** (public beta since June 2026) | After the handover. It organizes bins, renames, adds markers and assembles rough cuts from inside Premiere. Outside agents can't call it, but the editor can point it at the imported selects. |
| **Media Intelligence + Search panel** (25.2+) | The editor's tool for finding *more* shots by description. It runs locally. |
| **Text-Based Editing** | The editor can re-cut the selects from their transcript. |
| **Scene Edit Detection** | One right-click turns shot changes into cuts, markers or a subclip bin, so the selection doesn't need to ship shot boundaries. |
| **Auto Reframe** (Sequence > Auto Reframe Sequence > 9:16) | Horizontal source: hand over a 16:9 selects sequence and let the editor reframe. Don't pre-crop. Set the reframed sequence to 1080×1920; the default can come out at about 607×1080. |
| **Enhance Speech, Remix, Morph Cut, Generative Extend** | Finishing, which is the editor's job. Generative Extend adds about 2 s of video at most, so don't count on it to rescue a clip cut too tight. |

## Driving Premiere directly: possible, not worth it yet

- **No official Premiere MCP server exists.** Adobe's route is the built-in
  assistant. Adobe MAX runs 10–12 November 2026; check its announcements
  for news on this.
- **UXP**, the official plugin API (`@adobe/premierepro` 26.5), can now
  import files, create sequences, set in/out points, insert clips, make
  subclips, add coloured markers and import a transcript. A plugin can't
  listen for connections, so an outside agent needs a proxy process in
  between. Worth building only if one-click import with coloured markers
  ever matters.
- **Community MCP servers** for Premiere exist: leancoderkavy/premiere-pro-mcp,
  hetpatel-11/Adobe_Premiere_Pro_MCP, ayushozha/AdobePremiereProMCP and
  mikechambers/adb-mcp. Most use the older CEP bridge, which needs a debug
  flag. Some can run arbitrary scripts, and one ships telemetry and unsigned
  installers. Don't depend on them for client footage.

## The workflow Adobe Learn teaches

Ingest and organize in bins, then log and mark, then build selects or a
stringout, then rough cut, fine cut, finishing, reframe and export
([Select shots to create a rough cut][learn-select], [Auto Reframe for
socials][learn-reframe], [Media Intelligence search][learn-mi]; all three
read through search summaries). **This skill does steps two and three**, and
hands over at the rough cut.

[vfr]: https://community.adobe.com/questions-729/looking-for-vfr-variable-frame-rate-problem-files-help-us-improve-premiere-s-editing-experience-1550759
[learn-select]: https://www.adobe.com/learn/premiere-pro/web/premiere-pro-select-shots-cc
[learn-reframe]: https://www.adobe.com/learn/premiere-pro/web/auto-reframe-for-socials
[learn-mi]: https://www.adobe.com/learn/premiere-pro/web/media-intelligence-search-ai

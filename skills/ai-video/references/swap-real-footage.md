# Swapping a person in footage you already have

When a recorded shot is right but the person in it has to change — a colleague
who left, a presenter who should become the brand mascot — swap the character
instead of generating the shot again.

On Higgsfield this is **Genjutsu** (and the cheaper **Genjutsu Lite**): upload
the video, add an image of the new character, generate. Creators using it
report that it keeps the original camera angle, hand movements, timing and cut
points frame for frame, and can also change the outfit or the whole location
when asked. Source clips run from about 4 to 30 seconds.

## Flow

1. **Cut the shot exactly** with `scripts/prep_shots.py`, at full quality.
   Shorter is safer: one action per clip.
2. **Reference image:** the approved face close-up, or a full-body pose close to
   the one in the shot. For two people in frame, one reference per person.
3. **Prompt:** what to replace, with what, and what to keep —

   ```
   Replace the man in the green shirt with @character, matching the reference 100%
   (face, outfit, logo). Keep the camera movement, timing, hand movements, the
   other person, the room and the lighting exactly as they are. Do not add objects.
   ```

4. **Test cheap:** Lite tier or 720p first, on the hardest few seconds.
5. **Check the middle and the end** of the clip, the hands, and anything with
   text in it (posters, screens). Fix small things in the edit.

## When it is not the right tool

- **A UI recording with a face inside it** (an app's selfie step): swapping the
  whole frame warps the interface. Generate the character alone and composite
  it into the camera box instead — see "Compositing" in `prompting.md`.
- **A shot whose framing is wrong anyway:** regenerate it from a start frame.
- **A cartoon character replacing a real person in a real room** may look
  pasted in. Make one test before swapping a whole sequence; if it does,
  generate those shots in a consistent style instead.

## Related tools

- **Motion transfer:** reuse a real performance (a walk, a gesture) on another
  character when the camera can change.
- **Face fix on a finished clip** (Higgsfield calls it Object Swap): repair a
  drifted face without regenerating the shot.

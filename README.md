# Beyond the Sleeping Hills

An original, approximately three-minute fantasy CRPG title-screen theme: calm,
with a sense of setting out on an adventure. The music is in D Dorian and a
gentle 6/8, with an introduction, two contrasting themes, a varied return, and a
quiet ending. Subtle tempo changes and a short release tail are included in the
three-minute duration.

**File:** `beyond_the_sleeping_hills.mid`

Standard MIDI File type 1, 480 ticks per quarter note, seven instrument tracks
plus a conductor track. The General MIDI palette is recorder, nylon-string
guitar as a lute, harp, strings, cello, English horn, and a soft French horn.
Playback timbre depends on your MIDI player's sound bank.

## Regenerate or adapt

No third-party Python libraries are needed.

```sh
python3 create_music.py
python3 create_music.py --output another_journey.mid --duration 210 --seed 12
python3 create_music.py --output lower_key.mid --transpose -2
```

`--duration` sets the total playback length in seconds by scaling the tempo;
it does not add or remove measures. `--seed` varies expressive timing and note
velocities while preserving the composition. `--transpose` shifts the score
by semitones. To write new music with the tool, edit the named chord palettes,
melody phrases, and the arrangement in `create_music.py`. Phrase lengths are in
eighth notes; each measure must total six, and `R` means a rest.

The default output is placed beside the script. Running the same command again
replaces that output file.

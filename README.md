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
python3 songs/beyond_the_sleeping_hills.py
python3 songs/beyond_the_sleeping_hills.py --output another_journey.mid --duration 210 --seed 12
python3 songs/beyond_the_sleeping_hills.py --output lower_key.mid --transpose -2
```

`--duration` sets the total playback length in seconds by scaling the tempo;
it does not add or remove measures. `--seed` varies expressive timing and note
velocities while preserving the composition. `--transpose` shifts the score
by semitones. To adapt this piece, edit the named chord palettes, melody phrases,
and arrangement in `songs/beyond_the_sleeping_hills.py`. Its phrase lengths are
in eighth notes; each measure must total six, and `R` means a rest.

The default output is `beyond_the_sleeping_hills.mid` in the project root.
Relative `--output` paths are resolved from the current working directory.
Running the same command again replaces that output file. The song script can
also be run by absolute path from another directory, or with
`python3 -m songs.beyond_the_sleeping_hills` from the project root.

## Backend and songs

`create_music.py` is the reusable backend. It provides pitch conversion, MIDI
tracks and encoding, tempo scaling, and the shared command-line renderer. It
contains no composition and is imported by song scripts.

`songs/beyond_the_sleeping_hills.py` owns the title, score length, meter, chord
voicings, melodies, tempo curve, instruments, and arrangement for this piece.

To add a song, copy that script to `songs/your_song.py`, change its music and
metadata, and set its default output to `your_song.mid`. Then run
`python3 songs/your_song.py`. No backend changes or song registration are needed.
Keep the import-path setup and the `if __name__ == "__main__"` entry point so
the new script works both directly and as a module.

A song implements `arrange(seed, transpose, duration)` and returns its list of
`Track` objects, including a conductor track with tempo and other metadata.
Its `main()` calls `render_song()` with that function, the title, default output
path, and optional descriptive text. The renderer handles the common CLI
options, file writing, and output summary. Imports alone do not render music.

Track positions and durations are MIDI ticks (`PPQ = 480`, `EIGHTH = 240` by
default). Pass each `Track` an `end_tick` for the total playback length and an
optional `note_end_tick` to stop notes before a release tail. Each song chooses
its own length and meter. `tempo_map()` accepts `(tick, quarter-note BPM)` changes
starting at tick zero, plus `end_tick` and the requested `duration` in seconds;
it returns `(tick, microseconds per quarter note)` pairs for MIDI tempo events.
For rendering without the CLI, `encode_midi(tracks)` returns the MIDI bytes.

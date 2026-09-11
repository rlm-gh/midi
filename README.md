# Fantasy RPG title themes

Original, reproducible compositions using MIDI 1.0 / General MIDI instruments,
written as Standard MIDI Files of type 1. Each instrumental part has a separate
track and channel, with tempo and section markers in a conductor track.
Playback timbre depends on your MIDI player's sound bank.

## When the Ancient Gates Awaken

**MIDI:** [when_the_ancient_gates_awaken.mid](when_the_ancient_gates_awaken.mid)

**Score:** [songs/when_the_ancient_gates_awaken.py](songs/when_the_ancient_gates_awaken.py)

**Embellished brief:** [songs/when_the_ancient_gates_awaken.md](songs/when_the_ancient_gates_awaken.md)

A **4:48 medieval fantasy RPG title theme**, composed from an expanded version
of the original song request. Its 104 measures in 4/4 begin with quiet harp and
recorder, gradually introduce the orchestra, and transform an E-minor main
theme into an E-major coronation. A contrasting G-major melody, a quieter
development, and an independent cello countermelody give the piece its shape.
The final recorder-and-harp passage settles on an open fifth, with a release
measure included in the duration. It has a composed ending, rather than MIDI
loop commands.

The MIDI 1.0 / General MIDI score is a **Standard MIDI File type 1**, with
480 ticks per quarter note, 16 instrument tracks on independent channels, and
a conductor track carrying tempo, meter, key signatures, and section markers.
The palette includes harp, recorder, lute represented by nylon-string guitar,
five string sections, oboe, flute, horns, trumpets, trombones, choir, timpani,
and orchestral percussion. Pitched timpani have their own channel; unpitched
percussion uses channel 10. Sustained instruments have expression swells;
short string bowing, wind breaths, fanfare replies, suspensions, and drum rolls
are written into the score.

| Time | Section |
| --- | --- |
| 0:00 | Mist before the gate |
| 0:27 | A name remembered |
| 1:14 | Banners on the road |
| 1:58 | The realm beyond |
| 2:39 | A shadow on the stone |
| 3:01 | The turning of the key |
| 3:21 | The ancient gates awaken |
| 4:00 | The crown in sunlight |
| 4:18 | An unwritten journey |

Regenerate with Python's standard library:

```sh
python3 songs/when_the_ancient_gates_awaken.py
python3 -m songs.when_the_ancient_gates_awaken --output my_title.mid --duration 300 --seed 12
python3 songs/when_the_ancient_gates_awaken.py --output lower_title.mid --transpose -2
```

The defaults are 288 seconds and seed 41. `--duration` scales the tempo curve;
`--seed` changes performance timing and velocities; `--transpose` shifts the
pitched parts and key signatures while preserving percussion sound numbers.
The default file is written to the project root. Relative `--output` paths use
the current working directory, and rerunning replaces the chosen output file.
Phrase durations in the Python score are eighth notes, totaling eight per
measure. `R` denotes a rest; `>` in a harmony entry changes chords halfway
through a measure.

## Crown of the Dawn

**File:** [crown_of_the_dawn.mid](crown_of_the_dawn.mid)

**Score:** [songs/crown_of_the_dawn.py](songs/crown_of_the_dawn.py)

A **4:12 orchestral medieval fantasy RPG title-screen theme**: a quiet harp
opening, a solitary recorder, and a gradual gathering of the orchestra into an
epic reprise. Its 80 measures are in flowing 12/8, beginning in D minor and
turning to D major for the climactic statement. A short pastoral coda recalls
the opening and settles on an open fifth, followed by a release tail.

There are **16 instrumental tracks plus the conductor**, at 480 ticks per
quarter note: harp, recorder, flute, oboe, two violin sections, violas, cellos,
contrabasses, French horns, trumpets, trombones, choir, timpani, orchestral
percussion, and nylon-string guitar as a lute. The arrangement includes two
composed themes, a motivic development, a separate cello countermelody, string
ostinatos, brass replies, timpani and snare rolls, and cadential harp runs.
Continuous expression curves shape sustained notes; tempo changes, phrasing,
stereo placement, and restrained timing variation shape the performance.

Approximate cues at the default duration (also embedded as MIDI markers):

| Time | Section | Orchestration |
| --- | --- | --- |
| 0:00 | The sleeping kingdom | Harp, then recorder, lute, and cello |
| 0:30 | A traveller's promise | Main theme; inner strings, bass, and woodwinds enter |
| 1:22 | The oath beneath the banners | Broad horn melody; moving strings and timpani |
| 1:47 | Across the sunlit realm | Second theme in violins; choir and brass join |
| 2:33 | The gathering storm | Fragmented horn calls, rising strings, and drum rolls |
| 2:55 | Crown of the dawn | Main theme in violins and horns, with cello counterpoint |
| 3:17 | The gates of gold | D-major transformation and full orchestral climax |
| 3:38 | A kingdom awaits | Broad major-key resolution |
| 3:51 | The distant hills | Recorder and harp return; quiet open-fifth ending |

Generate the MIDI with the Python standard library alone:

```sh
python3 songs/crown_of_the_dawn.py
python3 songs/crown_of_the_dawn.py --output my_title.mid --duration 270 --seed 12
python3 -m songs.crown_of_the_dawn --output lower_title.mid --transpose -2
```

The default output is `crown_of_the_dawn.mid` in the project root. `--duration`
scales the tempo curve without changing the score; `--seed` changes timing and
velocities without changing the composition. `--transpose` moves pitched parts
and key signatures, including the timpani, while leaving percussion sound
numbers unchanged. The default seed is 23. Relative output paths use the current
working directory; rerunning a command replaces its output file.

To adapt the piece, edit the named harmony sequences, melody phrases, dynamics,
and orchestration in its song script. Phrase lengths are in eighth notes, each
measure totals twelve, and `R` denotes a rest.

## Beyond the Sleeping Hills

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

### Regenerate or adapt

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

Each script in `songs/` owns its title, score length, meter, chord voicings,
melodies, tempo curve, instruments, and arrangement. All compositions use the
same backend without any additional dependencies.

To add a song, copy a song script to `songs/your_song.py`, change its music and
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

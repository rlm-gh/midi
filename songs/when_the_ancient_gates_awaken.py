#!/usr/bin/env python3
"""Write When the Ancient Gates Awaken, an original orchestral RPG title theme.

    python3 songs/when_the_ancient_gates_awaken.py
    python3 -m songs.when_the_ancient_gates_awaken --duration 300 --transpose -2

The companion Markdown file records the brief and its embellishment. This is
a composed 104-bar score; the seed varies performance, never the written music.
Phrase durations and accompaniment offsets are eighth notes; each 4/4 bar has 8.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
import math
from pathlib import Path
import random
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from create_music import EIGHTH, Track, pitch, pitches, render_song, tempo_map


TITLE = "When the Ancient Gates Awaken"
BAR = 8 * EIGHTH
BARS = 104
SCORE_END = BARS * BAR
END = SCORE_END + BAR
DEFAULT_DURATION = 288.0
DEFAULT_SEED = 41

SECTIONS = [
    (0, "I - Mist before the gate"),
    (8, "II - A name remembered"),
    (24, "III - Banners on the road"),
    (40, "IV - The realm beyond"),
    (56, "V - A shadow on the stone"),
    (64, "VI - The turning of the key"),
    (72, "VII - The ancient gates awaken"),
    (88, "VIII - The crown in sunlight"),
    (96, "IX - An unwritten journey"),
]
# Quarter-note BPM, before scaling the complete performance to --duration.
TEMPO_CHANGES = [
    (0, 70), (4, 74), (8, 80), (16, 84), (23, 78),
    (24, 88), (32, 92), (39, 86), (40, 94), (48, 96), (55, 88),
    (56, 84), (60, 88), (64, 92), (66, 96), (68, 100), (70, 104),
    (71, 92), (72, 100), (80, 104), (87, 94), (88, 106), (92, 108),
    (95, 96), (96, 90), (98, 82), (100, 74), (102, 66), (103, 58),
]
ENERGY = [
    (0, .10), (4, .18), (8, .28), (16, .38), (24, .49), (32, .59),
    (40, .66), (48, .74), (55, .70), (56, .36), (60, .43), (64, .53),
    (68, .70), (72, .83), (80, .91), (88, .97), (92, 1.0), (95, .96),
    (96, .83), (99, .52), (100, .29), (103, .15), (104, .04),
]


@dataclass(frozen=True)
class Chord:
    bass: int
    inner: tuple[int, ...]
    upper: tuple[int, ...]
    harp: tuple[int, ...]


def chord(bass: str, inner: str, upper: str, harp: str) -> Chord:
    return Chord(pitch(bass), pitches(inner), pitches(upper), pitches(harp))


CHORDS = {
    "Em": chord("E2", "E3 G3 B3", "E4 G4 B4", "E3 B3 E4 G4 B4 E5"),
    "Em9": chord("E2", "E3 G3 B3", "E4 G4 B4", "E3 B3 E4 F#4 G4 B4"),
    "C": chord("C2", "E3 G3 C4", "E4 G4 C5", "C3 G3 C4 E4 G4 C5"),
    "Cmaj7": chord("C2", "E3 G3 B3", "E4 G4 B4", "C3 G3 B3 E4 G4 C5"),
    "G": chord("G1", "D3 G3 B3", "D4 G4 B4", "G2 D3 G3 B3 D4 G4"),
    "G/B": chord("B1", "D3 G3 B3", "D4 G4 B4", "B2 D3 G3 B3 D4 G4"),
    "D": chord("D2", "D3 F#3 A3", "D4 F#4 A4", "D3 A3 D4 F#4 A4 D5"),
    "D/F#": chord("F#2", "D3 F#3 A3", "D4 F#4 A4", "F#3 A3 D4 F#4 A4 D5"),
    "Am": chord("A1", "E3 A3 C4", "E4 A4 C5", "A2 E3 A3 C4 E4 A4"),
    "Em/G": chord("G2", "E3 G3 B3", "E4 G4 B4", "G3 B3 E4 G4 B4 E5"),
    "Em/B": chord("B1", "E3 G3 B3", "E4 G4 B4", "B2 E3 G3 B3 E4 G4"),
    "F#dim": chord("F#2", "F#3 A3 C4", "F#4 A4 C5", "F#3 A3 C4 F#4 A4 C5"),
    "Bsus": chord("B1", "F#3 B3 E4", "E4 F#4 B4", "B2 F#3 B3 E4 F#4 B4"),
    "B7": chord("B1", "F#3 A3 D#4", "D#4 F#4 A4", "B2 F#3 A3 D#4 F#4 B4"),
    "A/C#": chord("C#2", "E3 A3 C#4", "E4 A4 C#5", "C#3 E3 A3 C#4 E4 A4"),
    "Bm": chord("B1", "F#3 B3 D4", "F#4 B4 D5", "B2 F#3 B3 D4 F#4 B4"),
    "E": chord("E2", "E3 G#3 B3", "E4 G#4 B4", "E3 B3 E4 G#4 B4 E5"),
    "E/B": chord("B1", "E3 G#3 B3", "E4 G#4 B4", "B2 E3 G#3 B3 E4 G#4"),
    "A": chord("A1", "E3 A3 C#4", "E4 A4 C#5", "A2 E3 A3 C#4 E4 A4"),
    "C#m": chord("C#2", "E3 G#3 C#4", "E4 G#4 C#5", "C#3 G#3 C#4 E4 G#4 C#5"),
    "G#m/B": chord("B1", "D#3 G#3 B3", "D#4 G#4 B4", "B2 D#3 G#3 B3 D#4 G#4"),
    "F#m": chord("F#2", "F#3 A3 C#4", "F#4 A4 C#5", "F#3 A3 C#4 F#4 A4 C#5"),
    "E5": chord("E2", "E3 B3 E4", "E4 B4 E5", "E3 B3 E4 B4 E5 B5"),
}

INTRO_HARMONY = "E5 Em9 Cmaj7 G/B A/C# Em/G Bsus>B7 Em".split()
A_HARMONY = "Em C G/B D Am Em/G F#dim Bsus>B7 Em D/F# C G/B A/C# Em/B Bsus>B7 Em".split()
B_HARMONY = "G G/B C D Em Bm C D G/B C Am D/F# G C Bsus>B7 B7".split()
SHADOW_HARMONY = "Em Em/B Cmaj7 Am F#dim C Bsus B7".split()
BUILD_HARMONY = "Em/B C Em/B A/C# F#dim Bsus B7 B7".split()
SUNLIGHT_HARMONY = "E A C#m G#m/B F#m E/B Bsus>B7 E".split()
CODA_HARMONY = "E A E/B E Am Em/B Bsus E5".split()
HARMONY = (INTRO_HARMONY + A_HARMONY + A_HARMONY + B_HARMONY
           + SHADOW_HARMONY + BUILD_HARMONY + A_HARMONY
           + SUNLIGHT_HARMONY + CODA_HARMONY)

# Explicit melodic phrases: one measure per string, R denotes a rest.
THEME_A = [
    "B4:1 E5:2 F#5:1 G5:2 F#5:1 E5:1",
    "G5:3 E5:1 D5:1 C5:2 R:1",
    "D5:1 G5:2 B5:1 A5:2 G5:1 D5:1",
    "F#5:2 E5:1 D5:1 A4:3 R:1",
    "E5:1 A5:2 G5:1 E5:2 C5:1 B4:1",
    "B4:2 E5:2 G5:1 F#5:1 E5:1 R:1",
    "A5:2 F#5:1 E5:1 C5:2 A4:1 R:1",
    "F#5:2 E5:2 D#5:2 B4:1 R:1",
    "B4:1 E5:2 G5:1 B5:2 A5:1 G5:1",
    "A5:3 F#5:1 E5:2 D5:1 R:1",
    "E5:2 G5:1 C6:1 B5:1 G5:1 E5:1 R:1",
    "D5:1 G5:2 B5:1 A5:1 G5:1 D5:1 R:1",
    "C#5:2 E5:2 A5:2 G5:1 E5:1",
    "G5:2 F#5:1 E5:1 B4:2 E5:1 R:1",
    "F#5:2 E5:2 D#5:1 F#5:1 B5:1 R:1",
    "E5:6 R:2",
]
HORN_THEME = [
    "B3:2 E4:4 G4:2", "G4:4 E4:2 C4:1 R:1",
    "D4:2 G4:3 B4:1 G4:2", "F#4:4 D4:3 R:1",
    "E4:2 A4:3 G4:1 E4:2", "B3:2 E4:4 G4:1 R:1",
    "A4:3 F#4:1 C4:3 R:1", "F#4:2 E4:2 D#4:3 R:1",
    "B3:2 E4:2 G4:2 B4:2", "A4:4 F#4:2 D4:1 R:1",
    "E4:2 G4:2 C5:2 G4:2", "B4:3 G4:1 D4:3 R:1",
    "C#4:2 E4:2 A4:3 R:1", "G4:2 F#4:1 E4:1 B3:2 E4:2",
    "F#4:2 E4:2 D#4:2 B3:1 R:1", "E4:6 R:2",
]
THEME_B = [
    "B4:2 D5:2 G5:3 F#5:1", "G5:2 B5:2 A5:1 G5:1 D5:1 R:1",
    "E5:2 G5:2 C6:2 B5:1 G5:1", "F#5:3 E5:1 D5:3 R:1",
    "G5:2 B5:2 A5:1 G5:1 F#5:1 E5:1", "F#5:4 D5:2 B4:1 R:1",
    "E5:1 G5:1 C6:2 B5:1 A5:1 G5:1 E5:1", "F#5:2 E5:1 F#5:1 D5:3 R:1",
    "D5:1 G5:1 B5:2 D6:2 B5:1 G5:1", "C6:3 B5:1 A5:1 G5:1 E5:1 R:1",
    "A5:2 G5:1 E5:1 C5:2 E5:1 A5:1", "A5:2 F#5:2 E5:1 D5:2 R:1",
    "B5:4 G5:2 D5:1 R:1", "G5:2 E5:2 C5:3 R:1",
    "F#5:2 E5:2 D#5:2 F#5:1 R:1", "B5:4 F#5:2 D#5:1 R:1",
]
COUNTER_A = [
    "G3:3 B3:1 E4:2 D4:1 B3:1", "C4:2 B3:1 G3:1 E3:3 R:1",
    "G3:4 D4:2 B3:2", "A3:2 F#3:2 D3:3 R:1",
    "C4:3 B3:1 A3:2 E3:2", "G3:2 B3:2 E4:3 R:1",
    "C4:2 A3:2 F#3:2 A3:2", "B3:2 F#3:2 A3:2 D#4:1 R:1",
    "E4:3 D4:1 B3:2 G3:2", "D4:2 A3:2 F#3:3 R:1",
    "G3:2 C4:2 E4:3 D4:1", "B3:2 D4:2 G3:3 R:1",
    "A3:3 B3:1 C#4:2 E4:2", "B3:2 G3:2 E3:3 R:1",
    "B3:2 E4:2 D#4:2 F#4:1 R:1", "G3:2 B3:2 E4:3 R:1",
]
SUNLIGHT_THEME = [
    "B4:1 E5:2 F#5:1 G#5:2 B5:2", "C#6:3 B5:1 A5:2 E5:1 R:1",
    "G#5:2 E5:1 C#5:1 E5:2 G#5:2", "B5:3 G#5:1 F#5:1 D#5:2 R:1",
    "A5:2 C#6:2 B5:1 A5:1 F#5:2", "G#5:2 F#5:1 E5:1 B4:2 E5:2",
    "F#5:2 E5:2 D#5:1 F#5:1 B5:1 R:1", "E6:6 R:2",
]
COUNTER_SUNLIGHT = [
    "G#3:3 B3:1 E4:2 F#4:1 G#4:1", "A3:2 E4:2 C#4:3 R:1",
    "E4:2 D#4:1 C#4:1 G#3:2 E3:2", "D#4:2 B3:2 G#3:3 R:1",
    "C#4:2 A3:2 F#3:2 A3:2", "B3:2 G#3:2 E4:3 R:1",
    "B3:2 E4:2 D#4:2 F#4:1 R:1", "G#4:2 F#4:1 E4:3 R:2",
]


def energy(position: float) -> float:
    for (left, a), (right, b) in zip(ENERGY, ENERGY[1:]):
        if position <= right:
            return a + (b - a) * (position - left) / (right - left)
    return ENERGY[-1][1]


def harmony_at(bar: int):
    """Yield (offset, duration, chord); '>' gives a half-bar harmonic change."""
    names = HARMONY[bar].split(">")
    length = 8 / len(names)
    for index, name in enumerate(names):
        yield index * length, length, CHORDS[name]


def arrange(seed: int, transpose: int, duration: float) -> list[Track]:
    if len(HARMONY) != BARS:
        raise ValueError("Harmony must cover every measure")
    rng = random.Random(seed)
    make = partial(Track, end_tick=END, note_end_tick=SCORE_END)
    conductor = make(TITLE)
    conductor.meta(0, 0x01, b"Original RPG title theme; embellished brief in the companion Markdown score")
    conductor.meta(0, 0x01, b"GM1; 4/4; E minor with Dorian colour, G major, E major; composed ending")
    conductor.meta(0, 0x58, bytes([4, 2, 24, 8]))
    for tick, tempo in tempo_map([(bar * BAR, bpm) for bar, bpm in TEMPO_CHANGES],
                                 end_tick=END, duration=duration):
        conductor.meta(tick, 0x51, tempo.to_bytes(3, "big"))
    minor_keys = (-3, 4, -1, -6, 1, -4, 3, -2, 5, 0, -5, 2)
    major_keys = (0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5)
    for bar, tonic, minor in ((0, 4, True), (40, 7, False), (56, 4, True),
                              (88, 4, False), (100, 4, True)):
        signature = (minor_keys if minor else major_keys)[(tonic + transpose) % 12]
        conductor.meta(bar * BAR, 0x59, bytes([signature & 255, int(minor)]))
    for bar, label in SECTIONS:
        conductor.meta(bar * BAR, 0x06, label.encode("ascii"))

    # GM programs and channels are zero-based. Independent channels preserve
    # each section's articulation, pan and expression; channel 9 is drums only.
    harp = make("Harp - light through mist", 0, 46, 94, 34, 48)
    recorder = make("Recorder - the remembered name", 1, 74, 100, 58, 42)
    lute = make("Lute - nylon-string guitar", 2, 24, 81, 86, 33)
    cellos = make("Cellos - the answering oath", 3, 42, 94, 87, 42)
    violas = make("Violas - inner voices", 4, 48, 78, 72, 43)
    basses = make("Contrabasses - the foundations", 5, 43, 88, 65, 36)
    seconds = make("Violins II - the turning key", 6, 48, 80, 49, 42)
    oboe = make("Oboe - a distant companion", 7, 68, 97, 51, 40)
    flute = make("Flute - the open sky", 8, 73, 92, 76, 44)
    drums = make("Percussion - bass drum, snare, cymbals", 9, 0, 78, 64, 43)
    horns = make("French horns - the ancient banners", 10, 60, 102, 40, 47)
    firsts = make("Violins I - the gates awaken", 11, 48, 99, 29, 47)
    timpani = make("Timpani - footsteps of the kingdom", 12, 47, 91, 80, 43)
    choir = make("Choir aahs - memory of the realm", 13, 52, 73, 64, 60)
    trombones = make("Trombones - the stone towers", 14, 57, 81, 77, 44)
    trumpets = make("Trumpets - the crown in sunlight", 15, 56, 80, 58, 45)
    instruments = [harp, recorder, lute, cellos, violas, basses, seconds, oboe,
                   flute, drums, horns, firsts, timpani, choir, trombones, trumpets]

    def play(track, bar, offset, length, key, velocity, *, gate=.93, jitter=4):
        if bar == 71 and offset >= 7:
            return  # Decide the shared rest before adding performance jitter.
        start = max(bar * BAR, bar * BAR + round(offset * EIGHTH)
                    + rng.randint(-jitter, jitter))
        track.note(start, round(length * EIGHTH * gate),
                   key + (0 if track is drums else transpose),
                   round(velocity) + rng.randint(-3, 3))

    def phrase(track, start_bar, measures, *, octave=0, lift=0, gate=.96):
        for relative, measure in enumerate(measures):
            bar, offset = start_bar + relative, 0.0
            for token in measure.split():
                name, length = token.split(":")
                length = float(length)
                if name != "R":
                    accent = 4 if offset in (0, 4) else 0
                    play(track, bar, offset, length, pitch(name) + 12 * octave,
                         62 + 24 * energy(bar) + lift + accent, gate=gate)
                offset += length
            if offset != 8:
                raise ValueError(f"Bar {bar + 1}: expected 8 eighths, got {offset}")

    def sustain(track, first, last, voices, velocity):
        """Tie common tones across chord changes for up to two measures."""
        spans = [(bar * 8 + offset, length, voices(ch))
                 for bar in range(first, last)
                 for offset, length, ch in harmony_at(bar)]
        for voice in range(len(spans[0][2])):
            i = 0
            while i < len(spans):
                start, length, keys = spans[i]
                key, stop, j = keys[voice], start + length, i + 1
                while (j < len(spans) and spans[j][2][voice] == key
                       and spans[j][0] + spans[j][1] - start <= 16):
                    stop = spans[j][0] + spans[j][1]
                    j += 1
                bar, offset = divmod(start, 8)
                play(track, int(bar), offset + .03 * voice, stop - start - .12,
                     key, velocity + 18 * energy(bar), gate=1, jitter=2)
                i = j

    # Plucked accompaniment starts spaciously and hands its pulse to the strings.
    harp_run_bars = (7, 23, 39, 47, 55, 71, 79, 87, 91, 95, 99)
    for bar in range(BARS):
        e = energy(bar)
        for offset, length, ch in harmony_at(bar):
            if bar < 8 or 56 <= bar < 72 or 100 <= bar < 103:
                for step in range(0, int(length), 4 if bar < 4 or bar >= 102 else 2):
                    if bar in harp_run_bars and offset + step >= 5:
                        continue  # The cadential run takes over this hand's pattern.
                    index = (int(offset) + step) // 2 % 6
                    play(harp, bar, offset + step, min(3.7, length - step),
                         ch.harp[index], 45 + 18 * e, gate=1)
            elif bar % 2 == 0:
                for i, key in enumerate(ch.harp):
                    play(harp, bar, offset + i * .11, min(3.8, length) - i * .11,
                         key, 47 + 16 * e - i, gate=1, jitter=2)
            if 4 <= bar < 24 or 100 <= bar < 103:
                pattern = (0, 2, 3, 1, 4, 2, 3, 1)
                for step in range(int(length)):
                    if bar < 8 and step % 2:
                        continue
                    play(lute, bar, offset + step, 1.5, ch.harp[pattern[step]],
                         39 + 19 * e + (4 if step % 4 == 0 else 0))
        if bar in harp_run_bars:
            ch = list(harmony_at(bar))[-1][2]
            for i, index in enumerate((1, 2, 3, 4, 5, 4)):
                play(harp, bar, 5 + i * .5, 1.4, ch.harp[index], 48 + 18 * e)

    sustain(cellos, 6, 24, lambda ch: (ch.bass + 12,), 47)
    sustain(violas, 8, 100, lambda ch: (ch.inner[1],), 43)
    sustain(violas, 100, 104, lambda ch: (ch.inner[0],), 33)
    sustain(basses, 12, 24, lambda ch: (ch.bass,), 48)
    sustain(basses, 56, 64, lambda ch: (ch.bass,), 44)
    sustain(basses, 100, 104, lambda ch: (ch.bass,), 35)
    sustain(cellos, 100, 104, lambda ch: (ch.bass + 12,), 39)

    # Bowing changes with form: half notes, eighth-note arpeggios, a low retreat,
    # and finally sixteenth-note bursts during the dominant preparation.
    for bar in range(16, 100):
        if 56 <= bar < 60:
            continue
        for offset, length, ch in harmony_at(bar):
            if bar < 24 or 60 <= bar < 64 or bar >= 96:
                steps = [float(x) for x in range(0, int(length), 2)]
                note_length = 1.7
            elif 68 <= bar < 72:
                steps = [x * .5 for x in range(int(length * 2))]
                note_length = .40
            else:
                steps = [float(x) for x in range(int(length))]
                note_length = .78
            for i, step in enumerate(steps):
                if bar in (39, 55, 71, 87, 95, 99) and offset + step >= 7:
                    continue
                pattern = (0, 2, 1, 2, 0, 1, 2, 1)
                key = ch.upper[pattern[i % 8]]
                if 60 <= bar < 72:
                    key -= 12
                    if key < pitch("G3"):
                        key += 12  # Keep the lowered figure above the violin's G string.
                play(seconds, bar, offset + step, note_length, key,
                     43 + 27 * energy(bar) + (7 if step % 2 == 0 else 0), gate=.84)

    for bar in list(range(24, 56)) + list(range(64, 100)):
        for offset, length, ch in harmony_at(bar):
            for step in range(0, int(length), 4):
                play(basses, bar, offset + step, min(3.7, length - step),
                     ch.bass, 51 + 24 * energy(bar))
            if bar < 56 or 64 <= bar < 72 or bar >= 96:
                for step in range(0, int(length), 2):
                    key = ch.bass + 12 if step % 4 == 0 else ch.inner[0]
                    play(cellos, bar, offset + step, 1.85, key, 49 + 21 * energy(bar))

    phrase(recorder, 2, ["R:2 B4:1 E5:2 D5:1 B4:1 R:1",
                         "D5:3 B4:1 G4:2 R:2",
                         "R:2 A4:2 C#5:1 B4:1 A4:1 R:1",
                         "B4:1 E5:2 F#5:1 G5:2 R:2",
                         "F#5:2 E5:2 D#5:2 R:2", "E5:5 R:3"], lift=-12)
    phrase(recorder, 8, THEME_A[:8], lift=-2)
    phrase(oboe, 16, THEME_A[8:], octave=-1, lift=1)
    for bar, notes in {
        20: "R:6 E5:1 C#5:1", 22: "R:6 F#5:1 D#5:1",
        23: "R:6 B4:1 E5:1",
    }.items():
        phrase(flute, bar, [notes], lift=-10)

    phrase(horns, 24, HORN_THEME, gate=.92)
    sustain(firsts, 28, 32, lambda ch: (ch.upper[1] + 12,), 43)
    # Violin replies enter late in horn phrases instead of doubling every note.
    for bar, notes in {
        33: "R:4 A5:1 F#5:1 E5:1 D5:1", 35: "R:4 G5:2 D5:1 R:1",
        37: "R:4 B5:1 G5:1 F#5:1 E5:1", 39: "R:4 G5:1 F#5:1 E5:1 R:1",
    }.items():
        phrase(firsts, bar, [notes], lift=-5)

    phrase(firsts, 40, THEME_B, lift=2, gate=.98)
    sustain(horns, 40, 56, lambda ch: (ch.inner[0] + 12, ch.inner[2]), 42)
    sustain(choir, 44, 56, lambda ch: (ch.inner[0] + 12, ch.inner[1] + 12), 43)
    for bar, notes in {
        41: "R:4 B5:2 D6:1 R:1", 43: "R:4 A5:2 F#5:1 R:1",
        45: "R:4 B5:2 F#5:1 R:1", 47: "R:4 A5:1 G5:1 F#5:1 R:1",
        49: "R:4 E6:2 D6:1 C6:1", 51: "R:4 A5:2 F#5:1 R:1",
        53: "R:4 E5:1 G5:1 C6:1 R:1", 55: "R:4 F#5:1 D#5:1 B4:1 R:1",
    }.items():
        phrase(flute, bar, [notes], lift=-12)

    # Development passes fragments between different registers and instruments.
    phrase(cellos, 56, ["B2:1 E3:3 G3:2 R:2", "B3:2 G3:1 E3:1 B2:2 R:2",
                        "E3:2 G3:2 B3:2 R:2", "C4:2 B3:1 A3:1 E3:2 R:2",
                        "A3:2 F#3:2 C3:2 R:2", "E3:1 G3:3 C4:2 R:2",
                        "B2:2 E3:2 F#3:2 R:2", "D#3:2 F#3:2 B3:2 R:2"], lift=-9)
    for bar in range(56, 72):
        ch = list(harmony_at(bar))[0][2]
        if bar % 2 == 0:
            for offset, index, length in ((0, 0, 1.5), (2, 2, 2.5)):
                play(horns, bar, offset, length, ch.inner[index], 58 + (bar - 56), gate=.88)
        else:
            for offset, index in ((4, 2), (5, 1), (6, 0)):
                key = ch.upper[index]
                if key - 12 >= pitch("Bb3"):
                    key -= 12
                play(oboe, bar, offset, .9, key, 57 + (bar - 56), gate=.92)
        if bar >= 64:
            for i, index in enumerate((0, 1, 2, 1, 2, 3)):
                if bar == 71 and i >= 4:
                    continue
                line = (*ch.upper, ch.upper[0] + 12)
                play(firsts, bar, 2 + i, .85, line[index] + 12,
                     60 + 2 * (bar - 64), gate=.87)

    reprise = list(THEME_A)
    reprise[0] = "E5:2 B4:1 E5:1 G5:2 F#5:1 E5:1"
    phrase(firsts, 72, reprise, lift=5, gate=.98)
    phrase(horns, 72, HORN_THEME, lift=3, gate=.91)
    phrase(cellos, 72, COUNTER_A, lift=-3, gate=.97)
    sustain(choir, 76, 100, lambda ch: (ch.inner[0] + 12, ch.inner[1] + 12), 45)
    # A descant moves above the theme during its final eight-bar minor statement.
    phrase(flute, 80, ["G6:4 E6:2 B5:1 R:1", "F#6:3 E6:1 D6:3 R:1",
                       "E6:2 D6:1 C6:1 G5:3 R:1", "B5:4 D6:2 G6:1 R:1",
                       "E6:2 C#6:2 A5:3 R:1", "B5:2 G5:2 E6:3 R:1",
                       "B5:2 A5:2 F#5:2 D#5:1 R:1", "E6:6 R:2"], lift=-15)
    phrase(firsts, 88, SUNLIGHT_THEME, lift=7, gate=.98)
    phrase(horns, 88, SUNLIGHT_THEME, octave=-1, lift=1, gate=.91)
    phrase(cellos, 88, COUNTER_SUNLIGHT, lift=-1, gate=.97)
    phrase(flute, 88, ["G#6:4 F#6:1 E6:2 R:1", "E6:2 C#6:2 A5:3 R:1",
                       "C#6:3 B5:1 G#5:3 R:1", "D#6:4 B5:2 G#5:1 R:1",
                       "F#6:2 E6:1 C#6:1 A5:3 R:1", "B5:2 G#5:2 E6:3 R:1",
                       "B5:2 A5:2 F#5:2 D#5:1 R:1", "G#6:6 R:2"], lift=-15)

    # Short brass punctuation leaves space around the melodic lines.
    for bar in list(range(48, 56)) + list(range(68, 100)):
        e = energy(bar)
        for offset, length, ch in harmony_at(bar):
            if bar % 2 == 0 or 88 <= bar < 98:
                for key in ch.inner[:2]:
                    play(trombones, bar, offset, min(2.6, length), key,
                         51 + 27 * e, gate=.91, jitter=2)
            if (bar >= 52 and bar % 2 == 1 or bar in (72, 88, 92, 96)) and offset == 0:
                last_chord = list(harmony_at(bar))[-1][2]
                for step, index, note_length in ((4, 0, 1.25), (5.5, 1, .4), (6, 2, .9)):
                    play(trumpets, bar, step, note_length, last_chord.upper[index],
                         55 + 27 * e, gate=.84, jitter=2)

    fill_bars = (39, 47, 55, 67, 71, 79, 87, 91, 95)
    for bar in range(32, 100):
        if 56 <= bar < 64:
            continue
        e, ch = energy(bar), list(harmony_at(bar))[0][2]
        # Timpani sound at concert pitch; keep roots in a useful drum register.
        root = ch.bass + (12 if ch.bass < pitch("D2") else 0)
        for offset in ((0,) if bar < 40 else (0, 4)):
            if bar in fill_bars and offset == 4:
                continue
            play(timpani, bar, offset, 2.0, root, 45 + 30 * e, jitter=2)
        if bar >= 40:
            for offset in (0, 4):
                play(drums, bar, offset, .6, 36, 47 + 32 * e, jitter=2)
        if 48 <= bar < 56 or 68 <= bar < 96:
            for offset in (2, 6):
                if bar in fill_bars and offset == 6:
                    continue
                play(drums, bar, offset, .3, 38, 30 + 25 * e, jitter=3)
        if 80 <= bar < 96:
            for offset in (1, 3, 5, 7):
                if bar in fill_bars and offset == 7:
                    continue
                play(drums, bar, offset, .35, 54, 28 + 12 * e, jitter=2)
        if bar in fill_bars:
            for i in range(12):
                offset = 4 + i * .25  # Leave the final eighth free before arrival.
                play(drums, bar, offset, .16, 38, 31 + i * 2.4 + 13 * e, jitter=1)
                if i % 2 == 0:
                    play(timpani, bar, offset, .42, root, 43 + i * 2 + 14 * e, jitter=1)
        if bar in (40, 48, 72, 80, 88, 92, 96):
            play(drums, bar, 0, 5.5, 49, 47 + 34 * e, gate=1, jitter=0)

    phrase(firsts, 96, ["E6:4 B5:2 G#5:2", "A5:4 C#6:2 B5:2",
                        "G#5:2 F#5:1 E5:1 B4:2 E5:2", "E5:6 R:2"], gate=.98)
    phrase(horns, 96, ["E4:4 G#4:2 B4:2", "A4:4 E4:2 C#4:1 R:1",
                       "B3:2 E4:2 G#4:2 F#4:1 R:1", "E4:6 R:2"], lift=-3)
    phrase(recorder, 100, ["R:2 E5:2 C5:1 B4:1 A4:1 R:1",
                           "B4:1 E5:2 F#5:1 G5:2 R:2",
                           "F#5:2 E5:2 B4:2 R:2", "E5:5 R:3"], lift=-14)
    for i, key in enumerate(CHORDS["E5"].harp[:5]):
        play(harp, 103, i * .12, 7.2 - i * .12, key, 44 - 2 * i, gate=1, jitter=1)

    # A shared breath precedes the main return. Release every active voice,
    # including tied inner strings, before the last eighth of bar 72.
    breath_start = 71 * BAR + 7 * EIGHTH
    for track in instruments:
        track.notes = [(start, min(stop, breath_start) if start < breath_start else stop, key, vel)
                       for start, stop, key, vel in track.notes
                       if not breath_start <= start < 72 * BAR]
        track.note_count = len(track.notes)

    # CC11 swells act on sustained notes. Half-eighth sampling is smoothed by
    # only emitting changed integer values, keeping the MIDI compact.
    sustained = (cellos, violas, basses, firsts, horns, choir, trombones)
    for track in instruments:
        first = min(note[0] for note in track.notes) // (EIGHTH // 2)
        last = math.ceil(max(note[1] for note in track.notes) / (EIGHTH // 2))
        previous = None
        for step in range(first, last + 1):
            position = step / 16
            swell = 3 * math.sin(math.pi * (position % 4) / 4)
            if track in sustained:
                value = 49 + 55 * energy(position) + swell
            else:
                value = 70 + 34 * energy(position) + swell / 2
            if track in sustained and position > 103:
                value *= max(.15, 104 - position)
            value = max(1, min(127, round(value)))
            if value != previous:
                track.cc(step * (EIGHTH // 2), 11, value)
                previous = value

    return [conductor] + instruments


def main() -> None:
    render_song(
        arrange, title=TITLE,
        default_output=Path(__file__).resolve().parents[1] / "when_the_ancient_gates_awaken.mid",
        description=__doc__, details="4/4 | E minor to E major | 16 orchestral parts",
        default_duration=DEFAULT_DURATION, default_seed=DEFAULT_SEED,
    )


if __name__ == "__main__":
    main()

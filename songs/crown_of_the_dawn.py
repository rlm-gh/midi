#!/usr/bin/env python3
"""Compose Crown of the Dawn, an orchestral medieval fantasy RPG title theme.

    python3 songs/crown_of_the_dawn.py
    python3 songs/crown_of_the_dawn.py --output my_title.mid --duration 270

The 80-bar score grows from harp and recorder into a full orchestral statement.
Themes, harmony and orchestration are composed; the seed only varies the
performance. All durations in the score are eighth notes, in a lilting 12/8.
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


TITLE = "Crown of the Dawn"
BAR = 12 * EIGHTH
BARS = 80
SCORE_END = BARS * BAR
END = SCORE_END + BAR  # A measure of silence for the final orchestral release.
DEFAULT_DURATION = 252.0

# Quarter-note BPM (the dotted-quarter conducting pulse is two thirds of this).
TEMPO_CHANGES = [
    (0, 96), (4, 100), (8, 110), (16, 114), (23, 108),
    (24, 116), (28, 120), (31, 116), (32, 126), (40, 130),
    (47, 122), (48, 124), (50, 128), (52, 132), (54, 136),
    (55, 126), (56, 134), (64, 138), (68, 138), (71, 126),
    (72, 120), (74, 112), (76, 100), (77, 94), (78, 88), (79, 78),
]
SECTIONS = [
    (0, "I - The sleeping kingdom"),
    (8, "II - A traveller's promise"),
    (24, "III - The oath beneath the banners"),
    (32, "IV - Across the sunlit realm"),
    (48, "V - The gathering storm"),
    (56, "VI - Crown of the dawn"),
    (64, "VII - The gates of gold"),
    (72, "VIII - A kingdom awaits"),
    (76, "IX - The distant hills"),
]
FILL_BARS = (31, 39, 47, 55, 63, 67, 71)


@dataclass(frozen=True)
class Chord:
    bass: int
    inner: tuple[int, ...]
    upper: tuple[int, ...]
    arp: tuple[int, ...]


def chord(bass: str, inner: str, upper: str, arp: str) -> Chord:
    return Chord(pitch(bass), pitches(inner), pitches(upper), pitches(arp))


# Inversions and close inner voices let the harmony move under longer lines.
CHORDS = {
    "Dm": chord("D2", "D3 F3 A3", "D4 F4 A4", "D3 A3 D4 F4 A4 D5"),
    "Bb": chord("Bb1", "D3 F3 Bb3", "D4 F4 Bb4", "Bb2 F3 Bb3 D4 F4 Bb4"),
    "F": chord("F2", "C3 F3 A3", "C4 F4 A4", "F3 C4 F4 A4 C5 F5"),
    "C": chord("C2", "E3 G3 C4", "E4 G4 C5", "C3 G3 C4 E4 G4 C5"),
    "Gm": chord("G1", "D3 G3 Bb3", "D4 G4 Bb4", "G2 D3 G3 Bb3 D4 G4"),
    "Dm/F": chord("F2", "D3 F3 A3", "D4 F4 A4", "F3 A3 D4 F4 A4 D5"),
    "Dm/A": chord("A1", "D3 F3 A3", "D4 F4 A4", "A2 D3 A3 D4 F4 A4"),
    "Dm/C": chord("C2", "D3 F3 A3", "D4 F4 A4", "C3 A3 D4 F4 A4 D5"),
    "Em7b5": chord("E2", "D3 G3 Bb3", "D4 G4 Bb4", "E3 Bb3 D4 E4 G4 Bb4"),
    "Asus": chord("A1", "D3 E3 A3", "D4 E4 A4", "A2 E3 A3 D4 E4 A4"),
    "A": chord("A1", "C#3 E3 A3", "C#4 E4 A4", "A2 E3 A3 C#4 E4 A4"),
    "F/A": chord("A1", "C3 F3 A3", "C4 F4 A4", "A2 C3 F3 A3 C4 F4"),
    "G": chord("G1", "D3 G3 B3", "D4 G4 B4", "G2 D3 G3 B3 D4 G4"),
    "C/E": chord("E2", "E3 G3 C4", "E4 G4 C5", "E3 G3 C4 E4 G4 C5"),
    "D": chord("D2", "D3 F#3 A3", "D4 F#4 A4", "D3 A3 D4 F#4 A4 D5"),
    "A/C#": chord("C#2", "C#3 E3 A3", "C#4 E4 A4", "C#3 E3 A3 C#4 E4 A4"),
    "Bm": chord("B1", "D3 F#3 B3", "D4 F#4 B4", "B2 F#3 B3 D4 F#4 B4"),
    "F#m/A": chord("A1", "C#3 F#3 A3", "C#4 F#4 A4", "A2 C#3 F#3 A3 C#4 F#4"),
    "G/D": chord("D2", "D3 G3 B3", "D4 G4 B4", "D3 G3 B3 D4 G4 B4"),
    "D/A": chord("A1", "D3 F#3 A3", "D4 F#4 A4", "A2 D3 A3 D4 F#4 A4"),
    "D5": chord("D2", "D3 A3 D4", "D4 A4 D5", "D3 A3 D4 A4 D5 A5"),
}

INTRO_HARMONY = "Dm Dm Bb F/A Gm Dm/A Asus A".split()
A_HARMONY = "Dm Bb F C Gm Dm/F Em7b5 A Dm C Bb F/A Gm Dm/A Asus A".split()
OATH_HARMONY = "Dm Dm/C Bb F/A G Bb Asus A".split()
B_HARMONY = "F F C/E C Dm Bb Gm C F/A Bb C Dm G Bb Asus A".split()
STORM_HARMONY = "Dm Bb Gm Em7b5 Dm/A Bb Asus A".split()
MAJOR_HARMONY = "D A/C# Bm F#m/A G D/A Asus A".split()
CODA_HARMONY = "D G/D D/A D Gm Dm/A Asus D5".split()
HARMONY = (INTRO_HARMONY + A_HARMONY + OATH_HARMONY + B_HARMONY
           + STORM_HARMONY + A_HARMONY[:8] + MAJOR_HARMONY + CODA_HARMONY)

# Each string is a complete measure. R marks a rest, including breathing gaps.
THEME_A = [
    "R:1 A4:2 D5:3 E5:1 F5:2 E5:1 D5:2",
    "F5:4 D5:2 Bb4:3 R:1 D5:2",
    "C5:1 F5:2 A5:3 G5:2 F5:1 E5:1 F5:2",
    "G5:3 E5:3 D5:2 C5:2 R:2",
    "D5:2 G5:1 A5:2 G5:1 F5:2 D5:1 Bb4:2 R:1",
    "A4:3 D5:3 F5:2 E5:1 D5:2 R:1",
    "G5:3 E5:2 D5:1 Bb4:3 G4:2 R:1",
    "A4:3 C#5:2 E5:1 D5:2 C#5:1 A4:2 R:1",
    "A4:1 D5:2 F5:3 A5:3 G5:1 F5:2",
    "G5:4 E5:2 D5:3 C5:2 R:1",
    "F5:2 D5:1 Bb4:3 D5:2 F5:1 G5:1 F5:2",
    "A5:3 G5:1 F5:2 E5:2 F5:1 C5:2 R:1",
    "D5:3 G5:3 F5:2 D5:1 Bb4:2 R:1",
    "A4:1 D5:2 F5:3 E5:2 D5:1 A4:3",
    "E5:3 D5:3 A4:3 B4:2 R:1",
    "C#5:3 E5:3 A5:2 G5:1 E5:2 R:1",
]
OATH = [
    "D4:6 A3:3 D4:3", "F4:4 E4:2 D4:3 C4:3",
    "D4:3 F4:3 Bb4:3 A4:2 R:1", "A4:6 G4:3 F4:2 R:1",
    "G4:3 D4:3 B3:3 D4:3", "F4:3 D4:3 Bb3:3 D4:2 R:1",
    "E4:6 D4:3 A3:3", "C#4:3 E4:3 A4:3 R:3",
]
THEME_B = [
    "A4:3 C5:3 F5:4 E5:2",
    "F5:3 A5:3 G5:2 F5:1 C5:2 R:1",
    "E5:3 G5:3 A5:2 G5:1 E5:2 R:1",
    "D5:3 E5:3 G5:3 E5:2 R:1",
    "F5:3 A5:3 G5:2 F5:1 E5:1 D5:2",
    "F5:6 D5:3 Bb4:2 R:1",
    "D5:2 G5:1 Bb5:3 A5:2 G5:1 F5:1 D5:2",
    "E5:3 D5:3 C5:4 R:2",
    "C5:1 F5:2 A5:3 C6:3 A5:1 F5:2",
    "Bb5:3 A5:1 G5:2 F5:3 D5:2 R:1",
    "G5:3 E5:3 D5:2 E5:1 G5:3",
    "A5:6 F5:3 E5:1 D5:2",
    "B4:3 D5:3 G5:3 A5:2 R:1",
    "Bb5:3 A5:1 G5:2 F5:3 D5:2 R:1",
    "E5:3 D5:3 A4:3 D5:3",
    "C#5:6 E5:3 R:3",
]
GOLDEN_THEME = [
    "A4:1 D5:2 F#5:3 A5:3 G5:1 F#5:2",
    "E5:4 C#5:2 B4:3 A4:2 R:1",
    "F#5:2 D5:1 B4:3 D5:2 F#5:1 G5:1 F#5:2",
    "A5:3 G#5:1 F#5:2 E5:2 F#5:1 C#5:2 R:1",
    "D5:1 G5:2 B5:3 D6:3 B5:1 A5:2",
    "A5:3 F#5:3 E5:2 D5:1 A4:3",
    "E5:3 D5:3 A4:3 B4:2 R:1",
    "C#5:3 E5:3 A5:4 R:2",
]

# This lower line moves through held melody notes, becoming an independent
# cello countermelody beneath the main theme at bar 56.
COUNTER_A = [
    "F3:6 A3:3 D4:3", "D4:3 C4:3 Bb3:4 R:2",
    "A3:6 C4:3 A3:3", "G3:3 C4:3 E4:4 R:2",
    "Bb3:6 D4:3 G3:3", "F3:3 A3:3 D4:4 R:2",
    "E4:3 D4:3 Bb3:3 G3:3", "E3:3 A3:3 C#4:4 R:2",
]
COUNTER_GOLD = [
    "F#3:6 A3:3 D4:3", "E4:3 C#4:3 A3:4 R:2",
    "B3:6 D4:3 F#4:3", "C#4:3 A3:3 F#3:4 R:2",
    "B3:3 D4:3 G4:3 D4:3", "F#4:3 E4:3 D4:4 R:2",
    "A3:6 E4:3 D4:3", "C#4:3 E4:3 A3:4 R:2",
]


def energy(position: float) -> float:
    """Continuous large-scale dynamics, with room for the final reprise to grow."""
    points = [(0, .14), (4, .23), (8, .35), (16, .46), (24, .57),
              (32, .70), (40, .77), (48, .62), (52, .78), (56, .90),
              (64, .98), (68, 1.0), (72, .88), (74, .70), (76, .32), (80, .10)]
    for (left, a), (right, b) in zip(points, points[1:]):
        if position <= right:
            return a + (b - a) * (position - left) / (right - left)
    return points[-1][1]


def arrange(seed: int, transpose: int, duration: float) -> list[Track]:
    if len(HARMONY) != BARS:
        raise ValueError("Harmony must cover all 80 measures")
    rng = random.Random(seed)
    make_track = partial(Track, end_tick=END, note_end_tick=SCORE_END)
    conductor = make_track(TITLE)
    conductor.meta(0, 0x01, b"Original medieval fantasy RPG title theme; 12/8; D minor to D major")
    conductor.meta(0, 0x01, b"General MIDI 1; channel 10 percussion; nylon guitar represents lute")
    conductor.meta(0, 0x58, bytes([12, 3, 36, 8]))
    for tick, microseconds in tempo_map([(bar * BAR, bpm) for bar, bpm in TEMPO_CHANGES],
                                       end_tick=END, duration=duration):
        conductor.meta(tick, 0x51, microseconds.to_bytes(3, "big"))
    # Key signatures follow both the parallel-major arrival and CLI transposition.
    minor_keys = {0: -3, 1: 4, 2: -1, 3: -6, 4: 1, 5: -4, 6: 3, 7: -2, 8: 5, 9: 0, 10: -5, 11: 2}
    major_keys = {0: 0, 1: -5, 2: 2, 3: -3, 4: 4, 5: -1, 6: 6, 7: 1, 8: -4, 9: 3, 10: -2, 11: 5}
    tonic = (pitch("D4") + transpose) % 12
    for bar, minor in ((0, True), (64, False), (76, True)):
        sharps = (minor_keys if minor else major_keys)[tonic]
        conductor.meta(bar * BAR, 0x59, bytes([sharps & 0xFF, int(minor)]))
    for bar, label in SECTIONS:
        conductor.meta(bar * BAR, 0x06, label.encode("ascii"))

    # Each part has its own GM channel, so expression and pan remain independent.
    # Channels/programs are zero-based; only channel 9 is an unpitched drum kit.
    harp = make_track("Harp - light on the battlements", 0, 46, 94, 38, 46)
    recorder = make_track("Recorder - the traveller", 1, 74, 103, 57, 43)
    flute = make_track("Flute - wind over the realm", 2, 73, 94, 74, 45)
    oboe = make_track("Oboe - answering tales", 3, 68, 94, 49, 41)
    violins = make_track("Violins I - the royal theme", 4, 48, 95, 32, 47)
    seconds = make_track("Violins II - the onward motion", 5, 48, 81, 51, 43)
    violas = make_track("Violas - woven inner voices", 6, 48, 77, 73, 43)
    cellos = make_track("Cellos - the oath and countertheme", 7, 42, 91, 89, 40)
    basses = make_track("Contrabasses - foundations", 8, 43, 87, 69, 37)
    drums = make_track("Percussion - bass drum, snare, cymbals", 9, 0, 79, 64, 44)
    horns = make_track("French horns - banners at dawn", 10, 60, 102, 42, 48)
    trumpets = make_track("Trumpets - the golden gates", 11, 56, 78, 59, 45)
    trombones = make_track("Trombones - the ancient walls", 12, 57, 82, 78, 45)
    choir = make_track("Choir aahs - the waking kingdom", 13, 52, 73, 64, 62)
    timpani = make_track("Timpani - the gathering storm", 14, 47, 93, 81, 44)
    lute = make_track("Lute - nylon-string guitar", 15, 24, 85, 88, 32)
    instruments = [harp, recorder, flute, oboe, violins, seconds, violas, cellos,
                   basses, drums, horns, trumpets, trombones, choir, timpani, lute]

    def play(track: Track, bar: int, offset: float, length: float, key: int,
             velocity: float, *, gate: float = .92, jitter: int = 5):
        # Drum numbers select sounds, and must never follow --transpose.
        key += 0 if track is drums else transpose
        start = bar * BAR + round(offset * EIGHTH) + rng.randint(-jitter, jitter)
        track.note(start, round(length * EIGHTH * gate), key,
                   round(velocity) + rng.randint(-3, 3))

    def phrase(track: Track, start_bar: int, measures: list[str], *,
               octave: int = 0, lift: int = 0, gate: float = .95):
        for relative, measure in enumerate(measures):
            bar = start_bar + relative
            offset = 0.0
            for token in measure.split():
                name, length_text = token.split(":")
                length = float(length_text)
                if name != "R":
                    accent = 4 if offset % 3 == 0 else 0
                    play(track, bar, offset, length, pitch(name) + octave * 12,
                         62 + 27 * energy(bar) + accent + lift, gate=gate)
                offset += length
            if abs(offset - 12) > 1e-8:
                raise ValueError(f"Measure {bar + 1} has {offset} eighths; expected 12")

    def held(track: Track, first: int, last: int, keys, velocity: int):
        """Tie unchanged chord tones for up to two bars, preserving moving voices."""
        for voice in range(len(keys(CHORDS[HARMONY[first]]))):
            bar = first
            while bar < last:
                key = keys(CHORDS[HARMONY[bar]])[voice]
                stop = bar + 1
                while (stop < last and stop - bar < 2
                       and keys(CHORDS[HARMONY[stop]])[voice] == key):
                    stop += 1
                play(track, bar, .04 + voice * .015, (stop - bar) * 12 - .18,
                     key, velocity + 18 * energy(bar), gate=1, jitter=2)
                bar = stop

    # A quiet acoustic opening; plucked patterns gain motion before the strings.
    for bar, name in enumerate(HARMONY):
        ch, e = CHORDS[name], energy(bar)
        if bar < 8 or 24 <= bar < 32 or 48 <= bar < 56 or 76 <= bar < 79:
            offsets = (0, 6) if bar < 4 or bar >= 78 else (0, 3, 6, 9)
            for i, offset in enumerate(offsets):
                play(harp, bar, offset, 3.6, ch.arp[(i * 2) % 6], 45 + 19 * e, gate=1)
        elif bar % 2 == 0:
            for i, key in enumerate(ch.arp):
                play(harp, bar, i * .13, 4.5 - i * .13, key, 50 + 19 * e - i, gate=1)
        if bar in (7, 23, 31, 39, 47, 55, 63, 67, 71, 75):
            for i, index in enumerate((5, 4, 3, 2, 3, 4)):
                play(harp, bar, 9 + i * .5, 1.7, ch.arp[index], 51 + 20 * e - i)
        if 4 <= bar < 32 or 76 <= bar < 79:
            pattern = (0, 2, 3, 1, 3, 4, 0, 2, 4, 1, 3, 2)
            for i, index in enumerate(pattern):
                if bar < 8 and i % 3 == 2:
                    continue
                play(lute, bar, i, 1.8, ch.arp[index], 39 + 17 * e + (6 if i % 3 == 0 else 0))
        if bar >= 16 and bar < 76:
            # Two contrasting bow patterns, with accents on the four large beats.
            indices = (0, 1, 2, 1, 0, 1, 2, 1, 0, 2, 1, 2)
            offsets = range(12) if bar >= 24 else (0, 3, 6, 9)
            for i in offsets:
                if bar in (31, 47, 55, 71, 75) and i >= 9:
                    continue  # A shared breath before each large arrival.
                index = indices[i] if bar % 2 == 0 else indices[11 - i]
                play(seconds, bar, i, .84 if bar >= 24 else 2.2,
                     ch.upper[index], 43 + 25 * e + (7 if i % 3 == 0 else 0), gate=.80)

    # Low strings enter in stages. During the climax the cellos leave the bass
    # line to the contrabasses and sing a separately composed countertheme.
    held(cellos, 4, 24, lambda ch: (ch.bass + 12,), 48)
    held(violas, 8, 76, lambda ch: ch.inner[1:], 42)
    held(violas, 76, 80, lambda ch: (ch.inner[1],), 36)
    held(basses, 12, 24, lambda ch: (ch.bass,), 48)
    held(basses, 76, 80, lambda ch: (ch.bass,), 39)
    for bar in range(24, 76):
        ch, e = CHORDS[HARMONY[bar]], energy(bar)
        for offset in (0, 6):
            play(basses, bar, offset, 5.6, ch.bass, 58 + 20 * e, gate=.93)
        if bar < 56:
            for offset, key in ((0, ch.bass + 12), (3, ch.inner[0]),
                                (6, ch.bass + 12), (9, ch.inner[2])):
                play(cellos, bar, offset, 2.55, key, 52 + 22 * e)

    phrase(recorder, 2, ["R:6 F4:3 Bb4:2 R:1", "A4:6 C5:3 R:3"], lift=-12)
    phrase(recorder, 4, ["R:3 D5:3 A4:2 G4:1 D5:2 R:1",
                          "F5:3 E5:1 D5:2 A4:3 R:3",
                          "E5:3 D5:3 A4:3 R:3", "C#5:3 E5:3 R:6"], lift=-8)
    phrase(recorder, 8, THEME_A[:8])
    phrase(oboe, 16, THEME_A[8:], octave=-1, lift=3)
    # High flute answers fill the rests left by the lower oboe statement.
    for bar, measure in {
        17: "R:9 E5:1 D5:1 C5:1", 19: "R:9 C5:1 E5:1 F5:1",
        21: "R:9 F5:1 E5:1 D5:1", 23: "R:9 E5:1 C#5:1 A4:1",
    }.items():
        phrase(flute, bar, [measure], lift=-7)
    phrase(horns, 24, OATH, lift=1, gate=.91)
    held(violins, 24, 32, lambda ch: (ch.upper[1] + 12,), 43)
    phrase(violins, 32, THEME_B, lift=3, gate=.98)
    phrase(flute, 40, THEME_B[8:], lift=-10)
    # The winds recall the first theme underneath the second theme's long notes.
    for bar, measure in {
        33: "R:6 C4:2 A3:1 F4:2 R:1", 35: "R:6 C4:3 G3:2 R:1",
        37: "R:6 Bb3:2 D4:1 F4:2 R:1", 39: "R:6 G3:3 C4:2 R:1",
        41: "R:6 F4:3 D4:2 R:1", 43: "R:6 A3:2 D4:1 F4:2 R:1",
        45: "R:6 Bb3:3 D4:2 R:1", 47: "R:6 E4:3 C#4:2 R:1",
    }.items():
        phrase(oboe, bar, [measure], lift=-12)

    # Eight-bar development: the rising fourth becomes a terse brass call,
    # answered by climbing violins over increasingly urgent percussion.
    for relative, bar in enumerate(range(48, 56)):
        ch = CHORDS[HARMONY[bar]]
        for offset, key, length in ((0, ch.inner[0] + 12, 2),
                                    (3, ch.inner[2] + 12, 3),
                                    (7, ch.inner[1] + 12, 2)):
            play(horns, bar, offset, length, key, 71 + relative * 2, gate=.85)
        run = [key + 12 for key in ch.upper] + [ch.upper[0] + 24]
        for i, index in enumerate((0, 1, 2, 3, 2, 1)):
            play(violins, bar, 6 + i, .9, run[index], 62 + relative * 3, gate=.85)

    reprise = list(THEME_A[:8])
    reprise[0] = "D5:3 A4:1 D5:2 E5:1 F5:2 E5:1 D5:2"
    phrase(violins, 56, reprise, lift=5, gate=.98)
    phrase(horns, 56, reprise, octave=-1, lift=2, gate=.90)
    phrase(violins, 64, GOLDEN_THEME, lift=5, gate=.98)
    phrase(horns, 64, GOLDEN_THEME, octave=-1, lift=2, gate=.90)
    phrase(flute, 64, GOLDEN_THEME, lift=-12)
    phrase(cellos, 56, COUNTER_A, lift=-4, gate=.97)
    phrase(cellos, 64, COUNTER_GOLD, lift=-2, gate=.97)

    # Horn chorales in the broad middle section leave their later melody clear.
    for first, last in ((32, 40), (40, 48)):
        held(horns, first, last, lambda ch: (ch.inner[0] + 12, ch.inner[2]), 47)
    for first, last in ((36, 48), (56, 76)):
        held(choir, first, last, lambda ch: (ch.inner[1] + 12, ch.inner[2] + 12), 47)

    # Brass is reserved for structural accents and fanfare replies, keeping the
    # title melody audible when all sixteen instrumental parts are available.
    for bar in range(40, 76):
        if 48 <= bar < 52:
            continue
        ch, e = CHORDS[HARMONY[bar]], energy(bar)
        if bar % 2 == 0 or bar >= 56:
            for key in ch.inner[:2]:
                play(trombones, bar, 0, 4.8 if bar % 4 == 0 else 2.5, key, 56 + 23 * e)
            if bar >= 56:
                for key in (ch.bass + 12, ch.inner[2]):
                    play(trombones, bar, 6, 2.4, key, 54 + 22 * e)
        if bar % 2 == 1 or bar in (56, 64, 68, 72):
            # The root/third/fifth reply changes with the harmony, not a looped riff.
            for offset, index, length in ((6, 0, 1.8), (8, 1, .85), (9, 2, 2.1)):
                if bar in (47, 55, 71, 75) and offset >= 9:
                    continue
                play(trumpets, bar, offset, length, ch.upper[index], 60 + 25 * e, gate=.84)

    # Pitched timpani are separate from the GM percussion channel. The large
    # compound-meter beats use bass drum/toms; snare rolls announce arrivals.
    for bar in range(28, 76):
        ch, e = CHORDS[HARMONY[bar]], energy(bar)
        drum_root = ch.bass + (12 if ch.bass < pitch("C2") else 0)
        for offset in ((0,) if bar < 32 else (0, 6)):
            if bar in FILL_BARS and offset == 6:
                continue
            play(timpani, bar, offset, 2.7, drum_root, 51 + 29 * e)
        if bar >= 48 and bar % 2 == 1 and bar not in FILL_BARS:
            play(timpani, bar, 9, 1.7, drum_root + 7, 58 + 25 * e)
        if bar >= 32:
            for offset in (0, 6):
                play(drums, bar, offset, .6, 36, 53 + 31 * e, jitter=2)
            if bar >= 40:
                for offset in (3, 9):
                    if (bar in FILL_BARS or bar == 75) and offset == 9:
                        continue
                    play(drums, bar, offset, .45, 38, 37 + 28 * e, jitter=3)
            if 56 <= bar < 72:
                for offset in (2, 5, 8, 11):
                    if bar in FILL_BARS and offset == 11:
                        continue
                    play(drums, bar, offset, .35, 54, 29 + 8 * e, jitter=2)  # Tambourine.
        if bar in FILL_BARS:
            # The final roll leaves an eighth-note breath before the new phrase.
            for i in range(10):
                offset = 6 + i * .5
                play(drums, bar, offset, .24, 38, 35 + i * 3 + 13 * e, jitter=2)
                if i % 2 == 0:
                    play(timpani, bar, offset, .7, drum_root, 47 + i * 3 + 10 * e)
        if bar in (32, 40, 48, 56, 64, 68, 72):
            play(drums, bar, 0, 5.5, 49, 53 + 28 * e, jitter=0, gate=1)
        if bar >= 48 and bar % 4 == 2:
            for offset, key in ((9, 45), (10, 43), (11, 41)):
                play(drums, bar, offset, .5, key, 48 + 22 * e)

    # The arrival resolves in major; the borrowed minor subdominant at bar 76
    # then lets the original pastoral colour return, ending on an open fifth.
    phrase(violins, 72, ["D6:6 A5:3 F#5:3", "G5:6 B5:3 A5:3",
                         "F#5:3 E5:3 D5:3 A4:3", "D5:9 R:3"], lift=-1, gate=.98)
    phrase(horns, 72, ["D4:6 F#4:3 A4:3", "G4:6 D4:3 B3:3",
                       "A3:3 D4:3 F#4:3 E4:3", "D4:9 R:3"], lift=-2)
    held(cellos, 72, 80, lambda ch: (ch.bass + 12,), 46)
    phrase(recorder, 76, ["R:3 D5:3 A4:2 G4:1 D5:2 R:1",
                          "F5:3 E5:1 D5:2 A4:3 R:3",
                          "E5:3 D5:3 A4:3 R:3", "D5:9 R:3"], lift=-12)
    # The final harp chord rings naturally into the release measure.
    for i, key in enumerate(CHORDS["D5"].arp[:5]):
        play(harp, 79, .12 * i, 10 - .12 * i, key, 48 - i * 2, gate=1, jitter=2)

    # CC11 changes shape held notes as well as new attacks. Interpolated samples
    # every half eighth avoid abrupt bar-by-bar volume jumps in sustained parts.
    sustained = (violins, violas, cellos, basses, horns, trombones, choir)
    for track in instruments:
        first = max(0, min(note[0] for note in track.notes) // BAR)
        last = min(BARS, math.ceil(max(note[1] for note in track.notes) / BAR))
        for half_eighth in range(first * 24, last * 24 + 1):
            position = half_eighth / 24
            swell = 4 * math.sin(math.pi * (position % 2) / 2) if track in sustained else 0
            base, depth = (48, 57) if track in sustained else (67, 38)
            value = round(base + depth * energy(position) + swell)
            if position > 79.25 and track in sustained:
                value = round(value * max(.18, (80 - position) / .75))
            track.cc(half_eighth * (EIGHTH // 2), 11, max(1, min(127, value)))

    return [conductor] + instruments


def main() -> None:
    render_song(
        arrange, title=TITLE,
        default_output=Path(__file__).resolve().parents[1] / "crown_of_the_dawn.mid",
        description=__doc__, details="12/8 | D minor to D major | 16 orchestral parts",
        default_duration=DEFAULT_DURATION, default_seed=23,
    )


if __name__ == "__main__":
    main()

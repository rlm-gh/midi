#!/usr/bin/env python3
"""Generate an original, General MIDI fantasy title theme using only Python.

    python3 create_music.py
    python3 create_music.py --output another_journey.mid --duration 210 --seed 12

The score is hand-composed. The seed changes performance timing and dynamics,
not the tune. Edit CHORDS, the melody phrases, or arrange() to compose new music.
Tempo is expressed in quarter notes per minute, including in this 6/8 score.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import random
import struct


TITLE = "Beyond the Sleeping Hills"
PPQ = 480
EIGHTH = PPQ // 2
BAR = 6 * EIGHTH
BARS = 72
END = (BARS + 1) * BAR  # One extra measure lets the instruments release.


def pitch(name: str) -> int:
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    accidental = (1 if "#" in name else -1 if "b" in name else 0)
    return 12 * (int(name[-1]) + 1) + semitones[name[0]] + accidental


def pitches(names: str) -> tuple[int, ...]:
    return tuple(pitch(name) for name in names.split())


@dataclass(frozen=True)
class Chord:
    bass: int
    strings: tuple[int, ...]
    lute: tuple[int, ...]
    harp: tuple[int, ...]


def chord(bass: str, strings: str, lute: str, harp: str) -> Chord:
    return Chord(pitch(bass), pitches(strings), pitches(lute), pitches(harp))


CHORDS = {
    "Dm9": chord("D2", "F3 A3 D4 E4", "D3 A3 D4 F4 A4 E5", "D4 A4 D5 E5 F5 A5"),
    "C6": chord("C2", "G3 A3 C4 E4", "C3 G3 C4 E4 G4 A4", "C4 G4 C5 D5 E5 G5"),
    "G6": chord("G2", "G3 B3 D4 E4", "G3 B3 D4 G4 B4 E5", "G3 D4 G4 B4 D5 E5"),
    "Am7": chord("A2", "G3 A3 C4 E4", "A3 C4 E4 G4 A4 E5", "A3 E4 A4 C5 E5 G5"),
    "Fmaj7": chord("F2", "F3 A3 C4 E4", "F3 A3 C4 E4 A4 C5", "F3 C4 F4 A4 C5 E5"),
    "Em7": chord("E2", "G3 B3 D4 E4", "E3 B3 D4 G4 B4 E5", "E4 G4 B4 D5 E5 G5"),
    "Asus": chord("A2", "E3 A3 D4 E4", "A3 D4 E4 A4 D5 E5", "A3 E4 A4 D5 E5 A5"),
    "Dsus": chord("D2", "G3 A3 D4 E4", "D3 A3 D4 G4 A4 E5", "D4 A4 D5 E5 G5 A5"),
    "D5add9": chord("D2", "D3 A3 D4 E4", "D3 A3 D4 E4 A4 D5", "D4 A4 D5 E5 A5 D6"),
    "D5": chord("D2", "D3 A3 D4 A4", "D3 A3 D4 A4 D5 A5", "D4 A4 D5 A5 D6 A6"),
}

INTRO_HARMONY = "Dm9 Dm9 C6 C6 G6 G6 Dsus Dm9".split()
A_HARMONY = "Dm9 Dm9 C6 C6 G6 G6 Dm9 Am7 Fmaj7 C6 G6 Am7 Dm9 C6 Asus Dm9".split()
B_HARMONY = "Fmaj7 Fmaj7 C6 C6 G6 G6 Am7 Am7 Fmaj7 C6 G6 Em7 Dm9 G6 Asus Dm9".split()
CODA_HARMONY = "Dm9 C6 G6 Am7 Fmaj7 C6 Asus Dm9 Dm9 C6 G6 G6 Dsus Dm9 D5add9 D5".split()
HARMONY = INTRO_HARMONY + A_HARMONY + B_HARMONY + A_HARMONY + CODA_HARMONY

# Each item is one measure; lengths are eighth notes. R is a breathing rest.
# The main idea rises A-D-E-F, then falls gently back towards D.
THEME_A = [
    "R:1 A4:1 D5:2 E5:1 F5:1",
    "F5:3 E5:1 D5:2",
    "E5:2 G5:1 E5:1 D5:1 C5:1",
    "G4:1 C5:2 D5:1 E5:1 R:1",
    "D5:2 G5:2 A5:1 G5:1",
    "B4:2 D5:1 E5:1 D5:1 R:1",
    "A4:1 D5:2 F5:1 E5:1 D5:1",
    "C5:2 B4:1 A4:2 R:1",
    "A4:1 C5:1 F5:2 G5:1 A5:1",
    "G5:3 E5:1 D5:1 C5:1",
    "B4:1 D5:1 G5:2 E5:1 D5:1",
    "E5:2 C5:1 B4:1 A4:1 R:1",
    "A4:1 D5:2 E5:1 F5:1 A5:1",
    "G5:2 E5:2 D5:1 C5:1",
    "E5:2 D5:1 A4:2 R:1",
    "D5:4 R:2",
]

# The middle section begins on a lower reed, opening into the upper recorder.
THEME_B_LOW = [
    "R:1 A3:1 C4:1 E4:1 F4:2",
    "E4:1 F4:1 A4:2 G4:1 F4:1",
    "E4:3 D4:1 C4:2",
    "G3:1 C4:1 D4:1 E4:2 R:1",
    "B3:1 D4:1 G4:2 F4:1 E4:1",
    "D4:2 B3:1 A3:1 G3:1 R:1",
    "A3:1 C4:1 E4:2 G4:1 E4:1",
    "C4:3 B3:1 A3:1 R:1",
]
THEME_B_HIGH = [
    "C5:1 F5:2 G5:1 A5:2",
    "G5:2 E5:1 D5:1 C5:1 R:1",
    "D5:1 G5:2 A5:1 B5:1 A5:1",
    "G5:2 E5:1 D5:1 B4:1 R:1",
    "A4:1 D5:1 F5:2 E5:1 D5:1",
    "B4:1 D5:1 G5:2 E5:1 D5:1",
    "E5:2 D5:2 A4:1 R:1",
    "D5:4 R:2",
]

CODA = [
    "R:1 A4:1 D5:2 E5:1 F5:1",
    "E5:2 G5:1 E5:1 D5:1 C5:1",
    "B4:1 D5:1 G5:2 E5:1 D5:1",
    "C5:2 B4:1 A4:2 R:1",
    "A4:1 C5:1 F5:2 E5:1 C5:1",
    "E5:3 D5:1 C5:1 R:1",
    "D5:2 E5:1 D5:1 A4:1 R:1",
    "D5:4 R:2",
    "R:2 A4:1 D5:2 E5:1",
    "E5:2 D5:1 C5:2 R:1",
    "B4:2 D5:1 E5:2 R:1",
    "D5:3 B4:2 R:1",
    "A4:2 D5:2 E5:1 R:1",
    "F5:2 E5:1 D5:2 R:1",
    "E5:3 D5:2 R:1",
    "D5:4 R:2",
]


def vlq(value: int) -> bytes:
    """Standard MIDI variable-length quantity."""
    if not 0 <= value <= 0x0FFFFFFF:
        raise ValueError(f"Invalid MIDI delta time: {value}")
    result = [value & 0x7F]
    while value >> 7:
        value >>= 7
        result.insert(0, (value & 0x7F) | 0x80)
    return bytes(result)


class Track:
    def __init__(self, name: str, channel: int | None = None, program: int = 0,
                 volume: int = 90, pan: int = 64, reverb: int = 38):
        self.channel = channel
        self.events: list[tuple[int, int, bytes]] = []
        self.notes: list[tuple[int, int, int, int]] = []
        self.note_count = 0
        self.meta(0, 0x03, name.encode("utf-8"))
        if channel is not None:
            self.cc(0, 0, 0)  # General MIDI bank.
            self.cc(0, 32, 0)
            self.events.append((0, 2, bytes([0xC0 | channel, program])))
            for controller, value in ((7, volume), (10, pan), (11, 90),
                                      (91, reverb), (93, 0)):
                self.cc(0, controller, value)

    def meta(self, tick: int, kind: int, payload: bytes):
        self.events.append((tick, 0, b"\xff" + bytes([kind]) + vlq(len(payload)) + payload))

    def cc(self, tick: int, controller: int, value: int):
        if self.channel is None:
            raise ValueError("Controller requires an instrument channel")
        self.events.append((tick, 3, bytes([0xB0 | self.channel, controller, value])))

    def note(self, tick: int, duration: int, key: int, velocity: int):
        if self.channel is None or not 0 <= key <= 127:
            raise ValueError("Invalid channel or pitch")
        start = max(0, int(tick))
        stop = min(BARS * BAR, start + max(1, int(duration)))
        if stop <= start:
            raise ValueError("Note starts after the score ends")
        velocity = max(1, min(127, int(velocity)))
        self.notes.append((start, stop, key, velocity))
        self.note_count += 1

    def encode(self) -> bytes:
        events = list(self.events)
        if self.channel is not None:
            # A rearticulated pitch must release its previous note first.
            # This also handles small overlaps introduced by humanized timing.
            for key in sorted({note[2] for note in self.notes}):
                notes = sorted(note for note in self.notes if note[2] == key)
                for i, (start, stop, _, velocity) in enumerate(notes):
                    if i + 1 < len(notes):
                        stop = min(stop, notes[i + 1][0])
                    if stop <= start:
                        continue
                    events.append((start, 5, bytes([0x90 | self.channel, key, velocity])))
                    events.append((stop, 1, bytes([0x80 | self.channel, key, 0])))
            # Explicit cleanup follows the release measure.
            events.extend((END, 3, bytes([0xB0 | self.channel, c, 0])) for c in (64, 123))
        events.append((END, 99, b"\xff\x2f\x00"))
        result = bytearray()
        previous = 0
        for tick, _, message in sorted(events, key=lambda event: (event[0], event[1])):
            result.extend(vlq(tick - previous))
            result.extend(message)
            previous = tick
        return b"MTrk" + struct.pack(">I", len(result)) + result


def energy(bar: int) -> float:
    if bar < 8:
        return 0.32 + 0.04 * bar
    if bar < 24:
        return 0.64 + 0.09 * ((bar - 8) % 8) / 7
    if bar < 32:
        return 0.67
    if bar < 40:
        return 0.78 + 0.08 * (bar - 32) / 7
    if bar < 56:
        return 0.82 - 0.08 * (bar - 40) / 15
    return max(0.20, 0.69 - 0.034 * (bar - 56))


def tempo_map(duration: float) -> list[tuple[int, int]]:
    """Scale a modest rubato curve to the requested total playback duration."""
    changes = [(0, 70), (4, 72), (8, 74), (22, 71), (24, 73),
               (32, 76), (38, 72), (40, 74), (54, 70), (56, 72),
               (62, 69), (64, 68), (68, 65), (69, 63), (70, 60), (71, 57)]
    natural_seconds = 0.0
    for i, (bar, bpm) in enumerate(changes):
        next_bar = changes[i + 1][0] if i + 1 < len(changes) else BARS + 1
        natural_seconds += (next_bar - bar) * 3 * 60 / bpm
    scale = duration / natural_seconds
    return [(bar * BAR, round(60_000_000 / bpm * scale)) for bar, bpm in changes]


def arrange(seed: int, transpose: int, duration: float) -> list[Track]:
    if len(HARMONY) != BARS:
        raise ValueError("Harmony must cover the entire score")
    rng = random.Random(seed)
    conductor = Track(TITLE)
    conductor.meta(0, 0x01, b"Original fantasy CRPG title theme; D Dorian; gently in 6/8")
    conductor.meta(0, 0x01, b"GM instruments; nylon guitar stands in for lute")
    conductor.meta(0, 0x58, bytes([6, 3, 36, 8]))
    for tick, microseconds in tempo_map(duration):
        conductor.meta(tick, 0x51, microseconds.to_bytes(3, "big"))
    for bar, label in ((0, "I - Mist on the hills"), (8, "II - The road calls"),
                       (24, "III - Beyond the gate"), (40, "IV - A promise of adventure"),
                       (56, "V - The quiet horizon"), (64, "VI - Waiting for dawn")):
        conductor.meta(bar * BAR, 0x06, label.encode("ascii"))

    # Program numbers here are zero-based, as required in the MIDI byte stream.
    recorder = Track("Recorder - the traveller's theme", 0, 74, 108, 70, 44)
    lute = Track("Lute - nylon-string guitar", 1, 24, 103, 40, 30)
    harp = Track("Harp - distant light", 2, 46, 97, 88, 48)
    strings = Track("Soft strings - sustained inner voices", 3, 48, 90, 58, 49)
    cello = Track("Cello - warm foundations", 4, 42, 100, 62, 38)
    reed = Track("English horn - the answering voice", 5, 69, 99, 52, 42)
    horn = Track("French horn - the far horizon", 6, 60, 85, 78, 52)
    instruments = [recorder, lute, harp, strings, cello, reed, horn]

    def play(track: Track, bar: int, offset: float, length: float, key: int,
             velocity: float, jitter: int = 8, gate: float = 0.91):
        tick = bar * BAR + round(offset * EIGHTH) + rng.randint(-jitter, jitter)
        track.note(tick, round(length * EIGHTH * gate), key + transpose,
                   round(velocity) + 7 + rng.randint(-3, 3))

    def phrase(track: Track, first_bar: int, measures: list[str], lift: int = 0):
        for relative, measure in enumerate(measures):
            bar = first_bar + relative
            offset = 0.0
            for token in measure.split():
                name, length_text = token.split(":")
                length = float(length_text)
                if name != "R":
                    accent = 3 if offset in (0, 3) else 0
                    velocity = 53 + 20 * energy(bar) + accent + lift
                    # Long notes breathe before the next gesture.
                    play(track, bar, offset, length, pitch(name), velocity,
                         jitter=6, gate=0.90 if length >= 3 else 0.94)
                offset += length
            if abs(offset - 6) > 1e-8:
                raise ValueError(f"Measure {bar + 1} has {offset} eighths, expected 6")

    for bar in range(BARS):
        e = energy(bar)
        for track in instruments:
            base = 70 if track is strings else 78
            expression = round(base + 23 * e)
            track.cc(bar * BAR, 11, expression)
            # Gentle sustained swells inside the two dotted-quarter pulses.
            if track in (strings, reed, horn):
                track.cc(bar * BAR + 2 * EIGHTH, 11, min(127, expression + 4))
                track.cc(bar * BAR + 5 * EIGHTH, 11, max(30, expression - 2))

        ch = CHORDS[HARMONY[bar]]
        # Arpeggios leave room at the opening and become sparse at the close.
        if bar < 2:
            pattern = [(0, 0), (3, 2)]
        elif bar < 4 or bar >= 68:
            pattern = [(0, 0), (2, 2), (3, 1), (5, 3)]
        elif bar % 4 == 3:
            pattern = [(0, 0), (1, 2), (2, 3), (3, 1), (4, 2)]
        else:
            indices = (0, 2, 3, 1, 4, 2) if bar % 2 == 0 else (0, 2, 4, 1, 3, 2)
            pattern = list(enumerate(indices))
        if bar == 71:
            pattern = [(0, 0), (0.08, 1), (0.16, 2), (0.24, 3)]
        for offset, index in pattern:
            accent = 7 if offset == 0 else 3 if offset == 3 else 0
            play(lute, bar, offset, 2.0 if bar < 68 else 2.7,
                 ch.lute[index], 39 + 17 * e + accent, jitter=9, gate=0.98)

        # Harp appears at phrase boundaries, with a few answering cascades.
        if bar in (0, 4, 8, 16, 24, 32, 40, 48, 56, 64, 68, 70):
            for i in range(4):
                play(harp, bar, i * 0.11, 3.0, ch.harp[i],
                     40 + 12 * e - 2 * i, jitter=3, gate=1.0)
        elif bar in (7, 15, 23, 31, 39, 47, 55, 63):
            for offset, index in ((3, 4), (4, 3), (5, 1)):
                play(harp, bar, offset, 1.8, ch.harp[index], 43 + 13 * e)
        elif 8 <= bar < 64 and bar % 4 == 2:
            play(harp, bar, 3.5, 2.2, ch.harp[3], 37 + 12 * e)

    # Tie sustained common tones across chord boundaries. This avoids a pad
    # being retriggered on every bar and keeps the background moving smoothly.
    for voice in range(4):
        start_bar = 0 if voice in (1, 2) else 4
        bar = start_bar
        while bar < BARS:
            key = CHORDS[HARMONY[bar]].strings[voice]
            next_bar = bar + 1
            while (next_bar < BARS and next_bar - bar < 4
                   and CHORDS[HARMONY[next_bar]].strings[voice] == key):
                next_bar += 1
            start = bar * BAR + 12 + voice * 7
            stop = next_bar * BAR - 14
            if next_bar == BARS:
                stop -= EIGHTH // 2
            strings.note(start, stop - start, key + transpose,
                         round(41 + energy(bar) * 15) + rng.randint(-2, 2))
            bar = next_bar

    # A bowed, occasionally held bass; higher fifths answer at two cadences.
    bar = 0
    while bar < BARS:
        key = CHORDS[HARMONY[bar]].bass
        next_bar = bar + 1
        while (next_bar < BARS and next_bar - bar < 2
               and CHORDS[HARMONY[next_bar]].bass == key):
            next_bar += 1
        cello.note(bar * BAR + 5, (next_bar - bar) * BAR - 65,
                   key + transpose, round(51 + 16 * energy(bar)))
        bar = next_bar

    phrase(recorder, 4, ["R:3 B4:1 D5:2", "G5:3 D5:2 R:1",
                        "E5:2 D5:1 A4:2 R:1", "D5:3 R:3"], lift=-8)
    phrase(recorder, 8, THEME_A)
    phrase(reed, 24, THEME_B_LOW, lift=-5)
    phrase(recorder, 32, THEME_B_HIGH, lift=1)

    reprise = list(THEME_A)
    reprise[1] = "F5:2 A5:1 G5:1 E5:1 D5:1"
    reprise[3] = "C5:2 E5:1 G5:2 R:1"
    reprise[8] = "C5:1 F5:2 G5:1 A5:2"
    reprise[12] = "D5:1 F5:1 A5:2 G5:1 F5:1"
    phrase(recorder, 40, reprise, lift=2)
    phrase(recorder, 56, CODA, lift=-4)

    # Short lower-voice replies occupy gaps and selected held melody notes.
    answers = {
        11: "R:3 G3:1 C4:1 E4:1",
        15: "R:3 E4:1 C4:1 A3:1",
        19: "R:3 E4:1 C4:1 A3:1",
        23: "R:3 A3:1 D4:2",
        35: "R:3 B3:1 D4:1 E4:1",
        39: "R:3 A3:1 D4:2",
        43: "R:3 G3:1 C4:1 E4:1",
        47: "R:3 E4:1 C4:1 A3:1",
        51: "R:3 E4:1 C4:1 A3:1",
        55: "R:3 A3:1 D4:2",
        59: "R:3 E4:1 C4:1 A3:1",
        63: "R:3 A3:1 D4:2",
    }
    for bar, measure in answers.items():
        phrase(reed, bar, [measure], lift=-14)

    # A very soft horn broadens the centre and return, without percussion.
    for bar, names in ((32, "F3 C4"), (34, "G3 D4"), (36, "D3 A3"),
                       (38, "A3 E4"), (40, "D3 A3"), (42, "C3 G3"),
                       (44, "G3 D4"), (46, "D3 A3"), (48, "F3 C4"),
                       (50, "G3 D4"), (52, "D3 A3"), (54, "A3 E4")):
        # Only the chord at this measure is sustained; the next change breathes.
        for key in pitches(names):
            play(horn, bar, 0.12, 5.5, key, 37 + 9 * energy(bar), jitter=4)

    return [conductor] + instruments


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().with_name("beyond_the_sleeping_hills.mid"))
    parser.add_argument("--duration", type=float, default=180.0,
                        help="Total duration in seconds, including the release tail (default: 180)")
    parser.add_argument("--seed", type=int, default=17,
                        help="Reproducible performance variation (default: 17)")
    parser.add_argument("--transpose", type=int, default=0,
                        help="Transpose all instruments in semitones, -12 through 12")
    args = parser.parse_args()
    if not 30 <= args.duration <= 1800:
        parser.error("--duration must be between 30 and 1800 seconds")
    if not -12 <= args.transpose <= 12:
        parser.error("--transpose must be between -12 and 12")
    tracks = arrange(args.seed, args.transpose, args.duration)
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ)
    data = header + b"".join(track.encode() for track in tracks)
    args.output.write_bytes(data)
    print(f"Created {args.output.resolve()}")
    print(f"{TITLE} | {args.duration:.2f} seconds | 6/8 | D Dorian"
          + (f" transposed {args.transpose:+d}" if args.transpose else ""))
    print(f"Standard MIDI File type 1 | {len(tracks)} tracks | "
          f"{sum(t.note_count for t in tracks)} notes | {len(data):,} bytes")


if __name__ == "__main__":
    main()

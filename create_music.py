#!/usr/bin/env python3
"""Reusable MIDI encoding, timing, and command-line helpers for song scripts.

Songs define their own notes, instruments, arrangement, and tempo curve, then
call render_song() to write a Standard MIDI File using only Python.
Tempo is expressed in quarter notes per minute.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from pathlib import Path
import struct


PPQ = 480
EIGHTH = PPQ // 2


def pitch(name: str) -> int:
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    accidental = (1 if "#" in name else -1 if "b" in name else 0)
    return 12 * (int(name[-1]) + 1) + semitones[name[0]] + accidental


def pitches(names: str) -> tuple[int, ...]:
    return tuple(pitch(name) for name in names.split())


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
    """A MIDI track with explicit score and playback end ticks.

    Notes are clipped at note_end_tick; end_tick includes any release tail.
    Program numbers are zero-based General MIDI program numbers.
    """

    def __init__(self, name: str, channel: int | None = None, program: int = 0,
                 volume: int = 90, pan: int = 64, reverb: int = 38, *,
                 end_tick: int, note_end_tick: int | None = None):
        self.end_tick = end_tick
        self.note_end_tick = end_tick if note_end_tick is None else note_end_tick
        if not 0 < self.note_end_tick <= self.end_tick:
            raise ValueError("Expected 0 < note_end_tick <= end_tick")
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
        stop = min(self.note_end_tick, start + max(1, int(duration)))
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
            # Explicit cleanup follows the release tail.
            events.extend((self.end_tick, 3, bytes([0xB0 | self.channel, c, 0])) for c in (64, 123))
        events.append((self.end_tick, 99, b"\xff\x2f\x00"))
        result = bytearray()
        previous = 0
        for tick, _, message in sorted(events, key=lambda event: (event[0], event[1])):
            result.extend(vlq(tick - previous))
            result.extend(message)
            previous = tick
        return b"MTrk" + struct.pack(">I", len(result)) + result


def tempo_map(changes: Sequence[tuple[int, float]], *, end_tick: int,
              duration: float, ppq: int = PPQ) -> list[tuple[int, int]]:
    """Scale (tick, BPM) changes to a total duration, including the release tail."""
    if not changes or changes[0][0] != 0:
        raise ValueError("Tempo changes must start at tick 0")
    if duration <= 0 or ppq <= 0:
        raise ValueError("Duration and ticks per quarter note must be positive")
    natural_seconds = 0.0
    for i, (tick, bpm) in enumerate(changes):
        next_tick = changes[i + 1][0] if i + 1 < len(changes) else end_tick
        if bpm <= 0 or not 0 <= tick < next_tick <= end_tick:
            raise ValueError("Tempos must be positive and ticks increasing before end_tick")
        natural_seconds += (next_tick - tick) / ppq * 60 / bpm
    scale = duration / natural_seconds
    result = [(tick, round(60_000_000 / bpm * scale)) for tick, bpm in changes]
    if any(not 1 <= microseconds <= 0xFFFFFF for _, microseconds in result):
        raise ValueError("Requested duration exceeds the MIDI tempo range")
    return result


def encode_midi(tracks: Sequence[Track], *, ppq: int = PPQ) -> bytes:
    """Encode tracks as a Standard MIDI File, type 1."""
    if not 1 <= len(tracks) <= 0xFFFF:
        raise ValueError("A MIDI file requires between 1 and 65535 tracks")
    if not 1 <= ppq <= 0x7FFF:
        raise ValueError("Ticks per quarter note must be between 1 and 32767")
    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), ppq)
    return header + b"".join(track.encode() for track in tracks)


def render_song(arrange: Callable[[int, int, float], Sequence[Track]], *,
                title: str, default_output: Path, description: str | None = None,
                details: str = "", default_duration: float = 180.0,
                default_seed: int = 17, ppq: int = PPQ,
                argv: Sequence[str] | None = None) -> None:
    """Run a song's CLI; arrange(seed, transpose, duration) supplies its tracks."""
    parser = argparse.ArgumentParser(description=description or title,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--duration", type=float, default=default_duration,
                        help="Total duration in seconds, including the release tail "
                             f"(default: {default_duration:g})")
    parser.add_argument("--seed", type=int, default=default_seed,
                        help=f"Reproducible performance variation (default: {default_seed})")
    parser.add_argument("--transpose", type=int, default=0,
                        help="Transpose all instruments in semitones, -12 through 12")
    args = parser.parse_args(argv)
    if not 30 <= args.duration <= 1800:
        parser.error("--duration must be between 30 and 1800 seconds")
    if not -12 <= args.transpose <= 12:
        parser.error("--transpose must be between -12 and 12")
    tracks = arrange(args.seed, args.transpose, args.duration)
    data = encode_midi(tracks, ppq=ppq)
    args.output.write_bytes(data)
    print(f"Created {args.output.resolve()}")
    print(f"{title} | {args.duration:.2f} seconds"
          + (f" | {details}" if details else "")
          + (f" transposed {args.transpose:+d}" if args.transpose else ""))
    print(f"Standard MIDI File type 1 | {len(tracks)} tracks | "
          f"{sum(t.note_count for t in tracks)} notes | {len(data):,} bytes")

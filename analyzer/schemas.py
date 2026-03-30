from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class InputAsset:
    assetId: str
    taskId: str
    path: str
    type: str
    durationSec: float | None = None
    sampleRate: int | None = None
    channels: int | None = None
    sourceLabel: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StemCandidate:
    stemId: str
    taskId: str
    versionId: str
    sourceAssetId: str
    stemType: str
    path: str
    durationSec: float | None = None
    qualityScore: float | None = None
    selectionReason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Measure:
    index: int
    start: float
    end: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TimingGrid:
    timingGridId: str
    taskId: str
    versionId: str
    sourceStemId: str
    tempo: float
    selectedTimeSignature: str
    beats: list[float]
    measures: list[Measure]
    timeSignatureCandidates: list[str] = field(default_factory=list)
    downbeats: list[float] = field(default_factory=list)
    grooveLabel: str | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["measures"] = [measure.to_dict() for measure in self.measures]
        return payload


@dataclass(slots=True)
class DetailedNote:
    noteId: str
    taskId: str
    versionId: str
    start: float
    end: float
    midiPitch: int
    measureIndex: int
    beatOffset: float
    durationBeats: float
    phraseId: str | None = None
    parentBackboneId: str | None = None
    noteClass: str = "backbone"
    confidence: float | None = None
    stringCandidate: int | None = None
    fretCandidate: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["id"] = self.noteId
        return payload


@dataclass(slots=True)
class NotationCandidate:
    notationId: str
    taskId: str
    versionId: str
    timingGridId: str
    noteIds: list[str]
    phraseIds: list[str] = field(default_factory=list)
    fingeringId: str | None = None
    tabRepresentation: dict[str, Any] = field(default_factory=dict)
    staffRepresentation: dict[str, Any] = field(default_factory=dict)
    exportPaths: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

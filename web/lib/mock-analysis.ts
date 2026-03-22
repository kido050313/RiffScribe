import type { AnalysisResult } from "../types/analysis";

export const mockAnalysis: AnalysisResult = {
  sourceName: "sample-funk-01.wav",
  durationSec: 32.4,
  bpm: 96,
  timeSignature: {
    numerator: 4,
    denominator: 4,
  },
  beats: [0, 0.625, 1.25, 1.875, 2.5, 3.125, 3.75, 4.375],
  measures: [
    {
      index: 0,
      start: 0,
      end: 2.5,
    },
    {
      index: 1,
      start: 2.5,
      end: 5.0,
    },
  ],
  notes: [
    {
      id: "n1",
      start: 0.45,
      end: 0.72,
      midiPitch: 64,
      durationBeats: 0.5,
      measureIndex: 0,
      beatOffset: 0.75,
      stringCandidate: 2,
      fretCandidate: 5,
    },
    {
      id: "n2",
      start: 0.82,
      end: 1.18,
      midiPitch: 66,
      durationBeats: 0.5,
      measureIndex: 0,
      beatOffset: 1.25,
      stringCandidate: 2,
      fretCandidate: 7,
    },
    {
      id: "n3",
      start: 1.3,
      end: 1.9,
      midiPitch: 69,
      durationBeats: 1,
      measureIndex: 0,
      beatOffset: 2,
      stringCandidate: 1,
      fretCandidate: 5,
    },
  ],
};

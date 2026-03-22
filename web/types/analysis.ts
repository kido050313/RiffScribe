export type NoteEvent = {
  id: string;
  start: number;
  end: number;
  midiPitch: number;
  durationBeats: number;
  measureIndex: number;
  beatOffset: number;
  stringCandidate?: number;
  fretCandidate?: number;
};

export type Measure = {
  index: number;
  start: number;
  end: number;
};

export type TimeSignature = {
  numerator: number;
  denominator: number;
};

export type AnalysisResult = {
  sourceName: string;
  durationSec: number;
  bpm: number;
  timeSignature: TimeSignature;
  beats: number[];
  measures: Measure[];
  notes: NoteEvent[];
};

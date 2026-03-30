export type EntityId = string;

export type InputAsset = {
  assetId: EntityId;
  taskId: EntityId;
  path: string;
  type: "video" | "audio";
  durationSec?: number;
  sampleRate?: number;
  channels?: number;
  sourceLabel?: string;
  metadata?: Record<string, unknown>;
};

export type StemType = "extracted" | "other" | "vocals" | "bass" | "drums";

export type StemCandidate = {
  stemId: EntityId;
  taskId: EntityId;
  versionId: EntityId;
  sourceAssetId: EntityId;
  stemType: StemType;
  path: string;
  durationSec?: number;
  qualityScore?: number;
  selectionReason?: string;
};

export type Measure = {
  index: number;
  start: number;
  end: number;
};

export type TimingGrid = {
  timingGridId: EntityId;
  taskId: EntityId;
  versionId: EntityId;
  sourceStemId: EntityId;
  tempo: number;
  timeSignatureCandidates?: string[];
  selectedTimeSignature: string;
  beats: number[];
  downbeats?: number[];
  measures: Measure[];
  grooveLabel?: string;
  confidence?: number;
};

export type PhraseSegment = {
  phraseId: EntityId;
  taskId: EntityId;
  versionId: EntityId;
  sourceStemId: EntityId;
  start: number;
  end: number;
  measureRange?: [number, number];
  pauseBefore?: number;
  pauseAfter?: number;
  densityScore?: number;
  roleTag?: string;
};

export type DetailedNote = {
  noteId: EntityId;
  id: EntityId;
  taskId: EntityId;
  versionId: EntityId;
  phraseId?: EntityId | null;
  parentBackboneId?: EntityId | null;
  start: number;
  end: number;
  midiPitch: number;
  measureIndex: number;
  beatOffset: number;
  durationBeats: number;
  noteClass: "backbone" | "passing" | "ornament" | "noise_candidate";
  confidence?: number;
  stringCandidate?: number | null;
  fretCandidate?: number | null;
};

export type NotationCandidate = {
  notationId: EntityId;
  taskId: EntityId;
  versionId: EntityId;
  timingGridId: EntityId;
  phraseIds?: EntityId[];
  noteIds: EntityId[];
  fingeringId?: EntityId | null;
  tabRepresentation?: Record<string, unknown>;
  staffRepresentation?: Record<string, unknown>;
  exportPaths?: Record<string, string>;
};

export type EvaluationReport = {
  reportId: EntityId;
  schemaVersion: string;
  taskId: EntityId;
  versionId: EntityId;
  notationId: EntityId;
  analysisPath: string;
  input: {
    assetPath?: string;
    assetType?: string;
    durationSec?: number;
    selectedStem?: string;
    sourceName?: string;
  };
  candidate: {
    candidateId: EntityId;
    analysisPath: string;
    noteCount: number;
    measureCount: number;
    beatCount: number;
    tempo?: number;
    timeSignature: string;
  };
  overall: {
    score: number;
    confidence?: number;
    rankHint?: string;
    summary?: string;
  };
  metrics: {
    rhythm: {
      score: number;
      beatAlignment: number;
      measureBoundaryScore: number;
      negativeBeatOffsetRatio: number;
      fragmentationRatio: number;
      onsetDeviationMean: number;
      onsetDeviationMedian: number;
    };
    pitch: {
      score: number;
      validPitchRatio: number;
      outlierRatio: number;
      excessiveLeapRatio: number;
      contourStability: number;
    };
  };
  diagnosis: {
    primaryIssues: string[];
    secondaryIssues: string[];
    riskLevel: string;
  };
  adjustments?: {
    recommendedActions: string[];
    priority?: string;
    nextStrategy?: string;
    parameterHints?: Record<string, unknown>;
  };
  comparison?: Record<string, unknown>;
};

export type AdjustmentPlan = {
  adjustmentPlanId: EntityId;
  schemaVersion?: string;
  taskId: EntityId;
  sourceVersionId: EntityId;
  targetVersionId: EntityId;
  priority?: string;
  actions: string[];
  parameterChanges?: Record<string, unknown>;
  expectedGoal?: string;
  triggerIssues?: string[];
};

export type IterationSnapshotStatus =
  | "created"
  | "analyzing"
  | "evaluating"
  | "completed"
  | "failed"
  | "discarded"
  | "selected_best";

export type IterationSnapshot = {
  snapshotId: EntityId;
  taskId: EntityId;
  versionId: EntityId;
  inputAssetId: EntityId;
  selectedStemId?: EntityId;
  timingGridId?: EntityId;
  phraseIds?: EntityId[];
  notationId?: EntityId;
  reportId?: EntityId;
  adjustmentPlanId?: EntityId | null;
  status: IterationSnapshotStatus;
};

export type AnalysisResult = {
  schemaVersion: string;
  taskId: EntityId;
  versionId: EntityId;
  inputAsset: InputAsset;
  stemCandidate: StemCandidate;
  timingGrid: TimingGrid;
  detailedNotes: DetailedNote[];
  notationCandidate: NotationCandidate;
  sourceName: string;
  durationSec: number;
  bpm: number;
  timeSignature: {
    numerator: number;
    denominator: number;
  };
  beats: number[];
  measures: Measure[];
  notes: DetailedNote[];
};

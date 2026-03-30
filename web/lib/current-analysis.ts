import rawAnalysis from "../../output/analysis/test1.analysis.json";
import type { AnalysisResult } from "../types/analysis";

export const currentAnalysis = rawAnalysis as unknown as AnalysisResult;

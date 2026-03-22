import { mockAnalysis } from "../lib/mock-analysis";

export default function HomePage() {
  return (
    <main style={{ fontFamily: "sans-serif", padding: 24, lineHeight: 1.5 }}>
      <h1>Guitar Transcription PoC</h1>
      <p>
        Day 1 scaffold for a semi-automatic guitar transcription workflow focused
        on rhythm-first draft generation.
      </p>

      <section>
        <h2>Current Mock Analysis</h2>
        <p>Source: {mockAnalysis.sourceName}</p>
        <p>Duration: {mockAnalysis.durationSec}s</p>
        <p>BPM: {mockAnalysis.bpm}</p>
        <p>
          Time Signature: {mockAnalysis.timeSignature.numerator}/
          {mockAnalysis.timeSignature.denominator}
        </p>
        <p>Measures: {mockAnalysis.measures.length}</p>
        <p>Notes: {mockAnalysis.notes.length}</p>
      </section>

      <section>
        <h2>Next Day 2 Goals</h2>
        <ul>
          <li>Load a real audio file in the Python analyzer</li>
          <li>Estimate BPM and beat positions</li>
          <li>Emit the first real analysis JSON result</li>
        </ul>
      </section>
    </main>
  );
}

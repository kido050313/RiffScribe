import Link from "next/link";

import { ScorePreview } from "../../components/score-preview";

export default function ScorePage() {
  return (
    <main
      style={{
        maxWidth: 1080,
        margin: "0 auto",
        padding: 24,
        lineHeight: 1.6,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ marginBottom: 8 }}>网页五线谱预览</h1>
          <p style={{ marginTop: 0, color: "#475569" }}>
            这个页面会直接读取当前样例的 MusicXML，并在浏览器里显示正式谱面。
          </p>
        </div>
        <Link
          href="/"
          style={{
            alignSelf: "center",
            color: "#0369a1",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          返回主工作台
        </Link>
      </div>

      <ScorePreview />
    </main>
  );
}

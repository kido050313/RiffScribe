"use client";

import { useEffect, useRef, useState } from "react";

type ScorePreviewProps = {
  src?: string;
};

export function ScorePreview({ src = "/api/score" }: ScorePreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let disposed = false;

    const renderScore = async () => {
      if (!containerRef.current) {
        return;
      }

      setStatus("loading");
      setErrorMessage(null);
      containerRef.current.innerHTML = "";

      try {
        const [{ OpenSheetMusicDisplay }, response] = await Promise.all([
          import("opensheetmusicdisplay"),
          fetch(src, { cache: "no-store" }),
        ]);

        if (!response.ok) {
          throw new Error("读取 MusicXML 失败。");
        }

        const xml = await response.text();
        if (disposed || !containerRef.current) {
          return;
        }

        const osmd = new OpenSheetMusicDisplay(containerRef.current, {
          autoResize: true,
          drawTitle: true,
          drawingParameters: "compacttight",
        });

        await osmd.load(xml);
        osmd.render();

        if (!disposed) {
          setStatus("ready");
        }
      } catch (error) {
        if (!disposed) {
          const message = error instanceof Error ? error.message : "谱面渲染失败。";
          setStatus("error");
          setErrorMessage(message);
        }
      }
    };

    void renderScore();

    return () => {
      disposed = true;
    };
  }, [src]);

  return (
    <section
      style={{
        marginTop: 20,
        border: "1px solid #dbe4f0",
        borderRadius: 18,
        background: "rgba(255, 255, 255, 0.92)",
        padding: 20,
        boxShadow: "0 18px 40px rgba(15, 23, 42, 0.06)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h2 style={{ margin: 0 }}>五线谱预览</h2>
          <p style={{ margin: "6px 0 0", color: "#475569" }}>
            当前直接读取导出的 MusicXML，在网页中显示只读谱面。
          </p>
        </div>
        <a
          href={src}
          target="_blank"
          rel="noreferrer"
          style={{
            alignSelf: "center",
            color: "#0369a1",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          打开原始 MusicXML
        </a>
      </div>

      {status === "loading" ? (
        <p style={statusStyle("#475569", "rgba(241, 245, 249, 0.95)", "#cbd5e1")}>正在加载谱面…</p>
      ) : null}

      {status === "error" ? (
        <p style={statusStyle("#b91c1c", "rgba(254, 226, 226, 0.95)", "rgba(248, 113, 113, 0.35)")}>
          {errorMessage ?? "谱面渲染失败。"}
        </p>
      ) : null}

      <div
        ref={containerRef}
        style={{
          marginTop: 18,
          minHeight: 180,
          overflowX: "auto",
        }}
      />
    </section>
  );
}

function statusStyle(color: string, background: string, borderColor: string) {
  return {
    marginTop: 16,
    color,
    background,
    border: `1px solid ${borderColor}`,
    borderRadius: 12,
    padding: "10px 12px",
  } as const;
}

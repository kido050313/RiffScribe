"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

import { currentAnalysis } from "../lib/current-analysis";
import type { AnalysisResult, NoteEvent } from "../types/analysis";

type DragState = {
  noteId: string;
  pointerStartX: number;
  noteStart: number;
  noteEnd: number;
};

type ExportFormat = "midi" | "musicxml";

type SavedProject = {
  version: 1;
  savedAt: string;
  analysis: AnalysisResult;
  loopEnabled: boolean;
  loopStart: number;
  loopEnd: number;
  selectedNoteId: string | null;
};

const PROJECT_STORAGE_KEY = "guitar-poc-project-v1";

type MetricCardProps = {
  label: string;
  value: string;
};

type LegendSwatchProps = {
  color: string;
  label: string;
};

type FieldEditorProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
};

type StatusMessageProps = {
  message: string;
  error?: boolean;
};

export default function HomePage() {
  const [notes, setNotes] = useState<NoteEvent[]>(currentAnalysis.notes);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(
    currentAnalysis.notes[0]?.id ?? null,
  );
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioError, setAudioError] = useState<string | null>(null);
  const [loopEnabled, setLoopEnabled] = useState(false);
  const [loopStart, setLoopStart] = useState(0);
  const [loopEnd, setLoopEnd] = useState(Math.min(currentAnalysis.durationSec || 1, 4));
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(null);
  const [exportMessage, setExportMessage] = useState<string | null>(null);
  const [projectMessage, setProjectMessage] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const timelineRef = useRef<HTMLDivElement | null>(null);
  const importInputRef = useRef<HTMLInputElement | null>(null);

  const duration = currentAnalysis.durationSec || 1;
  const previewNotes = notes.slice(0, 12);
  const beatBadges = useMemo(() => currentAnalysis.beats.slice(0, 24), []);
  const playheadLeft = `${Math.min((currentTime / duration) * 100, 100)}%`;
  const loopLeft = `${Math.min((loopStart / duration) * 100, 100)}%`;
  const loopWidth = `${Math.max(((loopEnd - loopStart) / duration) * 100, 0)}%`;

  const manuallySelectedNote = notes.find((note) => note.id === selectedNoteId) ?? notes[0];
  const activePlaybackNote =
    notes.find((note) => currentTime >= note.start && currentTime <= note.end + 0.03) ?? null;
  const selectedNote = activePlaybackNote ?? manuallySelectedNote;

  const analysisForExport: AnalysisResult = {
    ...currentAnalysis,
    notes,
  };

  const currentProject: SavedProject = {
    version: 1,
    savedAt: new Date().toISOString(),
    analysis: analysisForExport,
    loopEnabled,
    loopStart,
    loopEnd,
    selectedNoteId,
  };

  const updateNoteById = (noteId: string, updater: (note: NoteEvent) => NoteEvent) => {
    setNotes((currentNotes) =>
      currentNotes.map((note) => (note.id === noteId ? updater(note) : note)),
    );
  };

  const updateSelectedNote = (field: keyof NoteEvent, rawValue: string) => {
    const baseNote = manuallySelectedNote;
    if (!baseNote) {
      return;
    }
    const parsedValue = Number(rawValue);
    if (Number.isNaN(parsedValue)) {
      return;
    }

    updateNoteById(baseNote.id, (note) => {
      const nextNote = { ...note, [field]: parsedValue } as NoteEvent;
      if (field === "start" && nextNote.end < nextNote.start) {
        nextNote.end = nextNote.start;
      }
      if (field === "end" && nextNote.end < nextNote.start) {
        nextNote.start = nextNote.end;
      }
      return nextNote;
    });
  };

  const resetNotes = () => {
    setNotes(currentAnalysis.notes);
    setSelectedNoteId(currentAnalysis.notes[0]?.id ?? null);
    setLoopEnabled(false);
    setLoopStart(0);
    setLoopEnd(Math.min(currentAnalysis.durationSec || 1, 4));
    setExportMessage("已恢复为原始分析结果。");
    setProjectMessage(null);
  };

  const jumpToTime = (time: number) => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }
    audio.currentTime = Math.max(0, Math.min(time, duration));
    setCurrentTime(audio.currentTime);
  };

  const clampLoop = (start: number, end: number) => {
    const safeStart = Math.max(0, Math.min(start, duration));
    const safeEnd = Math.max(safeStart + 0.05, Math.min(end, duration));
    setLoopStart(Number(safeStart.toFixed(3)));
    setLoopEnd(Number(safeEnd.toFixed(3)));
  };

  const setLoopAroundSelectedNote = () => {
    if (!manuallySelectedNote) {
      return;
    }
    clampLoop(
      Math.max(0, manuallySelectedNote.start - 0.15),
      Math.min(duration, manuallySelectedNote.end + 0.15),
    );
    setLoopEnabled(true);
  };

  const setLoopToCurrentMeasure = () => {
    if (!selectedNote) {
      return;
    }
    const measure = currentAnalysis.measures[selectedNote.measureIndex];
    if (!measure) {
      return;
    }
    clampLoop(measure.start, Math.min(measure.end, duration));
    setLoopEnabled(true);
  };

  const handleTimelinePointer = (clientX: number) => {
    const timeline = timelineRef.current;
    if (!timeline) {
      return;
    }
    const rect = timeline.getBoundingClientRect();
    const ratio = (clientX - rect.left) / rect.width;
    jumpToTime(ratio * duration);
  };

  const togglePlayback = async () => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }
    if (audio.paused) {
      setAudioError(null);
      try {
        await audio.play();
      } catch (error) {
        const message = error instanceof Error ? error.message : "未知音频播放错误。";
        setAudioError(message);
      }
      return;
    }
    audio.pause();
  };

  const handleExport = async (format: ExportFormat) => {
    try {
      setExportingFormat(format);
      setExportMessage(null);
      const response = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ analysis: analysisForExport, format }),
      });
      if (!response.ok) {
        const payload = (await response.json().catch(() => null)) as { error?: string } | null;
        throw new Error(payload?.error ?? "导出失败。");
      }
      const blob = await response.blob();
      const extension = format === "midi" ? "mid" : "musicxml";
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `guitar-draft.${extension}`;
      anchor.click();
      URL.revokeObjectURL(url);
      setExportMessage(`已开始下载 ${format === "midi" ? "MIDI" : "MusicXML"} 文件。`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "导出失败。";
      setExportMessage(message);
    } finally {
      setExportingFormat(null);
    }
  };

  const applyProject = (project: SavedProject) => {
    setNotes(project.analysis.notes);
    setSelectedNoteId(project.selectedNoteId ?? project.analysis.notes[0]?.id ?? null);
    setLoopEnabled(project.loopEnabled);
    setLoopStart(project.loopStart);
    setLoopEnd(project.loopEnd);
  };

  const saveProjectToBrowser = () => {
    try {
      window.localStorage.setItem(PROJECT_STORAGE_KEY, JSON.stringify(currentProject));
      setProjectMessage("已保存到当前浏览器。");
    } catch (error) {
      const message = error instanceof Error ? error.message : "浏览器保存失败。";
      setProjectMessage(message);
    }
  };

  const restoreProjectFromBrowser = () => {
    try {
      const raw = window.localStorage.getItem(PROJECT_STORAGE_KEY);
      if (!raw) {
        setProjectMessage("当前浏览器里还没有已保存工程。");
        return;
      }
      applyProject(JSON.parse(raw) as SavedProject);
      setProjectMessage("已从浏览器恢复工程。");
    } catch (error) {
      const message = error instanceof Error ? error.message : "恢复浏览器工程失败。";
      setProjectMessage(message);
    }
  };

  const downloadProjectFile = () => {
    try {
      const blob = new Blob([JSON.stringify(currentProject, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "guitar-project.json";
      anchor.click();
      URL.revokeObjectURL(url);
      setProjectMessage("已导出工程文件。");
    } catch (error) {
      const message = error instanceof Error ? error.message : "导出工程文件失败。";
      setProjectMessage(message);
    }
  };

  const handleImportProject = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    try {
      applyProject(JSON.parse(await file.text()) as SavedProject);
      setProjectMessage("已导入工程文件。");
    } catch (error) {
      const message = error instanceof Error ? error.message : "导入工程文件失败。";
      setProjectMessage(message);
    } finally {
      event.target.value = "";
    }
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }
    const handleTimeUpdate = () => {
      if (loopEnabled && audio.currentTime >= loopEnd) {
        audio.currentTime = loopStart;
      }
      setCurrentTime(audio.currentTime);
    };
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => setIsPlaying(false);
    const handleError = () => {
      setAudioError("音频加载或播放失败，请检查 /api/audio 路由和音频源文件。");
      setIsPlaying(false);
    };

    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("play", handlePlay);
    audio.addEventListener("pause", handlePause);
    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("error", handleError);

    return () => {
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("play", handlePlay);
      audio.removeEventListener("pause", handlePause);
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("error", handleError);
    };
  }, [loopEnabled, loopEnd, loopStart]);

  useEffect(() => {
    if (!dragState) {
      return;
    }
    const handlePointerMove = (event: PointerEvent) => {
      const timeline = timelineRef.current;
      if (!timeline) {
        return;
      }
      const rect = timeline.getBoundingClientRect();
      const secondsPerPixel = duration / rect.width;
      const deltaSeconds = (event.clientX - dragState.pointerStartX) * secondsPerPixel;
      const noteLength = dragState.noteEnd - dragState.noteStart;
      const nextStart = Math.max(
        0,
        Math.min(dragState.noteStart + deltaSeconds, duration - noteLength),
      );
      const nextEnd = nextStart + noteLength;
      updateNoteById(dragState.noteId, (note) => ({
        ...note,
        start: Number(nextStart.toFixed(3)),
        end: Number(nextEnd.toFixed(3)),
      }));
    };
    const handlePointerUp = () => setDragState(null);
    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [dragState, duration]);

  return (
    <main
      style={{
        padding: 24,
        lineHeight: 1.5,
        maxWidth: 1100,
        margin: "0 auto",
      }}
    >
      <h1>电吉他转谱 PoC</h1>
      <div style={{ marginBottom: 12 }}>
        <Link
          href="/score"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 14px",
            borderRadius: 999,
            background: "rgba(2, 132, 199, 0.10)",
            border: "1px solid rgba(2, 132, 199, 0.24)",
            color: "#0369a1",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          打开五线谱预览
        </Link>
      </div>
      <p>
        当前页面展示的是基于真实 pipeline 输出的分析结果，已经接入测试视频生成的最新分析
        JSON，可以播放、循环、局部调整，并导出为 MIDI 或 MusicXML。
      </p>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: 12,
          marginTop: 24,
        }}
      >
        <MetricCard label="分析来源 Stem" value={currentAnalysis.sourceName} />
        <MetricCard label="时长" value={`${currentAnalysis.durationSec}s`} />
        <MetricCard label="BPM" value={`${currentAnalysis.bpm}`} />
        <MetricCard
          label="拍号"
          value={`${currentAnalysis.timeSignature.numerator}/${currentAnalysis.timeSignature.denominator}`}
        />
        <MetricCard label="小节数" value={`${currentAnalysis.measures.length}`} />
        <MetricCard label="拍点数" value={`${currentAnalysis.beats.length}`} />
        <MetricCard label="音符数" value={`${notes.length}`} />
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>导出与音频控制</h2>
        <p>
          当前这份初稿来自分离后的 <code>other.wav</code>，这是我们在 4-stem Demucs
          分离后默认优先使用的电吉他候选轨道。
        </p>

        <div
          style={{
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
            alignItems: "center",
            marginTop: 16,
          }}
        >
          <button
            type="button"
            onClick={() => void togglePlayback()}
            style={primaryButtonStyle(isPlaying)}
          >
            {isPlaying ? "暂停音频" : "播放音频"}
          </button>
          <button
            type="button"
            onClick={() => void handleExport("midi")}
            style={secondaryButtonStyle(exportingFormat !== null)}
            disabled={exportingFormat !== null}
          >
            {exportingFormat === "midi" ? "正在导出 MIDI..." : "导出 MIDI"}
          </button>
          <button
            type="button"
            onClick={() => void handleExport("musicxml")}
            style={secondaryButtonStyle(exportingFormat !== null)}
            disabled={exportingFormat !== null}
          >
            {exportingFormat === "musicxml" ? "正在导出 MusicXML..." : "导出 MusicXML"}
          </button>
          <span style={{ color: "#475569", fontSize: 14 }}>
            当前播放位置：{currentTime.toFixed(2)}s / {duration.toFixed(2)}s
          </span>
        </div>

        {exportMessage ? (
          <StatusMessage message={exportMessage} error={exportMessage.includes("失败")} />
        ) : null}

        <div
          style={{
            display: "flex",
            gap: 10,
            flexWrap: "wrap",
            alignItems: "center",
            marginTop: 12,
          }}
        >
          <button
            type="button"
            onClick={() => setLoopEnabled((value) => !value)}
            style={secondaryButtonStyle(false)}
          >
            {loopEnabled ? "关闭循环" : "开启循环"}
          </button>
          <button type="button" onClick={setLoopAroundSelectedNote} style={secondaryButtonStyle(false)}>
            以当前音符设循环
          </button>
          <button type="button" onClick={setLoopToCurrentMeasure} style={secondaryButtonStyle(false)}>
            以当前小节设循环
          </button>
          <button
            type="button"
            onClick={() => clampLoop(Math.max(currentTime - 1, 0), Math.min(currentTime + 1.5, duration))}
            style={secondaryButtonStyle(false)}
          >
            以当前播放点设循环
          </button>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 12,
            marginTop: 14,
          }}
        >
          <FieldEditor
            label="循环开始"
            value={String(loopStart)}
            onChange={(value) => clampLoop(Number(value || 0), loopEnd)}
          />
          <FieldEditor
            label="循环结束"
            value={String(loopEnd)}
            onChange={(value) => clampLoop(loopStart, Number(value || loopStart + 0.05))}
          />
        </div>

        <p style={{ color: "#475569", marginTop: 10 }}>
          当前循环区间：{loopStart.toFixed(2)}s - {loopEnd.toFixed(2)}s
          {loopEnabled ? "（已启用）" : "（未启用）"}
        </p>

        <audio ref={audioRef} preload="metadata" src="/api/audio" />

        {audioError ? <StatusMessage message={audioError} error /> : null}
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>工程保存与恢复</h2>
        <p>
          这一步先支持浏览器本地保存和工程文件导入导出，避免你们调整过的节奏与循环设置只停留在当前页面会话里。
        </p>

        <div
          style={{
            display: "flex",
            gap: 10,
            flexWrap: "wrap",
            alignItems: "center",
            marginTop: 16,
          }}
        >
          <button type="button" onClick={saveProjectToBrowser} style={secondaryButtonStyle(false)}>
            保存到浏览器
          </button>
          <button
            type="button"
            onClick={restoreProjectFromBrowser}
            style={secondaryButtonStyle(false)}
          >
            从浏览器恢复
          </button>
          <button type="button" onClick={downloadProjectFile} style={secondaryButtonStyle(false)}>
            导出工程文件
          </button>
          <button
            type="button"
            onClick={() => importInputRef.current?.click()}
            style={secondaryButtonStyle(false)}
          >
            导入工程文件
          </button>
          <input
            ref={importInputRef}
            type="file"
            accept="application/json,.json"
            onChange={(event) => void handleImportProject(event)}
            hidden
          />
        </div>

        {projectMessage ? (
          <StatusMessage message={projectMessage} error={projectMessage.includes("失败")} />
        ) : null}
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>拍点预览</h2>
        <p style={{ color: "#475569", marginTop: 0 }}>
          这里展示前 {beatBadges.length} 个检测到的拍点。如果节奏网格比较准确，这些拍点在听感上应该会比较均匀。
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {beatBadges.map((beat, index) => (
            <span key={`${beat}-${index}`} style={beatBadgeStyle}>
              第 {index + 1} 拍：{beat.toFixed(3)}s
            </span>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>节奏时间轴</h2>
        <p>
          这个视图会把小节、拍点和检测到的音符事件放到同一条时间轴上，帮助我们更快判断节奏是否对齐。
        </p>
        <p style={{ color: "#475569", marginTop: 0 }}>
          点击音符可以跳转播放位置，也可以左右拖动音符块调整它的时间位置。播放时，当前命中的音符会自动高亮。
        </p>

        <div
          ref={timelineRef}
          onClick={(event) => handleTimelinePointer(event.clientX)}
          style={{
            position: "relative",
            height: 240,
            border: "1px solid #cbd5e1",
            borderRadius: 16,
            background: "linear-gradient(180deg, #ffffff 0%, #f8fafc 55%, #eef2ff 100%)",
            overflow: "hidden",
            marginTop: 16,
            cursor: "pointer",
          }}
        >
          {loopEnabled ? (
            <div
              style={{
                position: "absolute",
                left: loopLeft,
                top: 0,
                bottom: 0,
                width: loopWidth,
                background: "rgba(34, 197, 94, 0.10)",
                borderLeft: "2px solid rgba(34, 197, 94, 0.65)",
                borderRight: "2px solid rgba(34, 197, 94, 0.65)",
                zIndex: 0,
              }}
            />
          ) : null}

          <div
            style={{
              position: "absolute",
              left: playheadLeft,
              top: 0,
              bottom: 0,
              width: 2,
              background: "#e11d48",
              opacity: 0.9,
              zIndex: 4,
              boxShadow: "0 0 0 3px rgba(225, 29, 72, 0.12)",
            }}
          />

          {currentAnalysis.measures.map((measure) => {
            const left = `${(measure.start / duration) * 100}%`;
            return (
              <div
                key={`measure-${measure.index}`}
                style={{
                  position: "absolute",
                  left,
                  top: 0,
                  bottom: 0,
                  width: 1,
                  background: "#0f172a",
                  opacity: 0.35,
                  zIndex: 1,
                }}
                title={`第 ${measure.index + 1} 小节`}
              />
            );
          })}

          {currentAnalysis.beats.map((beat, index) => {
            const left = `${(beat / duration) * 100}%`;
            const isMeasureStart = index % currentAnalysis.timeSignature.numerator === 0;
            return (
              <div
                key={`beat-line-${index}`}
                style={{
                  position: "absolute",
                  left,
                  top: 28,
                  bottom: 0,
                  width: 1,
                  background: isMeasureStart ? "#334155" : "#94a3b8",
                  opacity: isMeasureStart ? 0.5 : 0.35,
                  zIndex: 1,
                }}
                title={`第 ${index + 1} 拍`}
              />
            );
          })}

          {currentAnalysis.measures.map((measure) => {
            const left = `${(measure.start / duration) * 100}%`;
            return (
              <div
                key={`measure-label-${measure.index}`}
                style={{
                  position: "absolute",
                  left,
                  top: 8,
                  transform: "translateX(6px)",
                  fontSize: 12,
                  color: "#1e293b",
                  fontWeight: 600,
                  zIndex: 3,
                }}
              >
                第 {measure.index + 1} 小节
              </div>
            );
          })}

          {notes.map((note, index) => {
            const left = (note.start / duration) * 100;
            const width = Math.max(((note.end - note.start) / duration) * 100, 0.8);
            const row = index % 6;
            const top = 48 + row * 24;
            const hue = 205 + (note.measureIndex % 3) * 18;
            const isSelected = note.id === selectedNote?.id;
            const isActivePlayback = note.id === activePlaybackNote?.id;

            return (
              <button
                key={note.id}
                type="button"
                onClick={(event) => {
                  event.stopPropagation();
                  setSelectedNoteId(note.id);
                  jumpToTime(note.start);
                }}
                onPointerDown={(event) => {
                  event.stopPropagation();
                  setSelectedNoteId(note.id);
                  setDragState({
                    noteId: note.id,
                    pointerStartX: event.clientX,
                    noteStart: note.start,
                    noteEnd: note.end,
                  });
                }}
                style={{
                  position: "absolute",
                  left: `${left}%`,
                  top,
                  width: `${width}%`,
                  minWidth: 6,
                  height: 16,
                  borderRadius: 999,
                  background: isActivePlayback
                    ? "linear-gradient(90deg, #f97316 0%, #fb7185 100%)"
                    : `hsla(${hue}, 85%, 52%, 0.75)`,
                  border: isSelected
                    ? "2px solid rgba(15, 23, 42, 0.78)"
                    : "1px solid rgba(15, 23, 42, 0.18)",
                  boxShadow: isActivePlayback
                    ? "0 0 0 4px rgba(251, 113, 133, 0.25)"
                    : isSelected
                      ? "0 0 0 3px rgba(56, 189, 248, 0.28)"
                      : "0 1px 2px rgba(15, 23, 42, 0.12)",
                  cursor: dragState?.noteId === note.id ? "grabbing" : "grab",
                  zIndex: 2,
                }}
                title={`${note.id} | ${note.start.toFixed(3)}s - ${note.end.toFixed(3)}s | MIDI ${note.midiPitch}`}
              />
            );
          })}
        </div>

        <div
          style={{
            display: "flex",
            gap: 16,
            flexWrap: "wrap",
            marginTop: 12,
            fontSize: 13,
            color: "#475569",
          }}
        >
          <LegendSwatch color="#0f172a" label="小节起点" />
          <LegendSwatch color="#94a3b8" label="拍点线" />
          <LegendSwatch color="hsla(205, 85%, 52%, 0.75)" label="检测到的音符事件" />
          <LegendSwatch color="#e11d48" label="当前播放位置" />
          <LegendSwatch
            color="linear-gradient(90deg, #f97316 0%, #fb7185 100%)"
            label="当前播放命中的音符"
          />
          <LegendSwatch color="rgba(34, 197, 94, 0.55)" label="循环区间" />
        </div>
      </section>

      {selectedNote ? (
        <section style={{ marginTop: 32 }}>
          <div
            style={{
              padding: 16,
              borderRadius: 14,
              background: "rgba(255, 255, 255, 0.78)",
              border: "1px solid rgba(148, 163, 184, 0.28)",
              backdropFilter: "blur(8px)",
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: 10 }}>当前音符详情</h3>
            {activePlaybackNote ? (
              <p style={{ marginTop: 0, color: "#c2410c", fontWeight: 600 }}>
                当前播放位置正在经过音符 {activePlaybackNote.id}。
              </p>
            ) : (
              <p style={{ marginTop: 0, color: "#475569" }}>
                当前播放位置位于两个检测音符之间。
              </p>
            )}

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                gap: 12,
              }}
            >
              <MetricCard label="音符 ID" value={selectedNote.id} />
              <MetricCard label="开始时间" value={`${selectedNote.start.toFixed(3)}s`} />
              <MetricCard label="结束时间" value={`${selectedNote.end.toFixed(3)}s`} />
              <MetricCard label="MIDI" value={`${selectedNote.midiPitch}`} />
              <MetricCard label="所在小节" value={`${selectedNote.measureIndex + 1}`} />
              <MetricCard label="拍内偏移" value={`${selectedNote.beatOffset}`} />
            </div>

            <div style={{ marginTop: 20 }}>
              <h4 style={{ marginBottom: 10 }}>本地编辑</h4>
              <p style={{ color: "#475569", marginTop: 0 }}>
                这里的修改会立即反映到时间轴和表格。当前已经支持拖动时间轴中的音符块整体移动位置。
              </p>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: 12,
                }}
              >
                <FieldEditor
                  label="开始时间"
                  value={String(manuallySelectedNote?.start ?? "")}
                  onChange={(value) => updateSelectedNote("start", value)}
                />
                <FieldEditor
                  label="结束时间"
                  value={String(manuallySelectedNote?.end ?? "")}
                  onChange={(value) => updateSelectedNote("end", value)}
                />
                <FieldEditor
                  label="MIDI"
                  value={String(manuallySelectedNote?.midiPitch ?? "")}
                  onChange={(value) => updateSelectedNote("midiPitch", value)}
                />
                <FieldEditor
                  label="拍内偏移"
                  value={String(manuallySelectedNote?.beatOffset ?? "")}
                  onChange={(value) => updateSelectedNote("beatOffset", value)}
                />
              </div>
              <div style={{ marginTop: 14 }}>
                <button type="button" onClick={resetNotes} style={secondaryButtonStyle(false)}>
                  恢复原始分析结果
                </button>
              </div>
            </div>
          </div>
        </section>
      ) : null}

      <section style={{ marginTop: 32 }}>
        <h2>音符预览</h2>
        <div style={{ overflowX: "auto" }}>
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: 14,
            }}
          >
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "1px solid #cbd5e1" }}>
                <th style={{ padding: "8px 10px" }}>ID</th>
                <th style={{ padding: "8px 10px" }}>开始时间</th>
                <th style={{ padding: "8px 10px" }}>结束时间</th>
                <th style={{ padding: "8px 10px" }}>MIDI</th>
                <th style={{ padding: "8px 10px" }}>时值拍数</th>
                <th style={{ padding: "8px 10px" }}>小节</th>
                <th style={{ padding: "8px 10px" }}>拍内偏移</th>
              </tr>
            </thead>
            <tbody>
              {previewNotes.map((note) => (
                <tr key={note.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                  <td style={{ padding: "8px 10px" }}>{note.id}</td>
                  <td style={{ padding: "8px 10px" }}>{note.start.toFixed(3)}</td>
                  <td style={{ padding: "8px 10px" }}>{note.end.toFixed(3)}</td>
                  <td style={{ padding: "8px 10px" }}>{note.midiPitch}</td>
                  <td style={{ padding: "8px 10px" }}>{note.durationBeats}</td>
                  <td style={{ padding: "8px 10px" }}>{note.measureIndex + 1}</td>
                  <td style={{ padding: "8px 10px" }}>{note.beatOffset}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>下一步 UI 方向</h2>
        <p>
          现在已经有了播放、循环、导出和工程保存闭环。下一步最有价值的升级，是继续支持在时间轴上直接调整音符长度，或加入多
          stem 切换对比。
        </p>
      </section>
    </main>
  );
}

function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div
      style={{
        padding: 16,
        borderRadius: 12,
        background: "#f8fafc",
        border: "1px solid #e2e8f0",
      }}
    >
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function LegendSwatch({ color, label }: LegendSwatchProps) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span
        style={{
          width: 18,
          height: 10,
          borderRadius: 999,
          background: color,
          display: "inline-block",
        }}
      />
      <span>{label}</span>
    </div>
  );
}

function FieldEditor({ label, value, onChange }: FieldEditorProps) {
  return (
    <label style={{ display: "grid", gap: 6 }}>
      <span style={{ fontSize: 13, color: "#475569", fontWeight: 600 }}>{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        style={{
          border: "1px solid #cbd5e1",
          borderRadius: 10,
          padding: "10px 12px",
          fontSize: 14,
          background: "#fff",
          color: "#0f172a",
        }}
      />
    </label>
  );
}

function StatusMessage({ message, error = false }: StatusMessageProps) {
  return (
    <p
      style={{
        marginTop: 12,
        color: error ? "#b91c1c" : "#166534",
        background: error ? "rgba(254, 226, 226, 0.9)" : "rgba(220, 252, 231, 0.85)",
        border: error
          ? "1px solid rgba(248, 113, 113, 0.4)"
          : "1px solid rgba(74, 222, 128, 0.35)",
        borderRadius: 10,
        padding: "10px 12px",
      }}
    >
      {message}
    </p>
  );
}

function primaryButtonStyle(isPlaying: boolean) {
  return {
    border: 0,
    borderRadius: 999,
    background: isPlaying ? "#0f172a" : "#0284c7",
    color: "#fff",
    padding: "12px 18px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    boxShadow: "0 8px 18px rgba(2, 132, 199, 0.18)",
  } as const;
}

function secondaryButtonStyle(disabled: boolean) {
  return {
    border: "1px solid #cbd5e1",
    borderRadius: 999,
    background: "#fff",
    color: disabled ? "#94a3b8" : "#0f172a",
    padding: "10px 14px",
    fontSize: 13,
    fontWeight: 600,
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.72 : 1,
  } as const;
}

const beatBadgeStyle = {
  padding: "6px 10px",
  borderRadius: 999,
  background: "#f1f5f9",
  border: "1px solid #cbd5e1",
  fontSize: 13,
} as const;

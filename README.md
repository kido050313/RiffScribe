# Guitar Transcription PoC

[English](./README.md) | [中文](./README.zh-CN.md)

This is an early prototype for a rhythm-first electric guitar transcription tool.

## What this project is

The goal is to help guitar players turn a short performance clip into an editable draft faster than manual transcription.

Current workflow:
1. Input a local video or mixed audio clip
2. Extract audio
3. Run 4-stem separation
4. Prefer `other.wav` as the guitar candidate stem
5. Analyze BPM, beats, measures, and note events
6. Review the result in a web timeline UI

## Current status

What already works:
- local video to wav extraction
- Demucs-based 4-stem separation
- rhythm and note-event analysis to JSON
- export to MIDI
- export to MusicXML
- a web page that can:
  - play the separated audio
  - show beats, measures, and note events
  - highlight the current playback note
  - loop a selected time range
  - edit note values locally
  - drag note blocks horizontally on the timeline

What is still prototype-level:
- note accuracy is still rough
- no final score export yet
- no persistent save yet
- no production-grade note editing yet

## Repository structure

- `analyzer/`: Python scripts for extraction, separation, and analysis
- `web/`: Next.js frontend prototype
- `samples/`: local sample guidance
- `samples/raw/`: original local video or mixed audio input
- `output/`: extracted audio, separated stems, and analysis JSON
- `docs/`: planning notes and implementation documents

## Quick start

### 1. Python environment

Create a project virtual environment:

```powershell
python -m venv .venv
```

Install Python dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt
```

### 2. Run the analysis pipeline

Put a local clip into `samples/raw/`, for example `samples/raw/test1.mp4`.

Run:

```powershell
.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/test1.mp4 --fallback-to-extracted
```

This produces:
- extracted wav in `output/extracted/`
- separated stems in `output/separated/`
- analysis JSON in `output/analysis/`

### 2.5 Export MIDI and MusicXML

Run:

```powershell
.\.venv\Scripts\python.exe analyzer/export.py --input output/analysis/test1.analysis.json
```

This produces:
- `output/exports/test1.mid`
- `output/exports/test1.musicxml`

### 3. Run the web UI

Go to the frontend directory:

```powershell
cd web
```

Install frontend dependencies:

```powershell
pnpm install
```

Start the dev server:

```powershell
pnpm dev
```

Then open the local URL shown in the terminal.

## Verified example

The repository has already been tested with:
- input: `samples/raw/test1.mp4`
- extracted audio: `output/extracted/test1.wav`
- preferred stem: `output/separated/htdemucs/test1/other.wav`
- analysis result: `output/analysis/test1.analysis.json`
- MIDI export: `output/exports/test1.mid`
- MusicXML export: `output/exports/test1.musicxml`

## Recommended usage right now

This project is best used as:
- a rhythm inspection tool
- a fast draft generator
- a practice helper for short guitar phrases

It is not yet a final notation product.

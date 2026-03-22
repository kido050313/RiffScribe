# Analyzer

[English](./README.md) | [中文](./README.zh-CN.md)

This folder contains the Python-side audio pipeline.

## Responsibilities

- extract wav audio from local video or mixed input
- run Demucs separation
- analyze audio into BPM, beats, measures, and note events
- write normalized JSON into `output/analysis/`

## Main scripts

- `extract.py`: convert local media into analysis-ready wav
- `separate.py`: run Demucs through the Python API and save stems with `soundfile`
- `main.py`: analyze an audio file into JSON note events
- `pipeline.py`: run extraction, separation, and analysis in one command
- `export.py`: export analysis JSON to MIDI and MusicXML

## Recommended workflow

Create and use the project virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt
```

Run the full pipeline:

```powershell
.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/test1.mp4 --fallback-to-extracted
```

Export MIDI and MusicXML:

```powershell
.\.venv\Scripts\python.exe analyzer/export.py --input output/analysis/test1.analysis.json
```

## Important project choices

- default separation is full 4-stem, not `--two-stems vocals`
- `other.wav` is treated as the first guitar candidate stem
- if separation is unusable, the pipeline can fall back to the extracted mixed audio

## Output expectations

After running the pipeline you should see:
- extracted wav in `output/extracted/`
- stems in `output/separated/`
- analysis JSON in `output/analysis/`
- exported MIDI and MusicXML in `output/exports/`

## Verified example

- input: `samples/raw/test1.mp4`
- extracted audio: `output/extracted/test1.wav`
- preferred stem: `output/separated/htdemucs/test1/other.wav`
- analysis output: `output/analysis/test1.analysis.json`
- MIDI export: `output/exports/test1.mid`
- MusicXML export: `output/exports/test1.musicxml`

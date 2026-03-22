# Output

[English](./README.md) | [中文](./README.zh-CN.md)

This folder stores generated artifacts from the pipeline.

## Current subfolders

- `extracted/`: wav files extracted from local media
- `separated/`: Demucs stem outputs
- `analysis/`: JSON analysis results

## Current verified files

- `output/extracted/test1.wav`
- `output/separated/htdemucs/test1/other.wav`
- `output/analysis/test1.analysis.json`

## What these files mean

- extracted wav: cleaned intermediate audio for analysis
- separated stems: stem candidates such as `drums.wav`, `bass.wav`, `other.wav`, `vocals.wav`
- analysis JSON: BPM, beats, measures, and note events used by the web UI

## Future output

Later versions may also write:
- `*.musicxml`
- `*.mid`

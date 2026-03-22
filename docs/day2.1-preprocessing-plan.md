# Day 2.1 Preprocessing Plan

[English](./day2.1-preprocessing-plan.md) | [中文](./day2.1-preprocessing-plan.zh-CN.md)

Goal:
- accept a local video or mixed audio input
- extract an analysis-ready audio file
- attempt source separation before rhythm and pitch analysis

Updated pipeline:
1. input video or mixed audio
2. extract audio
3. normalize audio format
4. run source separation
5. choose the best stem for guitar-focused analysis
6. pass the selected stem into rhythm and pitch analysis

Day 2.1 deliverables:
- a preprocessing pipeline definition
- clear input and output contracts
- a folder layout for extracted and separated media
- a recommended toolchain for media extraction and separation
- fallback behavior when separation quality is poor

Scope:
- support local `mp4`, `mov`, `wav`, `mp3`, `m4a`
- convert media into mono or stereo `wav` for analysis
- save extracted audio files
- save separated stems
- allow analysis on either the original extracted track or a separated stem

Out of scope:
- direct Bilibili URL ingestion
- cloud processing
- real-time separation
- guaranteed clean guitar isolation for all mixes

Recommended tools:
- `ffmpeg` for video-to-audio extraction and format normalization
- `demucs` as the first source separation baseline
- existing `analyzer/main.py` as the rhythm and note analysis stage

Proposed folder layout:
- `samples/raw/`: original local video and mixed audio files
- `output/extracted/`: audio extracted from video
- `output/separated/`: source-separated stems
- `output/analysis/`: JSON analysis outputs

Implementation order:
1. add a media extraction script
2. add a source separation script
3. add a pipeline runner that connects extraction, separation, and analysis
4. compare analysis quality between original extracted audio and separated stems

Success criteria:
- one local video can be converted into a wav file
- one mixed audio clip can produce separated stems
- at least one stem can be analyzed with the existing Day 2 analyzer
- the team can compare which input produces a better rhythm draft

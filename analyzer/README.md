# Analyzer

[English](./README.md) | [中文](./README.zh-CN.md)

This folder contains the Python-based audio analysis prototype.

Planned responsibilities:
- load audio clips from `samples/` or preprocessing outputs
- extract analysis-ready audio from local video inputs
- run source separation for guitar-focused analysis
- estimate duration, BPM, beat positions, and measures
- detect basic pitch events
- write a normalized analysis JSON file into `output/`

Day 1 status:
- `main.py` writes a placeholder `analysis-result.json`
- real audio processing starts on Day 2

Day 2 usage:
- create a project environment with `python -m venv .venv`
- use `.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt`
- place an audio clip in `samples/`, or pass a path with `--input`
- run `.\.venv\Scripts\python.exe analyzer/main.py`
- optional: run `.\.venv\Scripts\python.exe analyzer/main.py --input samples/your-clip.wav --output output/your-analysis.json`

Day 2.1 target:
- add preprocessing support for local video files
- extract wav audio before analysis
- compare analysis quality between original mixed audio and separated stems

Day 2.1 commands:
- run `.\.venv\Scripts\python.exe analyzer/extract.py` to extract wav audio from `samples/raw/`
- optional: run `.\.venv\Scripts\python.exe analyzer/extract.py --input samples/raw/your-video.mp4`
- install separation tools with `.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt`
- run `.\.venv\Scripts\python.exe analyzer/separate.py` to create stems from `output/extracted/`
- run `.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/your-video.mp4 --fallback-to-extracted` to execute extraction, separation, and analysis in one command

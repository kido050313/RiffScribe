# Guitar Transcription PoC

[English](./README.md) | [中文](./README.zh-CN.md)

This repository contains an early-stage scaffold for a semi-automatic electric guitar transcription product.

Current goal:
- Accept a 30-60 second local video or mixed audio clip
- Extract and separate guitar-focused audio before analysis
- Analyze rhythm and basic pitch candidates
- Produce an editable TAB + staff draft

Project structure:
- `web/`: frontend prototype files and shared TypeScript types
- `analyzer/`: Python analysis entrypoint and dependencies
- `samples/`: local audio samples for testing
- `output/`: generated JSON and export artifacts
- `docs/`: product and technical notes

Current implemented scope:
- Create project folders
- Define the shared `AnalysisResult` schema
- Add mock analysis data for frontend development
- Prepare the Python analyzer entrypoint
- Add a Day 2 audio analysis script for BPM, beats, and note candidates

Current next step:
- add Day 2.1 preprocessing for video extraction and source separation
- route extracted or separated audio into `analyzer/main.py`

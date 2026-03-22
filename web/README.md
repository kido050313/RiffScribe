# Web

[English](./README.md) | [中文](./README.zh-CN.md)

This folder contains the Next.js frontend prototype.

## What the page currently does

- reads the latest analysis JSON
- plays the separated guitar-candidate audio
- shows measures, beats, note events, and a playback cursor
- highlights the currently active note during playback
- supports loop playback
- supports local note editing
- supports dragging note blocks horizontally on the timeline

## How to run

Install dependencies:

```powershell
pnpm install
```

Start development:

```powershell
pnpm dev
```

Type check:

```powershell
pnpm typecheck
```

## Current data source

The current page reads:
- analysis JSON from `../output/analysis/test1.analysis.json`
- audio from `/api/audio`
- `/api/audio` serves `../output/separated/htdemucs/test1/other.wav`

## Notes

- only run one `pnpm dev` instance at a time
- if `.next/trace` gets locked on Windows, stop old Node processes and restart the dev server

## Current product role

Right now this page is a prototype correction workspace, not a polished final UI.

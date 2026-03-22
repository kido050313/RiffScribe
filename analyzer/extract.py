from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SUPPORTED_INPUT_SUFFIXES = {".mp4", ".mov", ".mkv", ".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def find_default_input(raw_dir: Path) -> Path | None:
    for path in sorted(raw_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_INPUT_SUFFIXES:
            return path
    return None


def build_output_path(input_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{input_path.stem}.wav"


def extract_audio(input_path: Path, output_path: Path, sample_rate: int = 22050, channels: int = 1) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        str(sample_rate),
        "-ac",
        str(channels),
        str(output_path),
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract analysis-ready wav audio from local media.")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a local media file. If omitted, uses the first supported file in samples/raw/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to the output wav file. Defaults to output/extracted/<input-name>.wav.",
    )
    parser.add_argument("--sample-rate", type=int, default=22050, help="Target sample rate for analysis.")
    parser.add_argument("--channels", type=int, default=1, help="Target channel count for analysis.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    raw_dir = repo_root / "samples" / "raw"
    extracted_dir = repo_root / "output" / "extracted"
    raw_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir.mkdir(parents=True, exist_ok=True)

    input_path = args.input or find_default_input(raw_dir)
    if input_path is None:
        raise SystemExit("No input media found. Add a file to samples/raw/ or pass --input <path>.")

    if not input_path.exists():
        raise SystemExit(f"Input media not found: {input_path}")

    output_path = args.output or build_output_path(input_path, extracted_dir)
    extract_audio(input_path, output_path, sample_rate=args.sample_rate, channels=args.channels)

    print(f"Extracted audio from: {input_path.name}")
    print(f"Wrote wav file to: {output_path}")


if __name__ == "__main__":
    main()

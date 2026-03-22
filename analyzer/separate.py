from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def find_default_audio(extracted_dir: Path) -> Path | None:
    if not extracted_dir.exists():
        return None
    for path in sorted(extracted_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_SUFFIXES:
            return path
    return None


def run_demucs(input_path: Path, output_dir: Path, two_stems: str | None = None) -> None:
    command = [sys.executable, "-m", "demucs", "-o", str(output_dir)]
    if two_stems:
        command.extend(["--two-stems", two_stems])
    command.append(str(input_path))

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Python was not found while trying to run Demucs."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "Demucs separation failed. Install it with `python -m pip install demucs` or "
            "`python -m pip install -r analyzer/requirements.txt`, then retry."
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run source separation on extracted audio.")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a local audio file. If omitted, uses the first supported file in output/extracted/.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for separated stems. Defaults to output/separated/.",
    )
    parser.add_argument(
        "--two-stems",
        default="vocals",
        help="Optional Demucs two-stem mode, for example 'vocals'. Defaults to vocals.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    extracted_dir = repo_root / "output" / "extracted"
    separated_dir = args.output_dir or (repo_root / "output" / "separated")
    separated_dir.mkdir(parents=True, exist_ok=True)

    input_path = args.input or find_default_audio(extracted_dir)
    if input_path is None:
        raise SystemExit(
            "No extracted audio found. Run analyzer/extract.py first or pass --input <path>."
        )

    if not input_path.exists():
        raise SystemExit(f"Input audio not found: {input_path}")

    run_demucs(input_path, separated_dir, two_stems=args.two_stems)
    print(f"Separated stems for: {input_path.name}")
    print(f"Stems written under: {separated_dir}")


if __name__ == "__main__":
    main()

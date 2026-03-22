from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], step_name: str) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"{step_name} failed with exit code {exc.returncode}.") from exc


def run_extract(script_path: Path, input_path: Path, output_path: Path, sample_rate: int, channels: int) -> Path:
    command = [
        sys.executable,
        str(script_path),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--sample-rate",
        str(sample_rate),
        "--channels",
        str(channels),
    ]
    run_command(command, "Audio extraction")
    return output_path


def run_separation(
    script_path: Path,
    input_path: Path,
    output_dir: Path,
    two_stems: str | None,
) -> Path:
    command = [
        sys.executable,
        str(script_path),
        "--input",
        str(input_path),
        "--output-dir",
        str(output_dir),
    ]
    if two_stems:
        command.extend(["--two-stems", two_stems])

    run_command(command, "Source separation")
    return output_dir


def run_analysis(script_path: Path, input_path: Path, output_path: Path) -> Path:
    command = [
        sys.executable,
        str(script_path),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ]
    run_command(command, "Audio analysis")
    return output_path


def find_preferred_stem(separated_dir: Path, source_stem: str) -> Path | None:
    if not separated_dir.exists():
        return None

    preferred_names = [
        "other.wav",
        "no_vocals.wav",
        f"{source_stem}.wav",
    ]

    for candidate_name in preferred_names:
        matches = sorted(separated_dir.rglob(candidate_name))
        if matches:
            return matches[0]

    all_wavs = sorted(separated_dir.rglob("*.wav"))
    if all_wavs:
        return all_wavs[0]
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run extraction, optional separation, and analysis in one command."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a local video or audio file.",
    )
    parser.add_argument(
        "--analysis-source",
        choices=["separated", "extracted"],
        default="separated",
        help="Choose whether analysis should prefer the separated stem or the extracted audio.",
    )
    parser.add_argument(
        "--skip-separation",
        action="store_true",
        help="Skip the separation step and analyze the extracted wav directly.",
    )
    parser.add_argument(
        "--fallback-to-extracted",
        action="store_true",
        help="If separation fails or no suitable stem is found, analyze the extracted wav instead.",
    )
    parser.add_argument(
        "--two-stems",
        default=None,
        help="Optional Demucs two-stem mode. Defaults to full 4-stem separation.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=22050,
        help="Sample rate for extracted wav audio.",
    )
    parser.add_argument(
        "--channels",
        type=int,
        default=1,
        help="Channel count for extracted wav audio.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Input media not found: {args.input}")

    repo_root = Path(__file__).resolve().parent.parent
    analyzer_dir = Path(__file__).resolve().parent
    extracted_dir = repo_root / "output" / "extracted"
    separated_dir = repo_root / "output" / "separated"
    analysis_dir = repo_root / "output" / "analysis"

    extracted_dir.mkdir(parents=True, exist_ok=True)
    separated_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    extracted_audio_path = extracted_dir / f"{args.input.stem}.wav"
    analysis_output_path = analysis_dir / f"{args.input.stem}.analysis.json"

    print("Step 1/3: extracting analysis-ready audio...")
    run_extract(
        script_path=analyzer_dir / "extract.py",
        input_path=args.input,
        output_path=extracted_audio_path,
        sample_rate=args.sample_rate,
        channels=args.channels,
    )

    analysis_input_path = extracted_audio_path
    used_separation = False

    if not args.skip_separation:
        print("Step 2/3: running source separation...")
        try:
            run_separation(
                script_path=analyzer_dir / "separate.py",
                input_path=extracted_audio_path,
                output_dir=separated_dir,
                two_stems=args.two_stems,
            )
            preferred_stem = find_preferred_stem(separated_dir, args.input.stem)
            if preferred_stem is not None and args.analysis_source == "separated":
                analysis_input_path = preferred_stem
                used_separation = True
            elif preferred_stem is None and not args.fallback_to_extracted:
                raise SystemExit(
                    "Source separation completed but no suitable stem was found. "
                    "Retry with --fallback-to-extracted to analyze the extracted wav."
                )
        except SystemExit:
            if not args.fallback_to_extracted:
                raise
            print("Separation step failed or returned no usable stem, falling back to extracted audio.")

    print("Step 3/3: analyzing selected audio...")
    run_analysis(
        script_path=analyzer_dir / "main.py",
        input_path=analysis_input_path,
        output_path=analysis_output_path,
    )

    print("")
    print("Pipeline completed.")
    print(f"Input media: {args.input}")
    print(f"Extracted wav: {extracted_audio_path}")
    print(f"Analysis input: {analysis_input_path}")
    print(f"Used separation: {used_separation}")
    print(f"Analysis JSON: {analysis_output_path}")


if __name__ == "__main__":
    main()

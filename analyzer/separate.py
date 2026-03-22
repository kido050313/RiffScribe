from __future__ import annotations

import argparse
from pathlib import Path

import soundfile as sf
import torch

from demucs.apply import BagOfModels, apply_model
from demucs.audio import AudioFile
from demucs.htdemucs import HTDemucs
from demucs.pretrained import get_model


SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def find_default_audio(extracted_dir: Path) -> Path | None:
    if not extracted_dir.exists():
        return None
    for path in sorted(extracted_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_SUFFIXES:
            return path
    return None


def load_model(model_name: str):
    model = get_model(name=model_name)
    max_allowed_segment = float("inf")
    if isinstance(model, HTDemucs):
        max_allowed_segment = float(model.segment)
    elif isinstance(model, BagOfModels):
        max_allowed_segment = model.max_allowed_segment

    model.cpu()
    model.eval()
    return model, max_allowed_segment


def load_track(track: Path, audio_channels: int, samplerate: int) -> torch.Tensor:
    return AudioFile(track).read(streams=0, samplerate=samplerate, channels=audio_channels)


def save_wav(source: torch.Tensor, destination: Path, samplerate: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    audio = source.detach().cpu().transpose(0, 1).numpy()
    sf.write(destination, audio, samplerate)


def separate_audio(
    input_path: Path,
    output_dir: Path,
    model_name: str,
    device: str,
    shifts: int,
    overlap: float,
    no_split: bool,
    segment: int | None,
    two_stems: str | None,
) -> Path:
    model, max_allowed_segment = load_model(model_name)
    if segment is not None and segment > max_allowed_segment:
        raise SystemExit(
            f"Cannot use a Transformer model with segment {segment}. Maximum is {max_allowed_segment}."
        )

    track_name = input_path.stem
    model_output_dir = output_dir / model_name / track_name
    model_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading audio for separation: {input_path}")
    wav = load_track(input_path, model.audio_channels, model.samplerate)

    ref = wav.mean(0)
    wav = wav - ref.mean()
    wav = wav / ref.std()

    with torch.no_grad():
        sources = apply_model(
            model,
            wav[None],
            device=device,
            shifts=shifts,
            split=not no_split,
            overlap=overlap,
            progress=True,
            num_workers=0,
            segment=segment,
        )[0]

    sources = sources * ref.std()
    sources = sources + ref.mean()

    if two_stems:
        if two_stems not in model.sources:
            raise SystemExit(
                f'Stem "{two_stems}" is not available in model sources: {", ".join(model.sources)}.'
            )
        source_index = model.sources.index(two_stems)
        target_source = sources[source_index]
        other_source = torch.zeros_like(target_source)
        for index, source in enumerate(sources):
            if index != source_index:
                other_source += source

        save_wav(target_source, model_output_dir / f"{two_stems}.wav", model.samplerate)
        save_wav(other_source, model_output_dir / f"no_{two_stems}.wav", model.samplerate)
    else:
        for source, name in zip(sources, model.sources):
            save_wav(source, model_output_dir / f"{name}.wav", model.samplerate)

    return model_output_dir


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
        default=None,
        help="Optional two-stem mode, for example 'vocals'. Defaults to full 4-stem separation.",
    )
    parser.add_argument(
        "--model",
        default="htdemucs",
        help="Demucs pretrained model name. Defaults to htdemucs.",
    )
    parser.add_argument(
        "--device",
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Computation device. Defaults to cuda if available, otherwise cpu.",
    )
    parser.add_argument("--shifts", type=int, default=1, help="Number of random shifts.")
    parser.add_argument("--overlap", type=float, default=0.25, help="Chunk overlap ratio.")
    parser.add_argument(
        "--no-split",
        action="store_true",
        help="Disable chunked inference. Can use much more memory.",
    )
    parser.add_argument(
        "--segment",
        type=int,
        help="Optional chunk size override in seconds.",
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

    result_dir = separate_audio(
        input_path=input_path,
        output_dir=separated_dir,
        model_name=args.model,
        device=args.device,
        shifts=args.shifts,
        overlap=args.overlap,
        no_split=args.no_split,
        segment=args.segment,
        two_stems=args.two_stems,
    )
    print(f"Separated stems for: {input_path.name}")
    print(f"Stems written under: {result_dir}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path
from statistics import mean, median

import cv2

from framework.contrib.detection import ColorMatchDetector


DEFAULT_WITH_INDICATOR_DIR = Path("frames/with_indicator")
DEFAULT_WITHOUT_INDICATOR_DIR = Path("frames/without_indicator")


def _parse_roi(value: str | None) -> tuple[int, int, int, int] | None:
    if value is None:
        return None
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("roi must be x,y,w,h")
    try:
        x, y, w, h = (int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("roi values must be integers") from exc
    return (x, y, w, h)


def _load_frames(directory: Path) -> list:
    if not directory.exists() or not directory.is_dir():
        raise FileNotFoundError(f"Frame directory not found: {directory}")

    files = sorted(path for path in directory.iterdir() if path.is_file())
    if not files:
        raise ValueError(f"Frame directory is empty: {directory}")

    frames = []
    for path in files:
        frame = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if frame is None:
            continue
        frames.append(frame)

    if not frames:
        raise ValueError(f"No readable image frames found in: {directory}")
    return frames


def _counts_for_detector(detector: ColorMatchDetector, frames: list) -> list[int]:
    return [detector.matched_pixel_count(frame) for frame in frames]


def _summary(name: str, counts: list[int]) -> str:
    counts_sorted = sorted(counts)
    return (
        f"{name}: n={len(counts_sorted)} min={counts_sorted[0]} "
        f"p50={int(median(counts_sorted))} avg={mean(counts_sorted):.2f} "
        f"max={counts_sorted[-1]}"
    )


def _score_threshold(with_counts: list[int], without_counts: list[int], threshold: int) -> tuple[int, int, int]:
    true_positives = sum(1 for c in with_counts if c >= threshold)
    true_negatives = sum(1 for c in without_counts if c < threshold)
    total = len(with_counts) + len(without_counts)
    correct = true_positives + true_negatives
    false_positives = len(without_counts) - true_negatives
    false_negatives = len(with_counts) - true_positives
    return correct, false_positives, false_negatives


def _suggest_threshold(with_counts: list[int], without_counts: list[int]) -> int:
    max_without = max(without_counts)
    min_with = min(with_counts)

    if max_without < min_with:
        return (max_without + min_with) // 2

    candidates = sorted(set(with_counts + without_counts))
    best_threshold = candidates[0]
    best_score = (-1, float("inf"), float("inf"))

    for threshold in candidates:
        correct, false_positives, false_negatives = _score_threshold(with_counts, without_counts, threshold)
        score = (correct, -false_positives, -false_negatives)
        if score > best_score:
            best_score = score
            best_threshold = threshold

    return best_threshold


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune drop indicator pixel threshold from captured frames.")
    parser.add_argument("--with-indicator-dir", type=Path, default=DEFAULT_WITH_INDICATOR_DIR)
    parser.add_argument("--without-indicator-dir", type=Path, default=DEFAULT_WITHOUT_INDICATOR_DIR)
    parser.add_argument("--hue-start", type=int, required=True)
    parser.add_argument("--hue-end", type=int, required=True)
    parser.add_argument("--saturation-min", type=int, required=True)
    parser.add_argument("--value-min", type=int, required=True)
    parser.add_argument("--roi", type=_parse_roi, default=None, help="Optional ROI as x,y,w,h")
    args = parser.parse_args()

    with_frames = _load_frames(args.with_indicator_dir)
    without_frames = _load_frames(args.without_indicator_dir)

    base_detector = ColorMatchDetector(
        hue_range=(args.hue_start, args.hue_end),
        saturation_min=args.saturation_min,
        value_min=args.value_min,
        pixel_threshold=0,
        roi=args.roi,
    )

    with_counts = _counts_for_detector(base_detector, with_frames)
    without_counts = _counts_for_detector(base_detector, without_frames)

    suggested_threshold = _suggest_threshold(with_counts, without_counts)

    print("Indicator tuning summary")
    print(_summary("with_indicator", with_counts))
    print(_summary("without_indicator", without_counts))
    print(f"suggested_pixel_threshold={suggested_threshold}")
    print("\nThreshold sweep")

    sweep_candidates = sorted(set(with_counts + without_counts))
    for threshold in sweep_candidates:
        correct, false_positives, false_negatives = _score_threshold(with_counts, without_counts, threshold)
        print(
            "threshold={threshold} correct={correct}/{total} false_pos={false_pos} false_neg={false_neg}".format(
                threshold=threshold,
                correct=correct,
                total=len(with_counts) + len(without_counts),
                false_pos=false_positives,
                false_neg=false_negatives,
            )
        )


if __name__ == "__main__":
    main()

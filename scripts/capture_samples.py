from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import cv2

from framework.contrib.hardware import AVerMediaCapture


DEFAULT_WITH_DIR = Path("frames/with_indicator")
DEFAULT_WITHOUT_DIR = Path("frames/without_indicator")


def _timestamp_name() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".png"


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture indicator and non-indicator sample frames.")
    parser.add_argument("--device-index", type=int, default=1)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=float, default=60.0)
    parser.add_argument("--capture-latency-frames", type=int, default=6)
    parser.add_argument("--backend", default="dshow")
    parser.add_argument("--with-dir", type=Path, default=DEFAULT_WITH_DIR)
    parser.add_argument("--without-dir", type=Path, default=DEFAULT_WITHOUT_DIR)
    args = parser.parse_args()

    args.with_dir.mkdir(parents=True, exist_ok=True)
    args.without_dir.mkdir(parents=True, exist_ok=True)

    capture = AVerMediaCapture(
        device_index=args.device_index,
        width=args.width,
        height=args.height,
        fps=args.fps,
        latency_frames=args.capture_latency_frames,
        backend=args.backend,
    )

    print("press w when indicator is visible, n when it's not")
    print("press q to quit")

    window_name = "diablo_bot sample capture"

    try:
        while True:
            stamped = capture.get_frame()
            frame = stamped.frame

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                print("Exiting capture.")
                break

            if key == ord("w"):
                out_path = args.with_dir / _timestamp_name()
                if cv2.imwrite(str(out_path), frame):
                    print(f"Saved with-indicator frame: {out_path}")
                else:
                    print(f"Failed to save with-indicator frame: {out_path}")

            if key == ord("n"):
                out_path = args.without_dir / _timestamp_name()
                if cv2.imwrite(str(out_path), frame):
                    print(f"Saved without-indicator frame: {out_path}")
                else:
                    print(f"Failed to save without-indicator frame: {out_path}")
    finally:
        capture.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

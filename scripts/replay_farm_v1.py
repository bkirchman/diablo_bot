from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

from framework.contrib.content_loops import ContentLoopProcessor, load_loops_from_file
from framework.contrib.hardware import ReplayCapture
from framework.interfaces import Action, OutputDevice
from framework.loop import BotLoop
from framework.temporal import FrameHistory

from diablo_bot.registries import build_command_registry, build_detector_registry


DEFAULT_REPLAY_DIR = Path("frames/replay")
DEFAULT_LOOPS_YAML = Path("configs/loops/farm_v1.yaml")

FISHING_TEMPLATE_HSV_CONFIG: Mapping[str, Any] = {
    "hue_range": (73, 84),
    "saturation_min": 95,
    "value_min": 100,
    "pixel_threshold": 7,
    "roi": (899, 217, 120, 120),
}


class DryRunOutput(OutputDevice):
    """Logs each action payload instead of sending controller UDP commands."""

    def execute(self, action: Action) -> None:
        print(f"[DRYRUN] frame_id={action.frame_id} timestamp={action.timestamp:.4f} payload={action.payload}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay one farm_v1 execution with dry-run output logging.")
    parser.add_argument("--replay-dir", type=Path, default=DEFAULT_REPLAY_DIR)
    parser.add_argument("--loops-yaml", type=Path, default=DEFAULT_LOOPS_YAML)
    parser.add_argument("--fps", type=float, default=60.0)
    parser.add_argument("--latency-frames", type=int, default=0)
    parser.add_argument("--history-capacity", type=int, default=512)
    args = parser.parse_args()

    loop_definitions = load_loops_from_file(args.loops_yaml)
    command_registry = build_command_registry()
    detector_registry = build_detector_registry(FISHING_TEMPLATE_HSV_CONFIG)

    processor = ContentLoopProcessor(
        loop_definitions=loop_definitions,
        command_registry=command_registry,
        detector_registry=detector_registry,
        loop_name="farm_v1",
    )

    capture = ReplayCapture(
        frames_dir=args.replay_dir,
        fps=args.fps,
        latency_frames=args.latency_frames,
    )
    output = DryRunOutput()
    history = FrameHistory(capacity=args.history_capacity)

    loop = BotLoop(capture=capture, output=output, processor=processor, history=history)
    loop.start()

    iterations = 0
    try:
        while processor.interpreter.status == "running":
            loop.step()
            iterations += 1
    except IndexError:
        print("Replay ended before farm_v1 completed; add more replay frames and try again.")
    except KeyboardInterrupt:
        print("Replay interrupted by user.")
    finally:
        loop.stop()

    print(f"Interpreter status: {processor.interpreter.status}")
    print(f"Iterations: {iterations}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from typing import Any, Mapping

from framework.contrib.content_loops import ContentLoopProcessor, load_loops_from_file
from framework.contrib.hardware import AVerMediaCapture, UDPXboxOutput
from framework.loop import BotLoop
from framework.temporal import FrameHistory

from diablo_bot.registries import build_command_registry, build_detector_registry


FISHING_TEMPLATE_HSV_CONFIG: Mapping[str, Any] = {
    "hue_range": (73, 84),
    "saturation_min": 95,
    "value_min": 100,
    "pixel_threshold": 7,
    "roi": (899, 217, 120, 120),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one live farm_v1 execution.")
    parser.add_argument("--loops-yaml", default="configs/loops/farm_v1.yaml")
    parser.add_argument("--device-index", type=int, default=1)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=float, default=60.0)
    parser.add_argument("--capture-latency-frames", type=int, default=6)
    parser.add_argument("--backend", default="dshow")
    parser.add_argument("--udp-ip", default="192.168.1.196")
    parser.add_argument("--udp-port", type=int, default=5005)
    parser.add_argument("--response-port", type=int, default=5006)
    parser.add_argument("--response-mode", type=int, default=0)
    parser.add_argument("--history-capacity", type=int, default=512)
    parser.add_argument("--debug-udp", action="store_true")
    args = parser.parse_args()

    capture = AVerMediaCapture(
        device_index=args.device_index,
        width=args.width,
        height=args.height,
        fps=args.fps,
        latency_frames=args.capture_latency_frames,
        backend=args.backend,
    )
    output = UDPXboxOutput(
        udp_ip=args.udp_ip,
        udp_port=args.udp_port,
        response_port=args.response_port,
        response_mode=args.response_mode,
        debug_mode=args.debug_udp,
    )

    # Pull runtime latency from the capture source; never hardcode a latency value.
    runtime_latency_frames = capture.latency_frames
    print(f"Runtime capture latency_frames={runtime_latency_frames}")

    loop_definitions = load_loops_from_file(args.loops_yaml)
    command_registry = build_command_registry()
    detector_registry = build_detector_registry(FISHING_TEMPLATE_HSV_CONFIG)
    processor = ContentLoopProcessor(
        loop_definitions=loop_definitions,
        command_registry=command_registry,
        detector_registry=detector_registry,
        loop_name="farm_v1",
    )

    history = FrameHistory(capacity=args.history_capacity)
    loop = BotLoop(capture=capture, output=output, processor=processor, history=history)
    loop.start()

    iterations = 0
    try:
        while processor.interpreter.status == "running":
            loop.step()
            iterations += 1
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        loop.stop()
        capture.close()
        output.close()

    print(f"Interpreter status: {processor.interpreter.status}")
    print(f"Iterations: {iterations}")


if __name__ == "__main__":
    main()

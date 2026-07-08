from __future__ import annotations

from typing import Any, Mapping

from framework.contrib.content_loops import CommandRegistry, DetectorRegistry
from framework.contrib.detection import ColorMatchDetector

# TODO: Verify against firmware mapping for this rig.
BUTTON_A_INDEX = 0

# TODO: Replace with verified move hold duration in milliseconds.
TBD_MS = 0


def build_command_registry() -> CommandRegistry:
    registry = CommandRegistry()

    # v2.1 firmware commands are single-packet with self-release durations.
    registry.register("dpad_up", lambda: {"hat_x": 0, "hat_y": -1, "hat_duration": 80})
    registry.register("move_left", lambda: {"move_x": -80, "move_y": 0, "move_duration": TBD_MS})
    registry.register(
        "press_a",
        lambda: {
            f"button_{BUTTON_A_INDEX}": 1,
            f"button_{BUTTON_A_INDEX}_duration": 80,
        },
    )
    registry.register("fire_trigger", lambda: {"trigger": 100, "trigger_duration": 200})

    return registry


def build_detector_registry(fishing_template_hsv_config: Mapping[str, Any]) -> DetectorRegistry:
    registry = DetectorRegistry()
    registry.register(
        "drop_indicator",
        ColorMatchDetector(
            hue_range=tuple(fishing_template_hsv_config["hue_range"]),
            saturation_min=int(fishing_template_hsv_config["saturation_min"]),
            value_min=int(fishing_template_hsv_config["value_min"]),
            pixel_threshold=int(fishing_template_hsv_config["pixel_threshold"]),
            roi=tuple(fishing_template_hsv_config["roi"]),
        ),
    )
    return registry

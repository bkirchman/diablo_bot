Project: diablo_bot — Diablo 4 fishing farm bot v1.
Consumer of bot_framework (installed as editable dependency via
`pip install -e ../bot_framework`, on the v0.1.0 tag).

This repo contains ONLY game knowledge: templates, macros, YAML loop
definitions, ROI coordinates, HSV thresholds, button indices. It
contains NO framework mechanism code. If a class or utility would
apply to any other game, it belongs in bot_framework/contrib/, not
here.

Hardware: same rig as bot_framework. Firmware v2.1 (from
bot_framework/firmware/xbox_controller/) — all commands are
self-releasing via duration parameters. Never write two-packet
press/release plumbing on the game side; use the duration form.

v1 scope: single fishing cycle. Setup sequence is
  D-pad up → left-stick left → A button
to initiate a cast. Detector is a ColorMatchDetector watching a teal
fishing indicator that fades in above the character and lasts ~30
frames (0.5s). Earlier detection = better loot, but the fade decays,
so peak brightness on frame 1 of visibility is the target signal.
Trigger response is a right-trigger burst. Loot collection is 8 A
presses with 0.3s spacing.

Available framework surface:
  from framework.interfaces import Action
  from framework.loop import BotLoop
  from framework.temporal import FrameHistory
  from framework.contrib.hardware import AVerMediaCapture, UDPXboxOutput
  from framework.contrib.detection import ColorMatchDetector
  from framework.contrib.content_loops import (
      CommandRegistry, DetectorRegistry, ContentLoopProcessor,
      load_loops_from_file,
  )

RULES FOR THIS SESSION:
1. Propose a plan and wait for approval before generating code.
2. Import framework code; never reimplement it.
3. OpenCV capture is 3 frames behind real time. Pull latency_frames
   from the CaptureSource at runtime — never hardcode 3.
4. Output one complete file at a time; wait for me between files.
5. All button and D-pad commands use the single-packet
   button_N_duration or hat_duration firmware form. Never emit
   separate press/release actions.
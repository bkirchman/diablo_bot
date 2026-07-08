# diablo_bot

Diablo 4 fishing farm bot v1 content project.

This repository contains game knowledge only:
- loop definitions
- detector tuning inputs
- command registry mappings
- frame datasets for tuning and replay

No framework mechanism code lives here.

## Prerequisites

This project consumes bot_framework from a sibling repository.

Install in editable mode from this repo root:

```bash
pip install -e ../bot_framework
pip install -e .
```

## Run Order

1. Tune indicator thresholds offline:

```bash
python scripts/tune_indicator.py \
  --hue-start 0 \
  --hue-end 0 \
  --saturation-min 0 \
  --value-min 0 \
  --roi 0,0,1,1
```

2. Replay farm loop with dry-run output logging:

```bash
python scripts/replay_farm_v1.py
```

3. Run live farm loop against capture + UDP output:

```bash
python scripts/run_farm_v1.py
```

## TODO Constants You Must Fill

- [src/diablo_bot/registries.py](src/diablo_bot/registries.py): set BUTTON_A_INDEX after firmware button mapping verification.
- [src/diablo_bot/registries.py](src/diablo_bot/registries.py): replace TBD_MS with validated move hold duration.
- [scripts/tune_indicator.py](scripts/tune_indicator.py): tune HSV and pixel threshold values from captured frames.
- [scripts/replay_farm_v1.py](scripts/replay_farm_v1.py): replace FISHING_TEMPLATE_HSV_CONFIG placeholder values.
- [scripts/run_farm_v1.py](scripts/run_farm_v1.py): replace FISHING_TEMPLATE_HSV_CONFIG placeholder values.

## Notes

- Firmware v2.1 command contract is single-packet with duration fields (button_N_duration, hat_duration, move_duration, trigger_duration).
- Do not split press/release into separate actions on the game side.

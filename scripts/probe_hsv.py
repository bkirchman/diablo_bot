import cv2
import numpy as np

# Replace with path to one of your with_indicator frames
frame = cv2.imread("frames/with_indicator/scene00155.png")

# Replace with your ROI (x, y, w, h)
x, y, w, h = 899, 217, 120, 120  # your values
roi = frame[y:y+h, x:x+w]

hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# Mask by high value + high saturation to isolate the bright teal pixels,
# ignoring background darkness
mask = (hsv[:,:,1] > 100) & (hsv[:,:,2] > 100)
teal_pixels = hsv[mask]

if len(teal_pixels) == 0:
    print("No bright pixels found — check ROI or lower thresholds")
else:
    hues = teal_pixels[:,0]
    sats = teal_pixels[:,1]
    vals = teal_pixels[:,2]
    print(f"Hue    range: {hues.min()}-{hues.max()}, median {int(np.median(hues))}")
    print(f"Sat    range: {sats.min()}-{sats.max()}, median {int(np.median(sats))}")
    print(f"Value  range: {vals.min()}-{vals.max()}, median {int(np.median(vals))}")
    print(f"Bright teal pixel count in ROI: {len(teal_pixels)}")
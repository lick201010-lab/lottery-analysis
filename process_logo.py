from PIL import Image
import numpy as np

# Load the original screenshot
img = Image.open(r'C:\Users\Yvette\AppData\Local\Temp\ScreenShot_2026-05-16_113858_491.png').convert('RGBA')
w, h = img.size

# Tight crop around the logo circle
cx = int(w * 0.129)
cy = int(h * 0.499)
r = int(w * 0.118)  # slightly smaller radius for tighter crop

left = cx - r
top = cy - r
right = cx + r
bottom = cy + r

# Ensure bounds
left = max(0, left)
top = max(0, top)
right = min(w, right)
bottom = min(h, bottom)

cropped = img.crop((left, top, right, bottom))

# Make background transparent
# The background is light pinkish/white, the logo is purple
arr = np.array(cropped)
# Find pixels that are close to background color (light, low saturation)
r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]

# Background detection: light pixels with similar R,G,B values
brightness = (r.astype(int) + g.astype(int) + b.astype(int)) / 3
max_diff = np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)

# Pixels that are light AND low saturation are background
bg_mask = (brightness > 200) & (max_diff < 30)
# Also mask out very light pixels regardless of saturation
bg_mask |= brightness > 245

arr[bg_mask] = [255, 255, 255, 0]

result = Image.fromarray(arr)
result.save(r'D:\六合彩\frontend\public\logo.png')
print('Saved transparent logo.png size=', result.size)

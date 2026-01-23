#!/usr/bin/env python3
"""Take a screenshot from the STB Tester device."""

import urllib.request
import os

PORTAL_URL = "https://ziggo.stb-tester.com"
PORTAL_TOKEN = "cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs"
DEVICE_ID = "stb-tester-48b02d5b0ab7"

url = f"{PORTAL_URL}/api/v2/nodes/{DEVICE_ID}/screenshot.png"
headers = {"Authorization": f"token {PORTAL_TOKEN}"}

request = urllib.request.Request(url, headers=headers)
print(f"Capturing screenshot from {DEVICE_ID}...")

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        image_data = response.read()
        save_path = "/Users/swatantrasohni/Downloads/stb-tester-main/device_screenshot.png"
        with open(save_path, "wb") as f:
            f.write(image_data)
        print(f"Screenshot saved to: {save_path}")
        print(f"Size: {len(image_data)} bytes")
except Exception as e:
    print(f"Error: {e}")

# Reference Images

This directory contains reference images used for visual matching in STB Tester tests.

## Directory Structure

```
reference_images/
├── epg/           # EPG/Guide screenshots
├── playback/      # Playback controls and video states
├── settings/      # Settings menus and options
└── common/        # Shared UI elements (logos, buttons)
```

## Naming Conventions

- Use lowercase with hyphens: `guide-open.png`, `pause-icon.png`
- Be descriptive: `bbc-one-channel-logo.png` not `logo1.png`
- Include state if relevant: `volume-slider-muted.png`

## Image Requirements

- **Format**: PNG (recommended) or JPEG
- **Resolution**: Match your capture device resolution (typically 1920x1080)
- **Cropping**: Crop to the smallest unique region that identifies the element
- **Consistency**: Capture images under the same conditions tests will run

## Adding Images

1. Capture screenshot using `stbt screenshot`
2. Crop to relevant region using an image editor
3. Save to appropriate subdirectory
4. Update test code to reference the new image

## Usage in Tests

```python
from conftest import get_reference_image

# Use helper function
stbt.wait_for_match(get_reference_image("epg/guide.png"))

# Or use direct path
stbt.wait_for_match("reference_images/epg/guide.png")
```

# Animation Presets Pro

A Blender addon for quick and easy animation presets with real-time controls and preview capabilities.

![Animation Presets Pro Preview](preview.gif)

## Features

- Easy-to-use animation presets with live previews
- Real-time animation speed control
- Full timeline control system
- Preview navigation with thumbnail support
- Support for GIF previews
- Semi-realistic VFX presets

## Installation

1. Download the latest release from the releases page
2. Open Blender and go to Edit > Preferences
3. Click on the "Add-ons" tab
4. Click "Install" and select the downloaded zip file
5. Enable the addon by checking the box next to "Animation: Animation Presets Pro"

## Usage

### Location
The addon can be found in the 3D Viewport's sidebar (Press N) under the "Animation" tab.

### Adding Animations
1. Select an object in your scene
2. Open the Animation tab in the sidebar
3. Browse through available presets using the navigation arrows
4. Click "Add Animation" to apply the selected preset to your object

### Animation Controls
- Use the timeline controls to:
  - Jump to first/last frame
  - Go to previous/next keyframe
  - Play/pause animation
  - Reset animation
- Adjust animation speed using the speed slider

## Creating Custom Presets

To add your own animation presets:

1. Navigate to the addon's presets folder:
```
blender_folder/VERSION/scripts/addons/animation_presets_pro/presets/
```

2. Add your preset files:
   - Animation file (preset_name.py)
   - Preview file (preset_name.gif)

### Preset File Structure
```python
import bpy

def create_animation(obj):
    # Your animation code here
    pass
```

## Known Issues

- GIF previews must be square format for best display
- Preview thumbnails require restart to update
- Speed control resets on file reload

## Support

For support and feature requests:
- Create an issue on GitHub
- Join our Discord community
- Check the documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

animation_presets_pro/
├── __init__.py              # Main addon file
├── operators.py             # Operator definitions
├── preview_generator.py     # Preview generation utilities
├── presets/                 # Preset files directory
│   ├── popup_rotation.gif   # Preview for popup rotation
│   └── scale_bounce.gif    # Preview for scale bounce
└── README.md               # This documentation

## Credits

Created by KLLC

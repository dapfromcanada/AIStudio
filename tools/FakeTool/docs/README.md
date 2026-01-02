# Fake Tool - Image Viewer

## Tool Purpose
Fake Tool is a simple image viewer application designed to test the AI Studio template system and launcher integration. It demonstrates the proper structure and conventions for AI Studio tools.

## Features
- 📁 **Folder Browser** - Browse and select folders containing images
- 🖼️ **Image Display** - View images with automatic scaling
- 📋 **File List** - List all images in selected folder with filtering
- 🔍 **Single Image Selection** - Browse and load individual images
- 📊 **Image Information** - Display image dimensions, format, and file size
- 📝 **Activity Logging** - Real-time log of all actions
- 🔧 **CLI Engine** - Headless engine for image analysis via command line

## Usage

### GUI Mode (Recommended)
1. **Run the GUI:**
   ```bash
   cd G:/AIStudio/tools/FakeTool
   .venv\Scripts\activate
   python main_gui.py
   ```

2. **Browse Images:**
   - Click "Browse Folder" to select a folder containing images
   - All images in the folder will appear in the left panel
   - Click any image in the list to display it
   - Or click "Browse Image" to select a single image file

3. **View Image Details:**
   - Selected image displays in the center panel
   - Image info shows filename, dimensions, and file size
   - Activity log shows all actions in real-time

### CLI Mode (Engine)
The engine can be run independently for headless operations:

```bash
# Test mode
python engine.py --config config.json --test

# Analyze a single image
python engine.py --config config.json --image "path/to/image.jpg"

# Scan a folder for images
python engine.py --config config.json --folder "path/to/folder"
```

## Configuration

### config.json Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | string | Internal tool identifier |
| `display_name` | string | Name shown in launcher |
| `version` | string | Tool version number |
| `supported_formats` | array | Image file extensions to recognize |
| `enable_logging` | boolean | Enable/disable file logging |
| `auto_scale_images` | boolean | Automatically scale images to fit display |
| `max_image_size_mb` | number | Maximum image file size to load |

### Supported Image Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)
- WebP (.webp)

## Data Requirements

### Input Data
- **Format:** Any standard image format (JPEG, PNG, BMP, GIF, TIFF, WebP)
- **Location:** Any accessible folder on the system
- **Size:** Configurable max size (default: 50MB per image)

### Output
- **Logs:** Activity logs stored in `logs/FakeTool_YYYYMMDD.log`
- **Status:** Real-time status in `logs/fake_tool_status.json`
- **Display:** Images rendered in GUI with scaling

## Dependencies

### Required Python Packages
- **PySide6 >= 6.6.0** - Qt framework for GUI
- **Pillow >= 10.0.0** - Image processing library

### Installation
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### System Requirements
- Python 3.8 or higher
- Windows, Linux, or macOS
- Display for GUI mode
- No GPU required

## Architecture

### File Structure
```
FakeTool/
├── main_gui.py          # Qt GUI controller (loads .ui dynamically)
├── interface.ui         # Qt Designer layout file
├── engine.py            # Headless image processing engine
├── config.json          # Tool configuration
├── requirements.txt     # Python dependencies
├── .venv/              # Virtual environment (not in Git)
├── logs/               # Runtime logs (not in Git)
│   ├── FakeTool_YYYYMMDD.log
│   └── fake_tool_status.json
└── docs/
    └── README.md        # This file
```

### Design Principles
- **Separation of Concerns:** GUI (main_gui.py) separate from logic (engine.py)
- **Dynamic UI Loading:** UI loaded from .ui file at runtime (not compiled)
- **Subprocess Architecture:** Engine runs as separate process from GUI
- **Configuration-Driven:** All settings in config.json (no hardcoded values)
- **Twin-Stream Logging:** Logs to both console and file
- **Status Monitoring:** Real-time status updates via JSON file

## Troubleshooting

### Common Issues

**Problem: "UI file not found" error**
- **Cause:** interface.ui is missing or in wrong location
- **Fix:** Ensure interface.ui exists in same folder as main_gui.py

**Problem: Images not loading**
- **Cause:** Unsupported format or file too large
- **Fix:** Check supported_formats in config.json and max_image_size_mb setting

**Problem: Engine fails to start**
- **Cause:** Virtual environment not activated or dependencies missing
- **Fix:** Run `.venv\Scripts\activate` and `pip install -r requirements.txt`

**Problem: No images showing in folder list**
- **Cause:** Folder contains no supported image formats
- **Fix:** Verify folder has .jpg, .png, .bmp, .gif, .tiff, or .webp files

**Problem: "ModuleNotFoundError: No module named 'PySide6'"**
- **Cause:** PySide6 not installed
- **Fix:** Install with `pip install PySide6>=6.6.0`

### Log Files
Check these files for diagnostic information:
- `logs/FakeTool_YYYYMMDD.log` - Detailed activity log
- `logs/fake_tool_status.json` - Current engine status

## Testing

### Quick Test
```bash
# 1. Activate environment
.venv\Scripts\activate

# 2. Run engine test
python engine.py --config config.json --test

# 3. Launch GUI
python main_gui.py
```

### Expected Behavior
1. GUI window opens (900x700 pixels)
2. "Browse Folder" button opens folder dialog
3. Images from selected folder populate the list
4. Clicking image in list displays it in viewer
5. Image info shows filename, dimensions, size
6. Activity log records all actions
7. Engine analysis runs in background

## Integration with AI Studio

### Launcher Registration
To register this tool with the master launcher, add to `G:/AIStudio/studio_config.json`:

```json
{
  "id": "fake_tool",
  "display_name": "Fake Tool - Image Viewer",
  "description": "Test tool for template validation and image viewing",
  "path": "G:/AIStudio/tools/FakeTool",
  "entry_point": "main_gui.py",
  "icon": "icon.png",
  "category": "Testing",
  "enabled": true
}
```

## Version History
- **1.0.0** (2026-01-01) - Initial release
  - Basic image viewing functionality
  - Folder and file browsing
  - CLI engine for image analysis
  - Template compliance

## Future Enhancements
- Image editing capabilities
- Batch processing support
- Thumbnail preview mode
- Image format conversion
- Metadata editing (EXIF data)

## License
Part of AI Studio Master Blueprint

## Support
For issues or questions about this tool template, refer to `TEMPLATE_INSTRUCTIONS.md`

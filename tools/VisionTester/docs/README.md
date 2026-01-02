# 📊 Vision Tester - User Guide

**Version:** 1.0.0  
**Last Updated:** January 2, 2026

---

## What is Vision Tester?

Vision Tester is a comprehensive YOLO object detection testing tool designed for the AI Studio ecosystem. It provides both a user-friendly GUI interface and a headless CLI engine for running object detection on images and batches of images.

### Key Features:
- 🚀 **Multi-YOLO Support** - YOLOv5, YOLOv8, YOLOv9, YOLOv10, YOLO11, YOLO12
- 💡 **Dual Mode** - GUI for interactive use, CLI engine for AWS/automation
- ⚡ **Real-time Detection** - Fast object detection with adjustable confidence
- 📁 **Batch Processing** - Process entire folders of images automatically
- 🎨 **Visual Results** - Annotated images with bounding boxes
- 📝 **Text Output** - Optional detection results in text format

---

## Getting Started

### Installation

1. **Navigate to tool directory:**
```bash
cd G:\AIStudio\tools\VisionTester
```

2. **Activate virtual environment:**
```bash
.venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

**Note:** First run will download YOLO model weights automatically (~100MB+).

### First Run

**GUI Mode:**
```bash
python main_gui.py
```

**CLI Mode (Test):**
```bash
python engine.py --config config.json --mode single --input "test.jpg" --output "output.jpg" --test
```

---

## Interface Guide

### Main Window

The Vision Tester GUI is divided into two main sections:

#### Left Panel - Controls
- **Model Configuration** - Select and load YOLO models
- **Detection Settings** - Adjust confidence threshold
- **Input/Output** - Select images/folders
- **Actions** - Run detection operations
- **Status Log** - View operation progress

#### Right Panel - Display
- **Input Image Tab** - View selected input image
- **Output Image Tab** - View detection results

### Buttons and Controls

**Model Configuration:**
- **Select Model** - Choose from available YOLO models
- **Load Model** - Load the selected model into memory

**Detection Settings:**
- **Confidence Threshold Slider** - Set detection confidence (0.01-1.00)
- **Save text results** - Export detections to .txt files

**Input/Output:**
- **Select Image** - Choose a single image for detection
- **Select Input Folder** - Choose folder for batch processing
- **Select Output Folder** - Choose where to save results

**Actions:**
- **Detect Single Image** - Run detection on one image
- **Detect Batch** - Process all images in selected folder

---

## Configuration

### config.json Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tool_name` | string | vision_tester | Tool identifier |
| `version` | string | 1.0.0 | Tool version |
| `paths.raw_data` | string | (path) | Input data directory |
| `paths.processed_data` | string | (path) | Processed output directory |
| `paths.model_output` | string | (path) | Model exports directory |
| `model.name` | string | yolo11x.pt | Default YOLO model |
| `model.confidence_threshold` | float | 0.25 | Detection confidence (0.0-1.0) |
| `model.filter_classes` | array/null | null | Filter specific COCO classes |
| `options.save_detections_txt` | boolean | false | Save text detection files |
| `options.enable_logging` | boolean | true | Enable file logging |
| `options.log_level` | string | INFO | Log verbosity level |

### Example Configuration

```json
{
  "tool_name": "vision_tester",
  "version": "1.0.0",
  "model": {
    "name": "yolo11x.pt",
    "confidence_threshold": 0.25,
    "filter_classes": null
  },
  "options": {
    "save_detections_txt": true,
    "enable_logging": true
  }
}
```

---

## Available Models

### YOLOv5
- `yolov5n.pt` - Nano (fastest, smallest)
- `yolov5s.pt` - Small
- `yolov5m.pt` - Medium
- `yolov5l.pt` - Large
- `yolov5x.pt` - XLarge (most accurate)

### YOLOv8
- `yolov8n.pt` through `yolov8x.pt` (same size variants)

### YOLOv9
- `yolov9c.pt` - Compact
- `yolov9e.pt` - Extended

### YOLOv10
- `yolov10n.pt` through `yolov10x.pt`
- `yolov10b.pt` - Balanced (recommended)

### YOLO11 (Recommended)
- `yolo11n.pt` through `yolo11x.pt`
- Latest stable version with best performance

### YOLO12 (Cutting Edge)
- `yolo12n.pt` through `yolo12x.pt`
- Newest model with attention mechanisms

**Model Selection Guide:**
- **Nano/Small** - Real-time applications, edge devices
- **Medium** - Balanced speed and accuracy (recommended)
- **Large/XLarge** - Maximum accuracy, offline processing

---

## CLI Usage

### Engine Command Structure

```bash
python engine.py --config CONFIG --mode MODE --input INPUT --output OUTPUT [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--config` | Yes | Path to config.json |
| `--mode` | Yes | `single` or `batch` |
| `--input` | Yes | Input image or folder path |
| `--output` | Yes | Output image or folder path |
| `--save-txt` | No | Save detection text files |
| `--test` | No | Test mode (validate only) |

### Examples

**Single Image Detection:**
```bash
python engine.py --config config.json --mode single --input "G:/images/test.jpg" --output "G:/results/detected.jpg"
```

**Batch Processing:**
```bash
python engine.py --config config.json --mode batch --input "G:/images/batch/" --output "G:/results/batch/" --save-txt
```

**Test Mode:**
```bash
python engine.py --config config.json --mode single --input "test.jpg" --output "out.jpg" --test
```

---

## Data Requirements

### Input Formats
- **Images:** JPG, JPEG, PNG, BMP
- **Resolution:** Any (automatically resized by YOLO)
- **Color:** RGB or grayscale

### Output Formats
- **Images:** Annotated images with bounding boxes
- **Text Files:** Detection results in YOLO format (optional)

### Text File Format
Each detection on one line:
```
class_id confidence x1 y1 x2 y2
```

Example:
```
0 0.9543 120.50 45.20 380.10 520.75
2 0.8721 450.00 100.30 650.25 400.60
```

---

## Dependencies

### Core Requirements
- **Python** 3.8+ (3.10+ recommended)
- **CUDA** 11.8+ (for GPU acceleration)
- **RAM** 8GB minimum (16GB recommended)
- **Storage** 10GB for models and data

### Package Dependencies
- **PySide6** - GUI framework
- **ultralytics** - YOLO implementation
- **torch** - Deep learning backend
- **opencv-python** - Image processing
- **numpy** - Numerical operations

See `requirements.txt` for complete list.

---

## Troubleshooting

### Common Issues

**Problem:** GUI window is blank or widgets not showing
- **Solution:** This indicates improper UI loading. Verify interface.ui file exists and is valid XML. Check that all QMainWindow components are properly transferred in main_gui.py.

**Problem:** "Ultralytics not installed" error
- **Solution:** Activate virtual environment and run: `pip install ultralytics`

**Problem:** CUDA out of memory
- **Solution:** Use smaller model (nano/small), reduce image resolution, or switch to CPU mode

**Problem:** Model download fails
- **Solution:** Check internet connection. Models auto-download on first use. Manually download from Ultralytics GitHub if needed.

**Problem:** Detection results are poor
- **Solution:** Adjust confidence threshold (try 0.15-0.35 range). Use larger model for better accuracy. Ensure input images are clear and well-lit.

**Problem:** Batch processing is slow
- **Solution:** Use GPU acceleration. Choose faster model (nano/small). Process smaller batches.

**Problem:** Engine.py subprocess fails
- **Solution:** Check Python path in subprocess call. Ensure virtual environment is activated. Verify config.json is valid JSON.

---

## Workflow Examples

### Example 1: Quick Single Image Test

1. Launch GUI: `python main_gui.py`
2. Select model: `yolo11m.pt` (balanced)
3. Click "Load Model"
4. Click "Select Image" → choose test image
5. Click "Detect Single Image"
6. View results in "Output Image" tab

### Example 2: Batch Processing for Dataset

1. Prepare images in folder: `G:/datasets/test_images/`
2. Launch engine:
```bash
python engine.py \
  --config config.json \
  --mode batch \
  --input "G:/datasets/test_images/" \
  --output "G:/datasets/results/" \
  --save-txt
```
3. Results saved to output folder with annotations and text files

### Example 3: AWS Automation

1. Upload tool and data to EC2 instance
2. Install dependencies: `pip install -r requirements.txt`
3. Run headless detection:
```bash
python engine.py --config config.json --mode batch --input /data/images/ --output /data/results/
```
4. Download results from S3 bucket

---

## Performance Tips

### Speed Optimization
- Use smaller models (nano, small, medium)
- Enable GPU acceleration (CUDA)
- Batch process instead of single images
- Reduce image resolution if acceptable

### Accuracy Optimization
- Use larger models (large, xlarge)
- Adjust confidence threshold (0.15-0.35)
- Ensure good image quality
- Use YOLO11 or YOLO12 for best results

### Resource Management
- Monitor GPU memory usage
- Process images in smaller batches if memory limited
- Close other applications during processing
- Use SSD storage for faster I/O

---

## Integration with AI Studio

Vision Tester is designed to integrate seamlessly with the AI Studio ecosystem:

### Data Flow
1. **Input:** Raw images from `G:/AIStudio/data/raw/vision_tester/`
2. **Processing:** Detection via GUI or CLI engine
3. **Output:** Results to `G:/AIStudio/models/vision_tester/exports/`

### Master Launcher Integration
The tool can be registered in `studio_config.json`:

```json
{
  "id": "vision_tester",
  "display_name": "Vision Tester",
  "description": "YOLO object detection testing tool",
  "path": "G:/AIStudio/tools/VisionTester",
  "entry_point": "main_gui.py",
  "category": "Testing",
  "enabled": true
}
```

---

## Advanced Usage

### Custom Class Filtering

Edit `config.json` to filter specific COCO classes:

```json
{
  "model": {
    "filter_classes": [0, 1, 2, 3, 5, 6, 7]
  }
}
```

**Common COCO Class IDs:**
- 0: person
- 1: bicycle
- 2: car
- 3: motorcycle
- 5: bus
- 6: train
- 7: truck

### Monitoring Status (Subprocess Mode)

The engine writes progress to `logs/vision_tester_status.json`:

```json
{
  "status": "running",
  "progress": 50,
  "message": "Processing image 10/20",
  "timestamp": "2026-01-02T14:30:00"
}
```

GUI can monitor this file for real-time progress updates.

---

## File Structure

```
vision_tester/
├── main_gui.py              # PySide6 GUI application
├── interface.ui             # Qt Designer UI file
├── engine.py                # Headless CLI engine
├── config.json              # Configuration file
├── detector_interface.py    # Abstract detector interface
├── detector_factory.py      # Factory pattern for detectors
├── ultralytics_detector.py  # Ultralytics YOLO implementation
├── requirements.txt         # Python dependencies
├── .venv/                   # Virtual environment (not in Git)
├── logs/                    # Runtime logs (not in Git)
│   ├── vision_tester_*.log
│   └── vision_tester_status.json
├── docs/                    # Documentation
│   └── README.md            # This file
└── tests/                   # Unit tests (optional)
    └── test_engine.py
```

---

## Support and Contribution

### Reporting Issues
- Check troubleshooting section first
- Review logs in `logs/` directory
- Include error messages and configuration

### Future Enhancements
- [ ] Video processing support
- [ ] Webcam/stream support
- [ ] Custom model training
- [ ] Export to ONNX/TensorRT
- [ ] Class filter presets in GUI
- [ ] Performance benchmarking

---

## License

This tool is part of the AI Studio project.

**Dependencies:**
- Ultralytics: AGPL-3.0
- PySide6: LGPL
- PyTorch: BSD-3-Clause

---

## Version History

### 1.0.0 (2026-01-02)
- Initial release
- PySide6 GUI implementation
- Headless CLI engine
- Support for YOLOv5-12
- Single and batch detection modes
- Configuration system
- Twin-stream logging

# 📄 Markdown Converter - User Guide

**Version:** 1.0.0  
**Last Updated:** January 2, 2026

---

## What is MD Converter?

**MD Converter** is an AI-powered document conversion tool that transforms various file formats into clean, formatted Markdown (.md) files. It uses docling's advanced AI models for intelligent document understanding and extraction.

### Key Features:
- 🚀 **Batch Conversion** - Convert multiple files at once
- 🤖 **AI-Powered** - Uses docling for intelligent document extraction
- 📋 **Multi-Format Support** - PDF, Office docs, images, HTML, spreadsheets, text
- 🖼️ **OCR Capabilities** - Extract text from images automatically
- 📊 **Real-time Progress** - Live conversion status and logging
- 💾 **Persistent Settings** - Remembers your folder preferences
- 🔧 **CLI Mode** - Headless batch processing for automation

---

## Supported File Formats

### Documents
- **PDF** (.pdf) - Portable Document Format
- **Word** (.docx, .doc) - Microsoft Word documents  
- **PowerPoint** (.pptx, .ppt) - Microsoft PowerPoint presentations

### Images (OCR)
- **PNG** (.png) - Portable Network Graphics
- **JPEG** (.jpg, .jpeg) - Joint Photographic Experts Group
- **GIF** (.gif) - Graphics Interchange Format
- **BMP** (.bmp) - Bitmap Image
- **TIFF** (.tiff) - Tagged Image File Format

### Web & Data
- **HTML** (.html, .htm) - HyperText Markup Language
- **Excel** (.xlsx, .xls) - Microsoft Excel spreadsheets

### Text
- **Plain Text** (.txt) - Text files
- **RTF** (.rtf) - Rich Text Format
- **ODT** (.odt) - OpenDocument Text

---

## Getting Started

### First Launch

1. **Open Terminal** in AI Studio:
   ```powershell
   cd G:\AIStudio
   ```

2. **Launch from AIStudio** (recommended):
   - Start AIStudio
   - Select "Markdown Converter"
   - Click "Launch Tool"

3. **Or launch directly**:
   ```powershell
   cd tools\md_converter
   .venv\Scripts\python.exe main_gui.py
   ```

### Initial Setup

1. **Set Input Folder**: Click "📁 Browse Input" and select folder with files to convert
2. **Set Output Folder**: Click "📁 Browse Output" and select destination for .md files
3. **Your settings are automatically saved** for next time

---

## Main Interface Guide

### Folder Selection (Top Panel)

**Input Folder**
- Location of files to convert
- Click "📁 Browse Input" to change
- Shows "No folder selected" if not set

**Output Folder**
- Destination for converted .md files
- Click "📁 Browse Output" to change
- Defaults to: `G:/AIStudio/data/processed/md_converter`

### Files to Convert (Left Panel)

- **Automatically scans** input folder on launch
- Lists all compatible files found
- Click **🔄 Refresh File List** to rescan after adding files
- Shows filename only (not full path)

### Converted Files (Right Panel)

- Shows successfully converted files during batch process
- Displays output filenames (.md extension)
- Cleared when starting new conversion

### Conversion Progress (Bottom Panel)

- **Progress Bar**: Shows conversion completion percentage
- **Activity Log**: Real-time status messages with timestamps
- **🧹 Clear Log**: Clears the activity log

### Action Buttons

**▶️ Convert Files**
- Starts batch conversion of all listed files
- Processes files one at a time
- Shows progress in real-time
- Displays completion dialog when done

**📖 Help**
- Opens this documentation in beautiful dark theme
- Always available for reference

---

## Using the Tool

### Basic Workflow

1. **Select folders** (input and output)
2. **Review file list** (auto-populated)
3. **Click "▶️ Convert Files"**
4. **Monitor progress** in log
5. **Check output folder** for .md files

### Batch Converting Files

The tool converts all files in sequence:

1. Each file appears in log with `[1/10]` counter
2. Success: ✓ message + file added to "Converted Files" list
3. Failure: ✗ message with error details
4. Final summary: "X successful, Y failed"

### Conversion Examples

**PDF Document** → Clean markdown with preserved structure  
**Word Document** → Formatted text with headings  
**PowerPoint** → Slide content as sections  
**Image with Text** → OCR-extracted text  
**Excel Spreadsheet** → Tables in markdown format  
**HTML Page** → Converted web content  

---

## CLI Mode (Headless Operation)

For automation and AWS deployment:

### Test Mode
```bash
.venv\Scripts\python engine.py --config config.json --test
```

### Convert Single File
```bash
.venv\Scripts\python engine.py --config config.json --file "input.pdf" --output "G:/output"
```

### Convert Entire Folder
```bash
.venv\Scripts\python engine.py --config config.json --folder "G:/input" --output "G:/output"
```

### Exit Codes
- `0` - Success
- `1` - Failure or errors

---

## Configuration

### config.json

Located in tool folder: `tools/md_converter/config.json`

```json
{
  "tool_name": "md_converter",
  "version": "1.0.0",
  "paths": {
    "output_folder": "G:/AIStudio/data/processed/md_converter"
  },
  "options": {
    "supported_formats": ["pdf", "docx", "png", "html", ...],
    "enable_logging": true,
    "batch_processing": true
  }
}
```

### settings.ini

Auto-generated file storing user preferences:

```ini
[Paths]
InputPath = G:/path/to/input
OutputPath = G:/path/to/output
```

**Location:** `tools/md_converter/settings.ini`  
**Note:** Automatically created on first folder selection

---

## Troubleshooting

### Common Issues

**Problem: "No files found"**
- **Cause:** Input folder is empty or contains unsupported file types
- **Solution:** Check folder has PDF, DOCX, images, etc.

**Problem: Conversion fails with error**
- **Cause:** Corrupt file, unsupported format variant, or missing permissions
- **Solution:** Check log for specific error, try file manually

**Problem: "Folders Not Set" message**
- **Cause:** Input or output folder not selected
- **Solution:** Click Browse buttons to set both folders

**Problem: OCR not extracting text from images**
- **Cause:** Image quality too low or text too small
- **Solution:** Use higher resolution images (300+ DPI recommended)

**Problem: First conversion is slow**
- **Cause:** Docling downloading AI models on first run (one-time only)
- **Solution:** Wait for download to complete (automatic, ~200MB)

### Log Files

Check these files for diagnostic information:

- **Activity Log** (in GUI): Real-time conversion status
- **Log Files** (in logs/ folder): `md_converter_YYYYMMDD_HHMMSS.log`
- **Status File**: `logs/md_converter_status.json` (for GUI/engine communication)

### Getting Help

- Click **📖 Help** button in tool for this documentation
- Check logs folder for detailed error messages
- Review [AI Studio Master Blueprint](G:/AIStudioSetup/AI%20Studio%20Master%20Blueprint.md)

---

## File Structure

```
md_converter/
├── main_gui.py              # GUI controller
├── interface.ui             # Qt Designer UI layout
├── engine.py                # Headless CLI engine
├── convert.py               # Docling conversion logic
├── foldersandfiles.py       # File scanning utilities
├── config.json              # Tool configuration
├── requirements.txt         # Python dependencies
├── settings.ini             # User preferences (auto-created)
├── .venv/                   # Virtual environment
├── logs/                    # Conversion logs
│   ├── md_converter_*.log
│   └── md_converter_status.json
└── docs/
    └── README.md            # This file
```

---

## Advanced Usage

### Integrating with AI Studio

MD Converter follows AI Studio standards:

- **Isolated Environment**: Own `.venv` with dependencies
- **Configuration-Driven**: All settings in `config.json`
- **Twin-Stream Logging**: Console + file logging
- **Status Monitoring**: Real-time progress via JSON
- **CLI-Ready**: Headless operation for AWS deployment

### Automating Conversions

Create batch script for recurring conversions:

```powershell
# convert_daily.ps1
$input = "G:\Documents\Daily"
$output = "G:\AIStudio\data\processed\md_converter\daily"

cd G:\AIStudio\tools\md_converter
.\.venv\Scripts\python.exe engine.py --config config.json --folder $input --output $output

Write-Host "Daily conversion complete"
```

Run with Task Scheduler for automation.

### Custom Output Paths

Modify `config.json` to change default output location:

```json
{
  "paths": {
    "output_folder": "D:/MyMarkdownFiles"
  }
}
```

---

## Best Practices

### Do:
- ✅ Use high-quality source files (clear scans, not compressed PDFs)
- ✅ Organize input files into topic-based folders
- ✅ Review converted markdown for formatting
- ✅ Keep first-run conversion small (docling downloads models)
- ✅ Check logs if conversions fail

### Don't:
- ❌ Convert password-protected PDFs (not supported)
- ❌ Expect perfect OCR from blurry images
- ❌ Delete input files until verifying output
- ❌ Convert same folder repeatedly (check output first)
- ❌ Force quit during conversion (let it complete)

---

## Version History

### v1.0.0 (January 2, 2026)
- ✅ Initial release
- ✅ Multi-format document conversion
- ✅ AI-powered extraction with docling
- ✅ Batch processing with progress tracking
- ✅ GUI and CLI modes
- ✅ Persistent settings
- ✅ Comprehensive logging
- ✅ Help viewer integration

---

## Technologies Used

- **PySide6** - Qt framework for GUI
- **docling** - AI-powered document conversion
- **Python 3.8+** - Core programming language
- **markdown** - Help documentation rendering

---

## Next Steps

### Create Your First Conversion

1. Gather some PDFs, Word docs, or images
2. Place them in a folder
3. Launch MD Converter
4. Set input folder
5. Click "▶️ Convert Files"
6. Check output folder for .md files!

### Explore AI Studio

- Build more tools using `tools/tools_template/TEMPLATE_INSTRUCTIONS.md`
- Integrate conversions into your AI workflows
- Share converted markdown with other AI tools

---

**Happy Converting! 🚀**

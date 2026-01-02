# 🛠️ Tool Creation Template & Instructions

**Purpose:** This document guides the creation of a new AI tool following the AI Studio Master Blueprint standards.

---

## When You Read This Document

After reading this file, you should:
1. ✅ Understand the complete tool structure
2. ✅ Know all file requirements and naming conventions
3. ✅ Be ready to ask: **"What tool would you like to build? Describe its purpose and main features."**

---

## Tool Architecture Overview

Every tool in AI Studio follows this structure:

```
tools/
  └── {tool_name}/              # snake_case folder name
      ├── main_gui.py           # Qt UI controller (loads .ui dynamically)
      ├── interface.ui          # Qt Designer layout file
      ├── engine.py             # Headless AI engine (CLI-ready for AWS)
      ├── config.json           # Tool configuration (paths, hyperparameters)
      ├── requirements.txt      # Python dependencies
      ├── .venv/                # Isolated virtual environment (NOT in Git)
      ├── logs/                 # Runtime logs (NOT in Git)
      │   └── {tool}_status.json
      ├── docs/                 # Tool documentation
      │   └── README.md
      └── tests/                # Unit tests (optional but recommended)
          └── test_engine.py
```

---

## Step-by-Step Creation Workflow

### STEP 1: Initial Setup
**What to create:**
1. New folder in `G:/AIStudio/tools/` with snake_case name
2. Navigate into the folder
3. Create virtual environment: `python -m venv .venv`
4. Activate: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
5. Create empty files: `main_gui.py`, `engine.py`, `config.json`, `requirements.txt`
6. Create subfolders: `logs/`, `docs/`, `tests/`

---

### STEP 2: Build the UI (Qt Designer)
**File:** `interface.ui`

**Rules:**
- Must be created in Qt Designer (NOT hand-coded)
- Load at runtime with `QUiLoader` from PySide6 (never convert to .py)
- Widget naming: `{type}_{description}` (e.g., `btn_start_train`, `txt_dataset_path`)
- Minimum widgets needed:
  - Start/Stop buttons
  - Progress bar or status label
  - Log display (QTextEdit or QPlainTextEdit)
  - Settings/config inputs

**Design Principles:**
- Clean, professional layout
- Group related controls in QGroupBox
- Use layouts (QVBoxLayout, QHBoxLayout) not absolute positioning
- Add icons/labels for clarity

**⚠️ CRITICAL - If Hand-Coding UI XML:**
If Qt Designer is unavailable and you must hand-code the .ui file:
- **ALWAYS use `class` attribute for widget type:** `<widget class="QGroupBox" name="grp_folders">`
- **NEVER duplicate `name` attribute:** ❌ `<widget name="QGroupBox" name="grp_folders">` 
- Widget syntax: `<widget class="{WidgetClass}" name="{instance_name}">`
- Test immediately: Run `python main_gui.py` to catch XML syntax errors early
- Common error: "Attribute 'name' redefined" means you used `name` instead of `class`

---

### STEP 3: Build the Engine (Headless AI Logic)
**File:** `engine.py`

**Requirements:**
1. **Must be CLI-runnable:** `python engine.py --arg1 value --arg2 value`
2. **No GUI imports:** Cannot import PySide6, PyQt or any UI libraries
3. **Full logging:** Use Twin-Stream logging (console + file)
4. **Progress reporting:** Write to `logs/{tool}_status.json`
5. **Graceful shutdown:** Catch SIGTERM, KeyboardInterrupt, save state
6. **Test mode:** Include `--test` flag for quick validation

**Template Structure:**
```python
import argparse
import logging
import json
from pathlib import Path

class ToolEngine:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.setup_logging()
    
    def setup_logging(self):
        # Twin-stream: console + file
        pass
    
    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def update_status(self, status, progress, message):
        # Write to logs/{tool}_status.json
        pass
    
    def run(self):
        # Main AI logic here
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    
    engine = ToolEngine(args.config)
    engine.run()
```

---

### STEP 4: Build the GUI Controller
**File:** `main_gui.py`

**Requirements:**
1. Loads `interface.ui` dynamically (not hardcoded)
2. Connects UI signals to engine calls
3. Launches engine.py as subprocess (NOT in-process)
4. Monitors `logs/{tool}_status.json` to update UI
5. Displays real-time logs from engine stdout/stderr

**Template Structure:**
```python
import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                               QTextEdit, QProgressBar, QToolBar)  # Import widget classes!
from PySide6.QtCore import QTimer, QFile
from PySide6.QtUiTools import QUiLoader

class ToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = Path(__file__).parent / "interface.ui"
        
        # Load UI with QUiLoader
        ui_file = QFile(str(ui_path))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        # CRITICAL: Load with None parent, then transfer ALL components
        loaded_window = loader.load(ui_file, None)
        ui_file.close()
        
        # Transfer ALL QMainWindow components to prevent loss
        # Menu bar, status bar, toolbars would be garbage collected otherwise!
        if loaded_window.menuBar():
            self.setMenuBar(loaded_window.menuBar())
        if loaded_window.statusBar():
            self.setStatusBar(loaded_window.statusBar())
        # Transfer any toolbars
        for toolbar in loaded_window.findChildren(QToolBar):
            self.addToolBar(toolbar)
        # Transfer central widget
        central = loaded_window.centralWidget()
        self.setCentralWidget(central)
        
        # Get widget references using findChild (from central widget)
        self.btn_start = central.findChild(QPushButton, "btn_start")
        self.btn_stop = central.findChild(QPushButton, "btn_stop")
        self.txt_log = central.findChild(QTextEdit, "txt_log")
        self.progress_bar = central.findChild(QProgressBar, "progress_bar")
        
        self.engine_process = None
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_progress)
        
        self.connect_signals()
    
    def connect_signals(self):
        # Connect buttons to methods
        if self.btn_start:  # Check widget exists
            self.btn_start.clicked.connect(self.start_engine)
        if self.btn_stop:
            self.btn_stop.clicked.connect(self.stop_engine)
    
    def start_engine(self):
        # Launch engine.py as subprocess
        config_path = Path(__file__).parent / "config.json"
        venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
        self.engine_process = subprocess.Popen(
            [str(venv_python), "engine.py", "--config", str(config_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.status_timer.start(2000)  # Poll every 2 seconds
    
    def update_progress(self):
        # Read logs/{tool}_status.json and update UI
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToolGUI()
    window.show()
    sys.exit(app.exec())
```

---

### STEP 5: Create Configuration File
**File:** `config.json`

**Required Structure:**
```json
{
  "tool_name": "tool_name_here",
  "version": "1.0.0",
  "paths": {
    "raw_data": "G:/AIStudio/data/raw/{tool_specific}",
    "processed_data": "G:/AIStudio/data/processed/{tool_specific}",
    "model_output": "G:/AIStudio/models/{tool_name}/exports"
  },
  "hyperparameters": {
    "epochs": 100,
    "batch_size": 16,
    "learning_rate": 0.001
  },
  "options": {
    "use_gpu": true,
    "save_checkpoints": true,
    "enable_logging": true
  }
}
```

**Customization Rules:**
- Add tool-specific hyperparameters as needed
- Use absolute paths with G:/AIStudio/ prefix
- Keep options as booleans for easy GUI toggles

---

### STEP 6: Dependencies
**File:** `requirements.txt`

**Format:**
```
# GUI dependencies (NOT for AWS)
PySide6>=6.6.0

# AI/ML dependencies (for AWS)
torch>=2.0.0
numpy>=1.24.0
Pillow>=10.0.0
# Add tool-specific libraries here

# Utilities
tqdm>=4.65.0
```

**Rules:**
- Pin major versions (`>=X.0,<Y.0`) to prevent breaking changes
- Comment GPU requirements: `# Requires CUDA 11.8+`
- Separate sections for GUI vs. Engine dependencies
- Create `requirements-dev.txt` for testing tools (pytest, black, etc.)

---

### STEP 7: Documentation
**File:** `docs/README.md`

**Format:** Markdown (will render beautifully in help viewer)

**Required Sections:**
1. **Tool Purpose:** What does this tool do?
2. **Features:** Bullet list of capabilities
3. **Usage:** How to run via GUI and via CLI (engine.py)
4. **Configuration:** Explain config.json parameters
5. **Data Requirements:** Input/output formats
6. **Dependencies:** Special setup (GPU drivers, datasets)
7. **Troubleshooting:** Common errors and fixes
8. **Examples:** Screenshots, code examples, sample outputs

**Markdown Best Practices:**
- Use `# Tool Name` for main title
- Use `## Section Name` for major sections
- Use `### Subsection` for subsections
- Use code blocks with language tags: ` ```python `, ` ```bash `, ` ```json `
- Use **bold** for important terms
- Use inline `code` for commands, file names, and code snippets
- Include tables for configuration parameters
- Use bullet lists for features and steps
- Add emoji sparingly for visual interest (✅ ❌ 🚀 etc.)

**Example Structure:**
```markdown
# 📊 Tool Name - User Guide

**Version:** 1.0.0  
**Last Updated:** January 2, 2026

---

## What is Tool Name?

Brief description of what the tool does and why it's useful.

### Key Features:
- 🚀 Feature 1
- 💡 Feature 2
- ⚡ Feature 3

---

## Getting Started

### Installation
Steps to set up the tool...

### First Run
How to launch and use for the first time...

---

## Interface Guide

### Main Window
Description of UI elements...

### Buttons and Controls
- **Button Name** - What it does

---

## Configuration

### config.json Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param1` | int | 100 | Description |

---

## Troubleshooting

### Common Issues

**Problem:** Description
- **Solution:** How to fix

---
```

### STEP 7b: Add Help Viewer to Tool (Optional but Recommended)

If you want your tool to have a built-in help viewer like AIStudio:

**1. Add Help Button to UI** (in Qt Designer):
- Add QPushButton named `btn_help`
- Text: "📖 Help"
- Place near other action buttons

**2. Update main_gui.py imports:**
```python
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QDialog, QVBoxLayout, QDialogButtonBox, QTextEdit)
```

**3. Add findChild for help button:**
```python
self.btn_help = central.findChild(QPushButton, "btn_help")
```

**4. Connect button signal:**
```python
if self.btn_help:
    self.btn_help.clicked.connect(self.on_help_clicked)
```

**5. Add handler method:**
```python
def on_help_clicked(self):
    """Open help documentation viewer."""
    help_dialog = HelpViewer(self)
    help_dialog.exec()
```

**6. Add HelpViewer class (before main() function):**
```python
class HelpViewer(QDialog):
    """Dialog to display help documentation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("{Tool Name} Help")
        self.resize(950, 750)
        
        layout = QVBoxLayout()
        
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        
        # Load help content
        help_path = Path(__file__).parent / "docs" / "README.md"
        if help_path.exists():
            with open(help_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            html_content = self.render_markdown(markdown_content)
            self.text_view.setHtml(html_content)
        else:
            self.text_view.setPlainText(
                "Help documentation not found.\n\n"
                f"Expected location: {help_path}"
            )
        
        layout.addWidget(self.text_view)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def render_markdown(self, markdown_text):
        """Convert markdown to HTML with Obsidian-style dark theme."""
        try:
            import markdown
            
            html_body = markdown.markdown(
                markdown_text,
                extensions=['fenced_code', 'tables', 'nl2br', 'codehilite']
            )
            
            # Use consistent dark theme styling
            return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 12pt;
            line-height: 1.7;
            color: #d4d4d4;
            background-color: #1e1e1e;
            padding: 25px 35px;
        }}
        h1 {{ color: #4ec9b0; font-size: 28pt; margin-top: 30px; padding-bottom: 10px; border-bottom: 2px solid #3a3a3a; }}
        h2 {{ color: #569cd6; font-size: 22pt; margin-top: 28px; }}
        h3 {{ color: #9cdcfe; font-size: 17pt; margin-top: 22px; }}
        code {{ background-color: #2d2d2d; color: #ce9178; padding: 3px 6px; border-radius: 4px; font-family: Consolas, monospace; }}
        pre {{ background-color: #252526; padding: 16px; border-radius: 6px; border: 1px solid #3e3e3e; overflow-x: auto; }}
        pre code {{ background-color: transparent; padding: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background-color: #2d2d2d; color: #4ec9b0; padding: 10px; border: 1px solid #3e3e3e; }}
        td {{ padding: 10px; border: 1px solid #3e3e3e; }}
        strong {{ color: #dcdcaa; }}
        hr {{ border: none; border-top: 2px solid #3a3a3a; margin: 30px 0; }}
    </style>
</head>
<body>{html_body}</body>
</html>'''
        except ImportError:
            return f'<html><body style="padding: 20px;"><pre>{markdown_text}</pre></body></html>'
```

**7. Add markdown to requirements.txt:**
```
markdown>=3.5.0
```

**8. Install in tool's venv:**
```bash
.venv\Scripts\pip install markdown
```

---

### STEP 8: Create Model Output Folder
**Path:** `G:/AIStudio/models/{tool_name}/`

Create these subfolders:
- `checkpoints/` - Training checkpoints
- `exports/` - Final trained models
- `metadata.json` - Model info (created by engine)

---

### STEP 9: Git Integration
**Commands:**
```bash
cd G:/AIStudio
git add tools/{tool_name}/*.py tools/{tool_name}/*.ui tools/{tool_name}/*.json tools/{tool_name}/*.txt
git commit -m "Add new tool: {Tool Display Name}"
git push
```

**What NOT to commit:**
- `.venv/` folders
- `logs/` contents
- `__pycache__/`
- Model weights (`.pt`, `.pth`, `.ckpt`)

---

### STEP 10: Register with Master Launcher
**Edit:** `G:/AIStudio/studio_config.json`

Add tool entry:
```json
{
  "id": "tool_name",
  "display_name": "Tool Display Name",
  "description": "Short description of what it does",
  "path": "G:/AIStudio/tools/tool_name",
  "entry_point": "main_gui.py",
  "icon": "icon.png",
  "category": "Training",
  "enabled": true
}
```

---

## Critical Rules Checklist

### UI Rules:
- ✅ Built in Qt Designer (`.ui` file)
- ✅ Loaded dynamically at runtime (never convert to .py)
- ✅ Widget names follow `{type}_{description}` convention
- ✅ No hardcoded paths (use config.json)

### Engine Rules:
- ✅ Completely headless (no PyQt imports)
- ✅ CLI-runnable with `--config` argument
- ✅ Twin-stream logging (console + file)
- ✅ Writes progress to `logs/{tool}_status.json`
- ✅ Handles SIGTERM gracefully
- ✅ Has `--test` mode for validation

### Data Rules:
- ✅ Reads from `G:/AIStudio/data/raw/` or `data/processed/`
- ✅ Writes models to `G:/AIStudio/models/{tool_name}/`
- ✅ Creates `{dataset}_metadata.json` for processed data
- ✅ Follows naming: `{tool}_{timestamp}_{description}.ext`

### Configuration Rules:
- ✅ All settings in `config.json`
- ✅ Absolute paths with G:/AIStudio/ prefix
- ✅ Hyperparameters easily editable by user

### Git Rules:
- ✅ Commit source code only (`.py`, `.ui`, `.json`, `.txt`)
- ✅ Never commit `.venv/`, `logs/`, `data/`, `models/`
- ✅ Small commits per feature

---

## Testing Before Integration

### Manual Tests:
1. ✅ **Engine Test:** Run `python engine.py --config config.json --test`
2. ✅ **GUI Test:** Run `python main_gui.py` and verify UI loads
3. ✅ **Subprocess Test:** Click "Start" button, verify engine launches
4. ✅ **Progress Test:** Verify status.json updates and UI reflects progress
5. ✅ **Log Test:** Check logs folder for rotating log files
6. ✅ **Crash Test:** Force stop engine, verify graceful shutdown

### Unit Tests (Optional):
Create `tests/test_engine.py`:
```python
import pytest
from engine import ToolEngine

def test_config_loading():
    engine = ToolEngine("config.json")
    assert engine.config is not None

def test_validation_mode():
    # Test --test flag behavior
    pass
```

---

## Common Pitfalls to Avoid

❌ **Don't:** Convert .ui to .py files  
✅ **Do:** Load .ui at runtime with `loadUi()`

❌ **Don't:** Load QMainWindow UI with `loader.load(ui_file, self)`  
✅ **Do:** Use `loader.load(ui_file, None)`, then transfer ALL components

❌ **Don't:** Only transfer central widget (loses menu/status bars)  
✅ **Do:** Transfer menuBar(), statusBar(), toolbars, AND centralWidget()

❌ **Don't:** Forget to import widget classes (QPushButton, QTextEdit, etc.)  
✅ **Do:** Import all widget types you'll use with `findChild()`

❌ **Don't:** Store display text in list widgets for identification  
✅ **Do:** Store unique IDs in `QListWidgetItem.setData(Qt.UserRole, id)`

❌ **Don't:** Import PyQt in engine.py  
✅ **Do:** Keep engine completely headless

❌ **Don't:** Run engine logic in GUI process  
✅ **Do:** Launch engine as subprocess

❌ **Don't:** Use hardcoded paths  
✅ **Do:** Read all paths from config.json

❌ **Don't:** Commit .venv or data folders  
✅ **Do:** Check .gitignore before commits

❌ **Don't:** Mix hyperparameters in code  
✅ **Do:** Store all settings in config.json

---

## 🚨 GUI Loading Troubleshooting

### Problem: GUI window appears but no widgets are visible (blank window)

**Root Cause:** Incorrect loading of QMainWindow UI files

**Solution:**
```python
# ❌ WRONG - This will show blank window:
ui_widget = loader.load(ui_file, self)
self.setCentralWidget(ui_widget)

# ❌ ALSO WRONG - Loses menu bar, status bar, toolbars:
loaded_window = loader.load(ui_file, None)
central = loaded_window.centralWidget()
self.setCentralWidget(central)
# loaded_window gets garbage collected with all its components!

# ✅ CORRECT - Transfer ALL QMainWindow components:
loaded_window = loader.load(ui_file, None)  # Load with None parent

# Transfer menu bar, status bar, toolbars FIRST
if loaded_window.menuBar():
    self.setMenuBar(loaded_window.menuBar())
if loaded_window.statusBar():
    self.setStatusBar(loaded_window.statusBar())
for toolbar in loaded_window.findChildren(QToolBar):
    self.addToolBar(toolbar)

# Then transfer central widget
central = loaded_window.centralWidget()
self.setCentralWidget(central)

# ✅ CORRECT - Find widgets from central widget:
self.btn_start = central.findChild(QPushButton, "btn_start")
```

**Why this happens:**
- Qt Designer saves QMainWindow layouts with components in specific slots
- A QMainWindow has: menuBar, statusBar, toolBars, centralWidget, dockWidgets
- The `loader.load()` returns the complete QMainWindow
- You MUST explicitly transfer each component to self before garbage collection
- Only transferring centralWidget() discards everything else

**Quick Checklist:**
If your GUI appears but is missing components:
1. ✅ Verify you're loading with `None` parent
2. ✅ Verify you're transferring menuBar() if it exists
3. ✅ Verify you're transferring statusBar() if it exists
4. ✅ Verify you're transferring toolbars with findChildren(QToolBar)
5. ✅ Verify you're transferring centralWidget() LAST
6. ✅ Verify you're calling `findChild()` on `central`, not `loaded_window`
7. ✅ Verify you imported all widget classes (QPushButton, QTextEdit, QToolBar, etc.)

---

### Problem: List widget items identified by display text causing duplicates

**Root Cause:** Using `item.text()` to identify items is fragile and fails with duplicates

**Solution:** Store unique IDs in item data using Qt.UserRole
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

# ❌ WRONG - Fragile, breaks with duplicate names:
for file in files:
    self.lst_files.addItem(file.name)
    
# Later when clicking:
selected_name = self.lst_files.selectedItems()[0].text()
# How do you find the RIGHT file if two have same name?

# ✅ CORRECT - Store unique identifier in item data:
for file in files:
    item = QListWidgetItem(file.name)  # Display text
    item.setData(Qt.ItemDataRole.UserRole, str(file.path))  # Unique ID
    self.lst_files.addItem(item)

# Later when clicking:
selected_item = self.lst_files.selectedItems()[0]
file_path = selected_item.data(Qt.ItemDataRole.UserRole)
# Now you have the EXACT file path!
```

**Benefits:**
- No name collision issues
- Faster lookups (no searching)
- Can store any data type (paths, IDs, objects)
- Industry standard Qt pattern

---

## Naming Standards Reference

| Asset        | Format             | Example                    |
| ------------ | ------------------ | -------------------------- |
| Tool Folder  | snake_case         | `yolo_sign_trainer`        |
| Python Files | snake_case         | `main_gui.py`, `engine.py` |
| UI Files     | snake_case         | `interface.ui`             |
| Classes      | PascalCase         | `class YoloEngine:`        |
| Functions    | snake_case         | `def train_model():`       |
| Variables    | snake_case         | `dataset_path`             |
| Constants    | UPPER_CASE         | `MAX_EPOCHS`               |
| Log Files    | Tool_Date.log      | `YoloTrain_20260101.log`   |
| Status File  | {tool}_status.json | `yolo_trainer_status.json` |

---

## Ready to Start?

After reading this document, ask the user:

**"What tool would you like to build? Please describe:**
- **Tool name:** (what should it be called?)
- **Purpose:** (what AI task does it perform?)
- **Key features:** (training, inference, data processing, etc.)
- **Input data:** (what kind of data does it work with?)
- **Output:** (what does it produce?)"**

Then follow the 10-step workflow above to create the tool systematically.

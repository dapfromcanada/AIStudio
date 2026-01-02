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
from PySide6.QtWidgets import QApplication, QMainWindow
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
        ui_widget = loader.load(ui_file, self)
        ui_file.close()
        
        # Transfer widgets from loaded UI to self
        for attr_name in dir(ui_widget):
            if not attr_name.startswith('_'):
                setattr(self, attr_name, getattr(ui_widget, attr_name))
        
        self.setCentralWidget(ui_widget)
        
        self.engine_process = None
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_progress)
        
        self.connect_signals()
    
    def connect_signals(self):
        # Connect buttons to methods
        self.btn_start.clicked.connect(self.start_engine)
        self.btn_stop.clicked.connect(self.stop_engine)
    
    def start_engine(self):
        # Launch engine.py as subprocess
        config_path = Path(__file__).parent / "config.json"
        self.engine_process = subprocess.Popen(
            [".venv/Scripts/python", "engine.py", "--config", str(config_path)],
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

**Required Sections:**
1. **Tool Purpose:** What does this tool do?
2. **Features:** Bullet list of capabilities
3. **Usage:** How to run via GUI and via CLI (engine.py)
4. **Configuration:** Explain config.json parameters
5. **Data Requirements:** Input/output formats
6. **Dependencies:** Special setup (GPU drivers, datasets)
7. **Troubleshooting:** Common errors and fixes

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

# 📖 AIStudio User Guide

**Version:** 1.0.0  
**Last Updated:** January 2, 2026

---

## What is AIStudio?

**AIStudio** is the master launcher and process manager for AI development tools. It is NOT an AI tool itself—it's a lightweight GUI that launches, monitors, and manages independent AI tools as separate processes.

### Key Features:
- 🚀 **One-Click Tool Launching** - Start any registered AI tool with a single click
- 🔄 **Process Management** - Automatically suspends when tools run, resumes when they close
- 📋 **Tool Registry** - Central catalog of all available AI tools
- 🔍 **Tool Information** - View details, descriptions, and configurations
- 🛡️ **Resource Efficiency** - Hides itself to free system resources while tools run

---

## Getting Started

### First Launch

1. **Open Terminal** in the AI Studio folder:
   ```powershell
   cd G:\AIStudio
   ```

2. **Launch AIStudio**:
   ```powershell
   .venv\Scripts\python.exe ai_studio.py
   ```

3. **The Main Window** will appear showing:
   - Title: "🛠️ AI Studio - Tool Manager"
   - Available tools list (left side)
   - Action buttons (right side)
   - Tool information panel (bottom)

---

## Main Interface Guide

### Available Tools List (Left Panel)

- Displays all registered tools from `studio_config.json`
- Click any tool to select it
- Selected tool shows details in the information panel below
- Alternating row colors for easy reading

### Action Buttons (Right Panel)

#### ▶️ Launch Tool
- **Purpose:** Start the selected tool as an independent process
- **Behavior:** 
  - AIStudio window hides automatically
  - Selected tool opens in its own window
  - When tool closes, AIStudio reappears
- **Requirements:** 
  - Must select a tool first
  - Tool must have valid virtual environment (`.venv` folder)

#### 🔄 Refresh List
- **Purpose:** Reload tool list from `studio_config.json`
- **When to use:**
  - After manually editing config file
  - After installing a new tool
  - If tools don't appear correctly

#### ➕ Add Tool
- **Status:** Coming soon
- **Current workaround:** Manually edit `studio_config.json` (see Tool Registration section)

#### ⚙️ Settings
- **Status:** Coming soon
- **Planned features:** Theme selection, default paths, logging preferences

### Tool Information Panel (Bottom)

Displays details about the currently selected tool:
- **Display Name** - User-friendly tool name
- **Description** - What the tool does
- **Category** - Tool type (Training, Inference, Data Processing, etc.)
- **Path** - Folder location on disk

---

## Using Tools

### Launching a Tool

1. **Select the tool** from the Available Tools list
2. **Click "▶️ Launch Tool"**
3. **AIStudio hides** - This is normal! It frees resources for your tool
4. **Tool window appears** - Work in the tool as needed
5. **Close the tool** when finished
6. **AIStudio reappears** automatically

### What If Launch Fails?

**Error: "Environment Missing"**
- **Problem:** Tool's virtual environment doesn't exist
- **Solution:**
  ```powershell
  cd G:\AIStudio\tools\{tool_name}
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  ```

**Error: "Tool Not Found"**
- **Problem:** Tool registration is incorrect in config
- **Solution:** Verify `studio_config.json` has correct `path` and `entry_point`

**Tool Starts But Crashes Immediately**
- **Problem:** Missing dependencies or Python errors
- **Solution:** Run tool standalone to see error:
  ```powershell
  cd G:\AIStudio\tools\{tool_name}
  .venv\Scripts\python.exe main_gui.py
  ```

---

## Tool Registration

### Manual Registration (Current Method)

1. **Open** `G:\AIStudio\studio_config.json`

2. **Add tool entry** to the `"tools"` array:
   ```json
   {
     "id": "my_tool",
     "display_name": "My Tool Name",
     "description": "What this tool does",
     "path": "G:/AIStudio/tools/my_tool",
     "entry_point": "main_gui.py",
     "icon": "",
     "category": "Training",
     "enabled": true
   }
   ```

3. **Field Definitions:**
   - `id` - Unique identifier (snake_case, no spaces)
   - `display_name` - Name shown in launcher
   - `description` - Brief explanation (1-2 sentences)
   - `path` - Absolute path to tool folder
   - `entry_point` - Python file to run (usually `main_gui.py`)
   - `icon` - Optional icon file name (future feature)
   - `category` - Tool type for filtering
   - `enabled` - Set to `false` to hide tool without deleting

4. **Save and click "🔄 Refresh List"** in AIStudio

### Disabling a Tool

Change `"enabled": true` to `"enabled": false` in the tool's config entry.

### Removing a Tool

Delete the entire tool object from the `"tools"` array in `studio_config.json`.

---

## Advanced Usage

### Running Multiple Tools

- You can only launch **one tool at a time** from AIStudio
- The launcher tracks the active process
- Close the current tool before launching another
- To run multiple tools simultaneously, launch them manually from their folders

### Closing AIStudio With Tools Running

If you try to close AIStudio while a tool is running:
- **Warning dialog appears:** "Tools are still running. Close anyway?"
- **Yes:** Launcher closes (tool continues running in background)
- **No:** Launcher stays open

### Standalone Tool Launch (Bypassing Launcher)

You can run any tool directly without the launcher:
```powershell
cd G:\AIStudio\tools\{tool_name}
.venv\Scripts\python.exe main_gui.py
```

This is useful for:
- Development/testing
- When launcher has issues
- Running multiple tools simultaneously

---

## Configuration Files

### studio_config.json

**Location:** `G:\AIStudio\studio_config.json`

**Structure:**
```json
{
  "launcher_version": "1.0.0",
  "launcher_name": "AIStudio",
  "tools": [
    {
      "id": "tool_id",
      "display_name": "Tool Name",
      "description": "Description",
      "path": "G:/AIStudio/tools/tool_folder",
      "entry_point": "main_gui.py",
      "icon": "",
      "category": "Category",
      "enabled": true
    }
  ]
}
```

**Editing Tips:**
- Use forward slashes `/` in paths (even on Windows)
- Ensure valid JSON syntax (no trailing commas)
- Use double quotes `"` for strings
- Validate JSON before saving (use online JSON validator)

---

## Troubleshooting

### GUI Doesn't Appear

**Check Python Version:**
```powershell
.venv\Scripts\python.exe --version
```
Should be Python 3.8+

**Check PySide6 Installation:**
```powershell
.venv\Scripts\pip list | Select-String PySide6
```
If missing: `.venv\Scripts\pip install PySide6`

**Check for Errors:**
Run in foreground to see error messages:
```powershell
.venv\Scripts\python.exe aicopilot_dp.py
```

### GUI Appears But Is Blank

This should be fixed in v1.0.0. If you still see this:
1. Verify you're using the latest code
2. Check that `ai_studio.ui` exists in the folder
3. Reinstall PySide6: `pip install --upgrade --force-reinstall PySide6`

### Tool Doesn't Launch

1. **Select the tool first** - Click it in the list
2. **Check virtual environment exists:**
   ```powershell
   Test-Path G:\AIStudio\tools\{tool_name}\.venv\Scripts\python.exe
   ```
3. **Check entry point exists:**
   ```powershell
   Test-Path G:\AIStudio\tools\{tool_name}\main_gui.py
   ```
4. **Check tool registration** in `studio_config.json`

### Launcher Doesn't Resume After Closing Tool

- Check if tool process is still running in Task Manager
- If so, end the process manually
- Restart AIStudio

---

## File Structure

```
G:\AIStudio\
├── aicopilot_dp.py          # Main launcher script
├── aicopilot_dp.ui          # Qt Designer UI layout
├── studio_config.json       # Tool registry
├── requirements.txt         # Launcher dependencies (PySide6)
├── .venv\                   # Launcher virtual environment
├── docs\                    # Documentation (you are here!)
│   └── README.md
├── tools\                   # All AI tools
│   ├── tools_template\      # Template for creating new tools
│   └── {tool_name}\         # Individual tool folders
├── data\                    # Shared data storage
│   ├── raw\                 # Raw input data
│   └── processed\           # Processed datasets
├── models\                  # Trained model storage
│   └── {tool_name}\         # Models organized by tool
└── shared\                  # Shared utilities (future)
```

---

## Best Practices

### Do:
- ✅ Keep studio_config.json backed up
- ✅ Test tools standalone before registering
- ✅ Use descriptive tool names and descriptions
- ✅ Keep tools isolated in their own folders
- ✅ Close tools properly (don't force kill)

### Don't:
- ❌ Edit config files while AiCopilotDP is running
- ❌ Move tool folders after registration (breaks paths)
- ❌ Delete .venv folders (tools won't launch)
- ❌ Run multiple instances of AiCopilotDP
- ❌ Force close tools (use their close buttons)

---

## Keyboard Shortcuts

Currently none implemented. Coming in future versions.

---

## Next Steps

### Create Your First Tool

1. Read the template: `G:\AIStudio\tools\tools_template\TEMPLATE_INSTRUCTIONS.md`
2. Decide what AI task your tool will perform
3. Follow the 10-step creation workflow
4. Register it in `studio_config.json`
5. Launch it from AiCopilotDP!

### Explore Example Tools

- **FakeTool** - Example image viewer (`G:\AIStudio\tools\FakeTool\`)
  - Shows proper GUI structure
  - Demonstrates engine separation
  - Good reference for your own tools

---

## Getting Help

### Documentation
- **This file:** General launcher usage
- **Blueprint:** `G:\AIStudioSetup\AI Studio Master Blueprint.md`
- **Tool Template:** `G:\AIStudio\tools\tools_template\TEMPLATE_INSTRUCTIONS.md`
- **Tool README:** `G:\AIStudio\tools\{tool_name}\docs\README.md`

### Common Issues
- Check terminal for error messages
- Verify virtual environments exist
- Validate JSON configuration syntax
- Try running tools standalone first

---

## Version History

### v1.0.0 (January 2, 2026)
- ✅ Initial release
- ✅ Tool launching and process management
- ✅ Suspend/resume functionality
- ✅ Tool registry and information display
- ✅ Fixed GUI loading issues (findChild pattern)
- ⏳ Add Tool wizard (coming soon)
- ⏳ Settings panel (coming soon)
- ⏳ Wiki viewer (coming soon)

---

**Happy Tool Building! 🚀**

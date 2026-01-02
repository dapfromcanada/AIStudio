# 🧪 Tool Tester - User Guide

**Version:** 1.0.0  
**Last Updated:** January 2, 2026

---

## What is Tool Tester?

**Tool Tester** is an automated quality assurance tool for AIStudio. It tests all registered tools to ensure they work correctly before deployment, catching issues early in the development cycle.

### Key Features:
- 🔍 **Automated Testing** - Test all tools with one click
- ✅ **Pass/Fail Detection** - Clear status indicators
- 📊 **Test Reports** - Detailed results with logs
- 🎯 **Selective Testing** - Test specific tools or all at once
- ⚡ **Fast Execution** - Parallel testing support
- 📝 **Detailed Logging** - Track every test step
- 💾 **Export Results** - Save reports for documentation

---

## What Gets Tested?

### For Each Tool:
1. **Directory Structure** - Tool folder exists
2. **Engine.py** - Headless CLI engine present
3. **Config.json** - Configuration file valid
4. **Virtual Environment** - .venv exists and configured
5. **Test Mode** - `python engine.py --config config.json --test` runs successfully
6. **Exit Code** - Returns 0 for success

### Test Status Indicators:
- **✅ Pass** - Tool works correctly
- **❌ Fail** - Tool has errors
- **⊘ Skip** - Tool doesn't have engine.py (GUI-only)

---

## Getting Started

### First Launch

1. **From AIStudio Launcher:**
   - Open AIStudio
   - Select "Tool Tester"
   - Click "Launch Tool"

2. **Direct Launch:**
   ```powershell
   cd G:\AIStudio\tools\tool_tester
   .venv\Scripts\python main_gui.py
   ```

3. **Tool list loads automatically** from `studio_config.json`

---

## Main Interface Guide

### Registered Tools Panel

- **Tool List** - Shows all enabled tools from studio_config.json
- **Multi-Selection** - Click multiple tools while holding Ctrl
- **🔄 Refresh Button** - Reload tool list from config

### Test Actions

**▶️ Test Selected**
- Tests only the tools you selected
- Great for testing after changes

**▶️ Test All Tools**
- Tests every registered tool
- Full regression testing
- Confirmation dialog shown

**⏹️ Stop**
- Stops currently running tests
- Enabled only during testing

### Test Progress

- **Progress Bar** - Visual completion percentage
- **Status Label** - Current test activity
- **Real-time Updates** - Updates every 500ms

### Test Results

**Summary Counters:**
- **✅ Passed** - Green, number of successful tests
- **❌ Failed** - Red, number of failed tests
- **⊘ Skipped** - Gray, number of skipped tests

**Activity Log:**
- Timestamped test output
- Engine stdout/stderr
- Test progress messages
- Auto-scrolls to latest

**Action Buttons:**
- **🧹 Clear Log** - Clears activity log
- **💾 Export Results** - Save results as JSON
- **📖 Help** - Opens this documentation

---

## Using the Tool

### Basic Workflow

1. **Launch Tool Tester** from AIStudio
2. **Review tool list** (auto-populated)
3. **Select testing mode:**
   - Click tools + "Test Selected"
   - Or click "Test All Tools"
4. **Monitor progress** in real-time
5. **Review results** in log and counters
6. **Export if needed** for documentation

### Testing Single Tool

1. **Click one tool** in the list
2. **Click "▶️ Test Selected"**
3. **Watch real-time output** in log
4. **See pass/fail** in summary

### Testing Multiple Tools

1. **Hold Ctrl** and click multiple tools
2. **Click "▶️ Test Selected"**
3. **Tests run sequentially**
4. **All results** shown in log

### Testing All Tools

1. **Click "▶️ Test All Tools"**
2. **Confirm in dialog**
3. **Full test suite runs**
4. **Completion summary** shown

---

## CLI Mode (Headless Operation)

For automation and CI/CD:

### Test Mode (Validate Engine)
```bash
cd tools\tool_tester
.venv\Scripts\python engine.py --config config.json --test
```

### Test All Tools
```bash
.venv\Scripts\python engine.py --config config.json
```

### Test Specific Tool
```bash
.venv\Scripts\python engine.py --config config.json --tool md_converter
```

### Exit Codes
- `0` - All tests passed
- `1` - One or more tests failed

---

## Understanding Results

### Test Results JSON

Located in `logs/test_results_YYYYMMDD_HHMMSS.json`:

```json
[
  {
    "tool_id": "md_converter",
    "tool_name": "Markdown Converter",
    "status": "pass",
    "message": "Test passed successfully",
    "details": {
      "exit_code": 0,
      "stdout": "...",
      "stderr": ""
    }
  }
]
```

### Status Values

- **`pass`** - Tool test succeeded, exit code 0
- **`fail`** - Tool test failed, non-zero exit code or exception
- **`skip`** - Tool has no engine.py (GUI-only tool)
- **`unknown`** - Unexpected state

---

## Troubleshooting

### Common Issues

**Problem: "No tools found"**
- **Cause:** studio_config.json empty or missing
- **Solution:** Register tools in studio_config.json

**Problem: "Tool directory not found"**
- **Cause:** Path in studio_config.json incorrect
- **Solution:** Verify tool path matches folder location

**Problem: "Virtual environment not found"**
- **Cause:** Tool's .venv not created
- **Solution:** Run `python -m venv .venv` in tool folder

**Problem: "Test timed out"**
- **Cause:** Tool's test mode takes >30 seconds
- **Solution:** Optimize tool's --test implementation

**Problem: Test fails but tool works**
- **Cause:** Tool's engine.py doesn't implement --test flag
- **Solution:** Add --test mode to engine.py (see template)

### Log Files

Check these for diagnostic information:

- **Activity Log** (in GUI): Real-time test output
- **Log Files**: `logs/tool_tester_YYYYMMDD_HHMMSS.log`
- **Status File**: `logs/tool_tester_status.json`
- **Results**: `logs/test_results_YYYYMMDD_HHMMSS.json`

### Getting Help

- Click **📖 Help** in Tool Tester for this documentation
- Check tool-specific logs in `{tool}/logs/` folder
- Review [AI Studio Master Blueprint](G:/AIStudioSetup/AI%20Studio%20Master%20Blueprint.md)
- Check tool's README.md in docs/ folder

---

## Best Practices

### When to Test

✅ **Test after:**
- Creating a new tool
- Modifying engine.py
- Changing config.json
- Updating dependencies
- Before git commits
- Before AWS deployment

✅ **Regular testing:**
- Daily regression test (Test All)
- Pre-deployment validation
- After pulling changes

### Development Workflow

1. **Create/modify tool**
2. **Run tool-specific test** (Test Selected)
3. **Fix any failures**
4. **Run full suite** (Test All)
5. **Commit if all pass**

### CI/CD Integration

```bash
# In your build script
cd G:\AIStudio\tools\tool_tester
.venv\Scripts\python engine.py --config config.json

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Tests failed"
    exit 1
fi
```

---

## Tool Requirements

### For Tools to be Testable

Your tool must have:

1. **engine.py** with CLI support
2. **--test flag** implemented
3. **config.json** in tool folder
4. **.venv/** virtual environment
5. **Exit code 0** on success

### Template Implementation

```python
# In your tool's engine.py
if args.test:
    logger.info("Running in TEST mode")
    logger.info("Tool engine is operational")
    # Do quick validation
    return 0  # Success
```

---

## Configuration

### config.json

Located in `tool_tester/config.json`:

```json
{
  "tool_name": "tool_tester",
  "version": "1.0.0",
  "paths": {
    "logs": "logs/",
    "results": "logs/test_results_{timestamp}.json"
  },
  "options": {
    "test_timeout": 30,
    "auto_refresh": true,
    "enable_logging": true
  }
}
```

### settings.ini

Auto-generated, stores user preferences:

```ini
[Settings]
# Future: Window size, theme, etc.
```

---

## Integration with AIStudio

### Tool Registration

Tool Tester is registered in `studio_config.json`:

```json
{
  "id": "tool_tester",
  "display_name": "Tool Tester",
  "description": "Automated testing system for AIStudio tools",
  "path": "G:/AIStudio/tools/tool_tester",
  "entry_point": "main_gui.py",
  "category": "Development",
  "enabled": true
}
```

### Data Flow

```
Tool Tester → studio_config.json → Load Tools
           ↓
    For each tool → engine.py --test
           ↓
    Collect results → test_results.json
           ↓
    Display in GUI → Pass/Fail summary
```

---

## Advanced Usage

### Testing Specific Tool Classes

If you want to test only certain types of tools:

1. Select multiple tools manually (Ctrl+Click)
2. Click "Test Selected"

### Batch Testing Script

```powershell
# test_all_daily.ps1
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$log = "test_report_$timestamp.txt"

cd G:\AIStudio\tools\tool_tester
.\.venv\Scripts\python.exe engine.py --config config.json | Tee-Object $log

Write-Host "Report saved to: $log"
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running AIStudio tool tests..."
cd tools/tool_tester
.venv/Scripts/python engine.py --config config.json

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "All tests passed!"
```

---

## File Structure

```
tool_tester/
├── main_gui.py              # GUI controller
├── interface.ui             # Qt Designer layout
├── engine.py                # Headless test engine
├── config.json              # Tool configuration
├── requirements.txt         # Python dependencies
├── settings.ini             # User preferences (auto-created)
├── .venv/                   # Virtual environment
├── logs/                    # Test logs and results
│   ├── tool_tester_*.log
│   ├── tool_tester_status.json
│   └── test_results_*.json
└── docs/
    └── README.md            # This file
```

---

## Version History

### v1.0.0 (January 2, 2026)
- ✅ Initial release
- ✅ Automated testing for all AIStudio tools
- ✅ GUI and CLI modes
- ✅ Pass/Fail/Skip detection
- ✅ Real-time progress tracking
- ✅ Test result export
- ✅ Help documentation
- ✅ Integration with AIStudio launcher

---

## Technologies Used

- **PySide6** - Qt framework for GUI
- **Python subprocess** - Running tool engines
- **JSON** - Configuration and results
- **Markdown** - Documentation rendering

---

## Future Enhancements

- [ ] Parallel testing (run multiple tools simultaneously)
- [ ] Test history tracking
- [ ] Performance benchmarking
- [ ] Email notifications on failure
- [ ] Integration with GitHub Actions
- [ ] Test coverage metrics
- [ ] Custom test scripts per tool

---

**Happy Testing! 🧪**

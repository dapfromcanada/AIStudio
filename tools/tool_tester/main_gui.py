"""
Tool Tester GUI - AIStudio Quality Assurance Interface
Test all registered AIStudio tools automatically
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from configparser import ConfigParser

from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, 
                               QPushButton, QListWidget, QPlainTextEdit,
                               QProgressBar, QLabel, QDialog, QVBoxLayout,
                               QDialogButtonBox, QFileDialog)
from PySide6.QtCore import QProcess, QFile, QTimer, Qt
from PySide6.QtUiTools import QUiLoader


class ToolTesterGUI(QMainWindow):
    """Main GUI for AIStudio Tool Tester"""
    
    def __init__(self):
        super().__init__()
        self.base_path = Path(__file__).parent
        self.config = self.load_config()
        self.test_process = None
        self.status_timer = QTimer()
        self.test_results = []
        
        self.load_ui()
        self.load_settings()
        self.connect_signals()
        self.refresh_tool_list()
        
        # Poll status every 500ms during testing
        self.status_timer.timeout.connect(self.check_status)
    
    def load_ui(self):
        """Load UI from interface.ui"""
        ui_path = self.base_path / "interface.ui"
        ui_file = QFile(str(ui_path))
        
        if not ui_file.open(QFile.ReadOnly):
            QMessageBox.critical(self, "Error", f"Cannot open UI file: {ui_path}")
            sys.exit(1)
        
        loader = QUiLoader()
        loaded_window = loader.load(ui_file, None)
        ui_file.close()
        
        # Transfer components
        if loaded_window.menuBar():
            self.setMenuBar(loaded_window.menuBar())
        if loaded_window.statusBar():
            self.setStatusBar(loaded_window.statusBar())
        
        central = loaded_window.centralWidget()
        self.setCentralWidget(central)
        
        # Get widget references
        self.lst_tools = central.findChild(QListWidget, "lst_tools")
        self.lbl_tool_count = central.findChild(QLabel, "lbl_tool_count")
        self.btn_refresh = central.findChild(QPushButton, "btn_refresh")
        self.btn_test_selected = central.findChild(QPushButton, "btn_test_selected")
        self.btn_test_all = central.findChild(QPushButton, "btn_test_all")
        self.btn_stop = central.findChild(QPushButton, "btn_stop")
        self.progress_bar = central.findChild(QProgressBar, "progress_bar")
        self.lbl_status = central.findChild(QLabel, "lbl_status")
        self.lbl_passed = central.findChild(QLabel, "lbl_passed")
        self.lbl_failed = central.findChild(QLabel, "lbl_failed")
        self.lbl_skipped = central.findChild(QLabel, "lbl_skipped")
        self.txt_log = central.findChild(QPlainTextEdit, "txt_log")
        self.btn_clear_log = central.findChild(QPushButton, "btn_clear_log")
        self.btn_export = central.findChild(QPushButton, "btn_export")
        self.btn_help = central.findChild(QPushButton, "btn_help")
        
        self.setWindowTitle(f"Tool Tester v{self.config.get('version', '1.0.0')}")
    
    def load_config(self):
        """Load tool configuration"""
        config_path = self.base_path / "config.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"version": "1.0.0"}
    
    def load_settings(self):
        """Load user settings from settings.ini"""
        settings_path = self.base_path / "settings.ini"
        self.settings = ConfigParser()
        
        if settings_path.exists():
            self.settings.read(settings_path)
    
    def save_settings(self):
        """Save user settings to settings.ini"""
        settings_path = self.base_path / "settings.ini"
        
        with open(settings_path, 'w') as f:
            self.settings.write(f)
    
    def connect_signals(self):
        """Connect UI signals to handlers"""
        if self.btn_refresh:
            self.btn_refresh.clicked.connect(self.refresh_tool_list)
        if self.btn_test_selected:
            self.btn_test_selected.clicked.connect(self.test_selected_tools)
        if self.btn_test_all:
            self.btn_test_all.clicked.connect(self.test_all_tools)
        if self.btn_stop:
            self.btn_stop.clicked.connect(self.stop_testing)
        if self.btn_clear_log:
            self.btn_clear_log.clicked.connect(self.clear_log)
        if self.btn_export:
            self.btn_export.clicked.connect(self.export_results)
        if self.btn_help:
            self.btn_help.clicked.connect(self.show_help)
    
    def refresh_tool_list(self):
        """Load and display registered tools from studio_config.json"""
        studio_config_path = self.base_path.parent.parent / "studio_config.json"
        
        try:
            with open(studio_config_path, 'r') as f:
                config = json.load(f)
                tools = config.get('tools', [])
            
            self.lst_tools.clear()
            
            for tool in tools:
                if tool.get('enabled', True):
                    item_text = f"{tool['display_name']} ({tool['id']})"
                    self.lst_tools.addItem(item_text)
                    # Store tool ID as user data
                    item = self.lst_tools.item(self.lst_tools.count() - 1)
                    item.setData(Qt.ItemDataRole.UserRole, tool['id'])
            
            self.lbl_tool_count.setText(f"{len(tools)} tools registered")
            self.log_message(f"Loaded {len(tools)} tools from configuration")
        
        except FileNotFoundError:
            QMessageBox.warning(self, "Config Error", "studio_config.json not found!")
            self.log_message("ERROR: studio_config.json not found", error=True)
    
    def test_selected_tools(self):
        """Test only selected tools"""
        selected_items = self.lst_tools.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one tool to test.")
            return
        
        tool_ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items]
        self.start_testing(tool_ids)
    
    def test_all_tools(self):
        """Test all registered tools"""
        reply = QMessageBox.question(
            self,
            "Test All Tools",
            f"Run tests on all {self.lst_tools.count()} registered tools?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.start_testing(None)  # None means test all
    
    def start_testing(self, tool_ids=None):
        """
        Start testing process
        
        Args:
            tool_ids: List of tool IDs to test, or None for all tools
        """
        config_path = self.base_path / "config.json"
        venv_python = self.base_path / ".venv" / "Scripts" / "python.exe"
        
        # Clear previous results
        self.test_results = []
        self.reset_counters()
        
        # Build command
        cmd = [str(venv_python), "engine.py", "--config", str(config_path)]
        
        if tool_ids:
            if len(tool_ids) == 1:
                cmd.extend(["--tool", tool_ids[0]])
                self.log_message(f"Starting test for: {tool_ids[0]}")
            else:
                # For multiple specific tools, run sequentially
                self.log_message(f"Starting tests for {len(tool_ids)} selected tools")
                # TODO: Enhance engine.py to support multiple tool IDs
                QMessageBox.information(
                    self,
                    "Note",
                    "Testing multiple selected tools sequentially..."
                )
        else:
            self.log_message("Starting tests for ALL registered tools")
        
        # Create process
        self.test_process = QProcess(self)
        self.test_process.setProgram(cmd[0])
        self.test_process.setArguments(cmd[1:])
        self.test_process.setWorkingDirectory(str(self.base_path))
        
        # Connect signals
        self.test_process.readyReadStandardOutput.connect(self.read_stdout)
        self.test_process.readyReadStandardError.connect(self.read_stderr)
        self.test_process.finished.connect(self.on_testing_finished)
        
        # Start process
        self.test_process.start()
        
        # Update UI
        self.btn_test_selected.setEnabled(False)
        self.btn_test_all.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Testing in progress...")
        
        # Start status polling
        self.status_timer.start(500)
    
    def read_stdout(self):
        """Read and display stdout from engine"""
        if self.test_process:
            output = bytes(self.test_process.readAllStandardOutput()).decode('utf-8')
            for line in output.strip().split('\n'):
                if line:
                    self.log_message(line)
    
    def read_stderr(self):
        """Read and display stderr from engine"""
        if self.test_process:
            output = bytes(self.test_process.readAllStandardError()).decode('utf-8')
            for line in output.strip().split('\n'):
                if line:
                    self.log_message(line, error=True)
    
    def check_status(self):
        """Check status JSON file for progress updates"""
        status_file = self.base_path / "logs" / "tool_tester_status.json"
        
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    status = json.load(f)
                
                progress = status.get('progress', 0)
                message = status.get('message', '')
                
                self.progress_bar.setValue(progress)
                self.lbl_status.setText(message)
            
            except (json.JSONDecodeError, IOError):
                pass  # Ignore transient read errors
    
    def on_testing_finished(self, exit_code, exit_status):
        """Handle testing completion"""
        self.status_timer.stop()
        
        # Update UI
        self.btn_test_selected.setEnabled(True)
        self.btn_test_all.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setValue(100)
        
        if exit_code == 0:
            self.lbl_status.setText("✅ All tests completed successfully")
            self.log_message("\n✅ Testing completed successfully!")
        else:
            self.lbl_status.setText("❌ Testing completed with failures")
            self.log_message(f"\n❌ Testing completed with failures (exit code: {exit_code})", error=True)
        
        # Load and parse results
        self.load_test_results()
    
    def load_test_results(self):
        """Load test results from latest JSON file"""
        logs_dir = self.base_path / "logs"
        
        # Find latest results file
        result_files = sorted(logs_dir.glob("test_results_*.json"), reverse=True)
        
        if result_files:
            latest_file = result_files[0]
            try:
                with open(latest_file, 'r') as f:
                    self.test_results = json.load(f)
                
                # Update counters
                passed = sum(1 for r in self.test_results if r['status'] == 'pass')
                failed = sum(1 for r in self.test_results if r['status'] == 'fail')
                skipped = sum(1 for r in self.test_results if r['status'] == 'skip')
                
                self.lbl_passed.setText(f"✅ Passed: {passed}")
                self.lbl_failed.setText(f"❌ Failed: {failed}")
                self.lbl_skipped.setText(f"⊘ Skipped: {skipped}")
                
                # Show completion message
                if failed == 0:
                    QMessageBox.information(
                        self,
                        "Tests Passed",
                        f"All {passed} tests passed successfully! 🎉"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Tests Failed",
                        f"{failed} test(s) failed.\n{passed} passed, {skipped} skipped."
                    )
            
            except (json.JSONDecodeError, IOError) as e:
                self.log_message(f"Error loading results: {e}", error=True)
    
    def reset_counters(self):
        """Reset test result counters"""
        self.lbl_passed.setText("✅ Passed: 0")
        self.lbl_failed.setText("❌ Failed: 0")
        self.lbl_skipped.setText("⊘ Skipped: 0")
    
    def stop_testing(self):
        """Stop running tests"""
        if self.test_process and self.test_process.state() == QProcess.ProcessState.Running:
            reply = QMessageBox.question(
                self,
                "Stop Testing",
                "Stop current test run?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.test_process.kill()
                self.log_message("Testing stopped by user", error=True)
                self.lbl_status.setText("⏹️ Testing stopped")
    
    def clear_log(self):
        """Clear the log display"""
        self.txt_log.clear()
    
    def export_results(self):
        """Export test results to file"""
        if not self.test_results:
            QMessageBox.information(self, "No Results", "No test results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Test Results",
            f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.test_results, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Results exported to:\n{file_path}")
                self.log_message(f"Results exported to: {file_path}")
            
            except IOError as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{e}")
    
    def show_help(self):
        """Show help documentation"""
        help_dialog = HelpViewer(self)
        help_dialog.exec()
    
    def log_message(self, message, error=False):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if error:
            formatted = f"[{timestamp}] ❌ {message}"
        else:
            formatted = f"[{timestamp}] {message}"
        
        self.txt_log.appendPlainText(formatted)
        
        # Auto-scroll to bottom
        self.txt_log.verticalScrollBar().setValue(
            self.txt_log.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.test_process and self.test_process.state() == QProcess.ProcessState.Running:
            reply = QMessageBox.question(
                self,
                "Tests Running",
                "Tests are still running. Quit anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            self.test_process.kill()
        
        self.save_settings()
        event.accept()


class HelpViewer(QDialog):
    """Dialog to display help documentation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tool Tester Help")
        self.resize(900, 700)
        
        layout = QVBoxLayout()
        
        from PySide6.QtWidgets import QTextEdit
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
        """Convert markdown to HTML with dark theme"""
        try:
            import markdown
            
            html_body = markdown.markdown(
                markdown_text,
                extensions=['fenced_code', 'tables', 'nl2br']
            )
            
            # Obsidian-style dark theme
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
        h1 {{ color: #4ec9b0; font-size: 28pt; margin-top: 30px; }}
        h2 {{ color: #569cd6; font-size: 22pt; margin-top: 28px; }}
        h3 {{ color: #9cdcfe; font-size: 17pt; margin-top: 22px; }}
        code {{ background-color: #2d2d2d; color: #ce9178; padding: 3px 6px; border-radius: 4px; }}
        pre {{ background-color: #252526; padding: 16px; border-radius: 6px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background-color: #2d2d2d; color: #4ec9b0; padding: 10px; border: 1px solid #3e3e3e; }}
        td {{ padding: 10px; border: 1px solid #3e3e3e; }}
        strong {{ color: #dcdcaa; }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''
        except ImportError:
            return f'<html><body style="padding: 20px;"><pre>{markdown_text}</pre></body></html>'


def main():
    """Entry point for Tool Tester GUI"""
    app = QApplication(sys.argv)
    app.setApplicationName("Tool Tester")
    app.setOrganizationName("AIStudio")
    
    window = ToolTesterGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

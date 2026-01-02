"""
AiCopilotDP - AI Studio Master Controller
A lightweight launcher for managing AI development tools.

Purpose: Launch, monitor, and manage independent AI tool processes.
NOT an AI tool itself - pure process management.
"""

import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QPushButton, 
                               QListWidget, QListWidgetItem, QTextEdit, QDialog, QVBoxLayout, QDialogButtonBox)
from PySide6.QtCore import QProcess, QFile, Qt
from PySide6.QtUiTools import QUiLoader


class AiCopilotDP(QMainWindow):
    """Main controller window for AI Studio tools."""
    
    def __init__(self):
        super().__init__()
        self.base_path = Path(__file__).parent
        self.config = self.load_config()
        self.active_processes = {}  # Track running tools
        
        # Load UI (will be created in Qt Designer)
        self.load_ui()
        self.setup_window()
        self.connect_signals()
        
    def load_config(self):
        """Load studio_config.json with registered tools."""
        config_path = self.base_path / "studio_config.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(
                self, 
                "Config Error", 
                "studio_config.json not found!"
            )
            sys.exit(1)
    
    def load_ui(self):
        """Load the UI file created in Qt Designer."""
        ui_path = self.base_path / "aicopilot_dp.ui"
        if ui_path.exists():
            ui_file = QFile(str(ui_path))
            ui_file.open(QFile.ReadOnly)
            loader = QUiLoader()
            # Load returns a QMainWindow, we need its central widget
            loaded_window = loader.load(ui_file, None)
            ui_file.close()
            
            # Get the central widget from the loaded window
            central = loaded_window.centralWidget()
            self.setCentralWidget(central)
            
            # Get references to widgets using findChild from central widget
            self.btn_launch = central.findChild(QPushButton, "btn_launch")
            self.btn_refresh = central.findChild(QPushButton, "btn_refresh")
            self.btn_add_tool = central.findChild(QPushButton, "btn_add_tool")
            self.btn_help = central.findChild(QPushButton, "btn_help")
            self.btn_settings = central.findChild(QPushButton, "btn_settings")
            self.lst_tools = central.findChild(QListWidget, "lst_tools")
            self.txt_tool_info = central.findChild(QTextEdit, "txt_tool_info")
        else:
            # Placeholder until UI is created
            self.setWindowTitle("AiCopilotDP - UI Not Found")
            self.resize(800, 600)
    
    def setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle(f"AiCopilotDP v{self.config.get('launcher_version', '1.0.0')}")
        
    def connect_signals(self):
        """Connect UI widgets to handlers (after UI is created)."""
        try:
            self.btn_launch.clicked.connect(self.on_launch_clicked)
            self.btn_refresh.clicked.connect(self.refresh_tool_list)
            self.btn_add_tool.clicked.connect(self.on_add_tool_clicked)
            self.btn_help.clicked.connect(self.on_help_clicked)
            self.btn_settings.clicked.connect(self.on_settings_clicked)
            self.lst_tools.itemSelectionChanged.connect(self.on_tool_selected)
            
            # Populate tool list on startup
            self.refresh_tool_list()
        except AttributeError:
            # UI not loaded yet
            pass
    
    def launch_tool(self, tool_id):
        """
        Launch a tool as an independent subprocess.
        
        Args:
            tool_id: Tool identifier from studio_config.json
        """
        tool_info = self.get_tool_by_id(tool_id)
        if not tool_info:
            QMessageBox.warning(self, "Tool Not Found", f"Tool '{tool_id}' not registered.")
            return
        
        tool_path = Path(tool_info['path'])
        entry_point = tool_path / tool_info['entry_point']
        venv_python = tool_path / ".venv" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            QMessageBox.warning(
                self, 
                "Environment Missing", 
                f"Virtual environment not found for {tool_info['display_name']}.\n"
                f"Expected: {venv_python}"
            )
            return
        
        # Suspend (hide) the launcher to free resources
        self.hide()
        
        # Launch tool as subprocess
        process = QProcess(self)
        process.setProgram(str(venv_python))
        process.setArguments([str(entry_point)])
        process.setWorkingDirectory(str(tool_path))
        
        # Connect process signals
        process.finished.connect(lambda: self.on_tool_finished(tool_id))
        process.errorOccurred.connect(lambda: self.on_tool_error(tool_id))
        
        process.start()
        self.active_processes[tool_id] = process
    
    def on_tool_finished(self, tool_id):
        """Handle tool process completion."""
        if tool_id in self.active_processes:
            del self.active_processes[tool_id]
        
        # Resume (show) the launcher
        self.show()
        self.activateWindow()
    
    def on_tool_error(self, tool_id):
        """Handle tool process errors."""
        tool_info = self.get_tool_by_id(tool_id)
        QMessageBox.critical(
            self,
            "Tool Error",
            f"{tool_info['display_name']} encountered an error."
        )
        self.on_tool_finished(tool_id)
    
    def get_tool_by_id(self, tool_id):
        """Retrieve tool info from config by ID."""
        for tool in self.config.get('tools', []):
            if tool['id'] == tool_id:
                return tool
        return None
    
    def refresh_tool_list(self):
        """Refresh the list of available tools from config."""
        try:
            self.lst_tools.clear()
            tools = self.config.get('tools', [])
            
            if not tools:
                self.txt_tool_info.setHtml(
                    "<p><b>No tools registered</b></p>"
                    "<p>Click 'Add Tool' to register your first tool.</p>"
                )
                return
            
            for tool in tools:
                if tool.get('enabled', True):
                    item = QListWidgetItem(tool['display_name'])
                    # Store unique tool ID in item data for reliable lookups
                    item.setData(Qt.ItemDataRole.UserRole, tool['id'])
                    self.lst_tools.addItem(item)
        except AttributeError:
            pass
    
    def on_tool_selected(self):
        """Display selected tool information."""
        try:
            selected_items = self.lst_tools.selectedItems()
            if not selected_items:
                return
            
            # Get tool ID from item data (more reliable than display name)
            tool_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            tool_info = self.get_tool_by_id(tool_id)
            
            if tool_info:
                info_html = f"""
                <p><b>{tool_info['display_name']}</b></p>
                <p>{tool_info.get('description', 'No description')}</p>
                <p><small>Category: {tool_info.get('category', 'Uncategorized')}</small></p>
                <p><small>Path: {tool_info['path']}</small></p>
                """
                self.txt_tool_info.setHtml(info_html)
        except AttributeError:
            pass
    
    def on_launch_clicked(self):
        """Handle launch button click."""
        try:
            selected_items = self.lst_tools.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "No Selection", "Please select a tool to launch.")
                return
            
            # Get tool ID directly from item data (prevents duplicate name issues)
            tool_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.launch_tool(tool_id)
        except AttributeError:
            pass
    
    def on_add_tool_clicked(self):
        """Handle add tool button (placeholder)."""
        QMessageBox.information(
            self,
            "Add Tool",
            "Tool registration wizard coming soon!\n\n"
            "For now, manually edit studio_config.json"
        )
    
    def on_help_clicked(self):
        """Open help documentation viewer."""
        help_dialog = HelpViewer(self)
        help_dialog.exec()
    
    def on_settings_clicked(self):
        """Handle settings button (placeholder)."""
        QMessageBox.information(
            self,
            "Settings",
            "Settings panel coming soon!"
        )
    
    def closeEvent(self, event):
        """Handle launcher close - ensure no tools are running."""
        if self.active_processes:
            reply = QMessageBox.question(
                self,
                "Tools Running",
                "Tools are still running. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        event.accept()


class HelpViewer(QDialog):
    """Dialog to display help documentation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AiCopilotDP Help")
        self.resize(950, 750)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create text viewer
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        
        # Load help content
        help_path = Path(__file__).parent / "docs" / "README.md"
        if help_path.exists():
            with open(help_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            # Convert markdown to HTML
            html_content = self.render_markdown(markdown_content)
            self.text_view.setHtml(html_content)
        else:
            self.text_view.setPlainText(
                "Help documentation not found.\n\n"
                f"Expected location: {help_path}"
            )
        
        layout.addWidget(self.text_view)
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def render_markdown(self, markdown_text):
        """Convert markdown to beautiful HTML using markdown library."""
        try:
            import markdown
            
            # Convert markdown to HTML with extensions
            html_body = markdown.markdown(
                markdown_text,
                extensions=['fenced_code', 'tables', 'nl2br', 'codehilite']
            )
            
            # Wrap with beautiful styling similar to Obsidian
            return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.7;
            color: #d4d4d4;
            background-color: #1e1e1e;
            padding: 25px 35px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #4ec9b0;
            font-size: 28pt;
            font-weight: 600;
            margin-top: 30px;
            margin-bottom: 18px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3a3a3a;
        }}
        
        h2 {{
            color: #569cd6;
            font-size: 22pt;
            font-weight: 600;
            margin-top: 28px;
            margin-bottom: 15px;
        }}
        
        h3 {{
            color: #9cdcfe;
            font-size: 17pt;
            font-weight: 600;
            margin-top: 22px;
            margin-bottom: 12px;
        }}
        
        h4 {{
            color: #c586c0;
            font-size: 14pt;
            font-weight: 600;
            margin-top: 18px;
            margin-bottom: 10px;
        }}
        
        p {{
            margin: 10px 0;
            text-align: left;
        }}
        
        code {{
            background-color: #2d2d2d;
            color: #ce9178;
            padding: 3px 6px;
            border-radius: 4px;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 11pt;
            border: 1px solid #3e3e3e;
        }}
        
        pre {{
            background-color: #252526;
            color: #d4d4d4;
            padding: 16px;
            border-radius: 6px;
            border: 1px solid #3e3e3e;
            overflow-x: auto;
            margin: 15px 0;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 10.5pt;
            line-height: 1.5;
        }}
        
        pre code {{
            background-color: transparent;
            color: inherit;
            padding: 0;
            border: none;
        }}
        
        ul, ol {{
            margin: 12px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 6px 0;
            line-height: 1.6;
        }}
        
        blockquote {{
            border-left: 4px solid #569cd6;
            padding-left: 20px;
            margin: 15px 0;
            color: #b4b4b4;
            font-style: italic;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #3a3a3a;
            margin: 30px 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        
        th {{
            background-color: #2d2d2d;
            color: #4ec9b0;
            padding: 10px;
            text-align: left;
            border: 1px solid #3e3e3e;
        }}
        
        td {{
            padding: 10px;
            border: 1px solid #3e3e3e;
        }}
        
        tr:nth-child(even) {{
            background-color: #252526;
        }}
        
        a {{
            color: #569cd6;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        strong {{
            color: #dcdcaa;
            font-weight: 600;
        }}
        
        em {{
            color: #b4b4b4;
            font-style: italic;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''
        except ImportError:
            # Fallback if markdown library not available
            return f'<html><body style="padding: 20px; font-family: Arial;"><pre>{markdown_text}</pre></body></html>'


def main():
    """Entry point for AiCopilotDP."""
    app = QApplication(sys.argv)
    app.setApplicationName("AiCopilotDP")
    app.setOrganizationName("AI Studio")
    
    launcher = AiCopilotDP()
    launcher.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

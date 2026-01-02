"""
MD Converter - GUI Controller
Converts documents to Markdown using AI-powered docling
"""

import sys
import json
import configparser
import subprocess
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox,
                               QPushButton, QLineEdit, QListWidget, QPlainTextEdit,
                               QProgressBar, QDialog, QVBoxLayout, QDialogButtonBox, QTextEdit)
from PySide6.QtCore import QFile, QTimer, Qt
from PySide6.QtUiTools import QUiLoader

import convert
import foldersandfiles


class MDConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load UI file
        self.load_ui()
        
        # Initialize variables
        self.config_path = Path(__file__).parent / "config.json"
        self.settings_file = Path(__file__).parent / "settings.ini"
        self.status_file = Path(__file__).parent / "logs" / "md_converter_status.json"
        self.engine_process = None
        
        # Load configuration and settings
        self.load_config()
        self.load_settings()
        
        # Connect UI signals
        self.connect_signals()
        
        # Setup status monitoring timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_status)
        
        # Initialize UI
        self.log_message("MD Converter initialized and ready")
        self.statusBar().showMessage("Ready")
    
    def load_ui(self):
        """Load the UI file dynamically using QUiLoader"""
        ui_path = Path(__file__).parent / "interface.ui"
        
        if not ui_path.exists():
            raise FileNotFoundError(f"UI file not found: {ui_path}")
        
        # Load UI with QUiLoader
        ui_file = QFile(str(ui_path))
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_path}")
            
        loader = QUiLoader()
        loaded_window = loader.load(ui_file, None)  # Load with None parent
        ui_file.close()
        
        if loaded_window is None:
            raise RuntimeError("Failed to load UI")
        
        # Transfer ALL QMainWindow components to prevent garbage collection
        if loaded_window.menuBar():
            self.setMenuBar(loaded_window.menuBar())
        if loaded_window.statusBar():
            self.setStatusBar(loaded_window.statusBar())
        
        # Transfer central widget
        central = loaded_window.centralWidget()
        self.setCentralWidget(central)
        
        # Get widget references from central widget
        self.txt_input_folder = central.findChild(QLineEdit, "txt_input_folder")
        self.txt_output_folder = central.findChild(QLineEdit, "txt_output_folder")
        self.btn_browse_input = central.findChild(QPushButton, "btn_browse_input")
        self.btn_browse_output = central.findChild(QPushButton, "btn_browse_output")
        self.lst_files_to_convert = central.findChild(QListWidget, "lst_files_to_convert")
        self.lst_converted_files = central.findChild(QListWidget, "lst_converted_files")
        self.btn_refresh_list = central.findChild(QPushButton, "btn_refresh_list")
        self.btn_convert = central.findChild(QPushButton, "btn_convert")
        self.btn_clear_log = central.findChild(QPushButton, "btn_clear_log")
        self.btn_help = central.findChild(QPushButton, "btn_help")
        self.progress_bar = central.findChild(QProgressBar, "progress_bar")
        self.txt_log = central.findChild(QPlainTextEdit, "txt_log")
        
        # Set window properties
        self.setWindowTitle("MD Converter - Document to Markdown")
        self.resize(1000, 750)
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.log_message(f"Configuration loaded: {self.config_path.name}")
        except Exception as e:
            self.log_message(f"Error loading config: {e}")
            self.config = {"paths": {}, "options": {}}
    
    def load_settings(self):
        """Load user settings from settings.ini"""
        config = configparser.ConfigParser()
        if self.settings_file.exists():
            config.read(self.settings_file)
            self.input_folder = config.get("Paths", "InputPath", fallback="")
            self.output_folder = config.get("Paths", "OutputPath", fallback=self.config.get("paths", {}).get("output_folder", ""))
            
            # Update UI
            if self.input_folder:
                self.txt_input_folder.setText(self.input_folder)
                self.populate_file_list()
            if self.output_folder:
                self.txt_output_folder.setText(self.output_folder)
            
            self.log_message("Settings loaded")
        else:
            self.input_folder = ""
            self.output_folder = self.config.get("paths", {}).get("output_folder", "")
            if self.output_folder:
                self.txt_output_folder.setText(self.output_folder)
    
    def save_settings(self):
        """Save user settings to settings.ini"""
        config = configparser.ConfigParser()
        config["Paths"] = {
            "InputPath": self.input_folder,
            "OutputPath": self.output_folder
        }
        with open(self.settings_file, "w") as f:
            config.write(f)
        self.log_message("Settings saved")
    
    def connect_signals(self):
        """Connect UI widget signals to methods"""
        self.btn_browse_input.clicked.connect(self.on_browse_input)
        self.btn_browse_output.clicked.connect(self.on_browse_output)
        self.btn_refresh_list.clicked.connect(self.populate_file_list)
        self.btn_convert.clicked.connect(self.on_convert_files)
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.btn_help.clicked.connect(self.on_help_clicked)
    
    def on_browse_input(self):
        """Handle browse input folder button"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
            self.input_folder if self.input_folder else str(Path.home())
        )
        
        if folder:
            self.input_folder = folder
            self.txt_input_folder.setText(self.input_folder)
            self.save_settings()
            self.log_message(f"Input folder set: {folder}")
            self.statusBar().showMessage(f"Input: {Path(folder).name}", 3000)
            self.populate_file_list()
    
    def on_browse_output(self):
        """Handle browse output folder button"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_folder if self.output_folder else str(Path.home())
        )
        
        if folder:
            self.output_folder = folder
            self.txt_output_folder.setText(self.output_folder)
            self.save_settings()
            self.log_message(f"Output folder set: {folder}")
            self.statusBar().showMessage(f"Output: {Path(folder).name}", 3000)
    
    def populate_file_list(self):
        """Populate the file list with convertible files from input folder"""
        self.lst_files_to_convert.clear()
        
        if not self.input_folder:
            self.log_message("Input folder not set")
            return
        
        self.log_message(f"Scanning folder: {self.input_folder}")
        files = foldersandfiles.get_convertible_files(self.input_folder)
        
        if not files:
            self.log_message("No convertible files found")
            self.statusBar().showMessage("No files found", 2000)
            return
        
        # Add files to list
        for file_path in files:
            filename = Path(file_path).name
            self.lst_files_to_convert.addItem(filename)
        
        count = len(files)
        self.log_message(f"Found {count} file(s) to convert")
        self.statusBar().showMessage(f"Ready - {count} files found", 2000)
    
    def on_convert_files(self):
        """Handle convert files button - batch convert all files"""
        if not self.input_folder or not self.output_folder:
            QMessageBox.warning(
                self,
                "Folders Not Set",
                "Please set both input and output folders before converting."
            )
            return
        
        if self.lst_files_to_convert.count() == 0:
            QMessageBox.information(
                self,
                "No Files",
                "No files to convert. Please select an input folder with compatible files."
            )
            return
        
        # Clear converted list
        self.lst_converted_files.clear()
        self.progress_bar.setValue(0)
        
        total_files = self.lst_files_to_convert.count()
        successful = 0
        failed = 0
        
        self.log_message("="*60)
        self.log_message(f"Starting conversion of {total_files} file(s)")
        
        # Process each file
        for i in range(total_files):
            filename = self.lst_files_to_convert.item(i).text()
            input_file = str(Path(self.input_folder) / filename)
            
            # Update progress
            progress = int(((i + 1) / total_files) * 100)
            self.progress_bar.setValue(progress)
            self.statusBar().showMessage(f"Converting {i + 1}/{total_files}: {filename}", 0)
            QApplication.processEvents()  # Update UI
            
            self.log_message(f"[{i + 1}/{total_files}] {filename}")
            
            # Convert file
            try:
                success, message, output_file = convert.convert_file(input_file, self.output_folder)
                
                if success:
                    successful += 1
                    output_filename = Path(output_file).name
                    self.lst_converted_files.addItem(output_filename)
                    self.log_message(f"  ✓ {message}")
                else:
                    failed += 1
                    self.log_message(f"  ✗ {message}")
            except Exception as e:
                failed += 1
                self.log_message(f"  ✗ Exception: {str(e)}")
        
        # Final status
        final_msg = f"Conversion complete: {successful} successful, {failed} failed"
        self.log_message("="*60)
        self.log_message(final_msg)
        self.statusBar().showMessage(final_msg, 5000)
        
        # Show completion message
        QMessageBox.information(
            self,
            "Conversion Complete",
            f"Converted {successful} file(s) successfully.\n{failed} file(s) failed."
        )
    
    def check_status(self):
        """Check engine status from JSON file (for subprocess monitoring)"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                    message = status.get('message', 'Unknown')
                    progress = status.get('progress', 0)
                    self.progress_bar.setValue(progress)
                    self.statusBar().showMessage(f"Engine: {message}", 0)
        except Exception:
            pass  # Silent fail for status checks
    
    def on_help_clicked(self):
        """Open help documentation viewer"""
        help_dialog = HelpViewer(self)
        help_dialog.exec()
    
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.txt_log.appendPlainText(log_entry)
    
    def clear_log(self):
        """Clear the log display"""
        self.txt_log.clear()
        self.log_message("Log cleared")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup: stop engine process if running
        if self.engine_process and self.engine_process.poll() is None:
            self.engine_process.terminate()
        
        self.log_message("MD Converter closed")
        event.accept()


class HelpViewer(QDialog):
    """Dialog to display help documentation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MD Converter Help")
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
        """Convert markdown to HTML with Obsidian-style dark theme"""
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


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    try:
        window = MDConverterGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting MD Converter: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

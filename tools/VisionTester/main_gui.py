"""
Vision Tester GUI - PySide6 Interface
Main GUI controller for YOLO object detection
"""

import os
import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QTextEdit,
    QProgressBar, QComboBox, QSlider, QCheckBox,
    QTabWidget, QFileDialog, QMessageBox, QDialog, QVBoxLayout,
    QDialogButtonBox
)
from PySide6.QtCore import QTimer, QFile, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader

from detector_factory import DetectorFactory


class HelpViewer(QDialog):
    """Dialog to display help documentation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vision Tester Help")
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
        """Convert markdown to HTML with dark theme."""
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


class VisionTesterGUI(QMainWindow):
    """Main GUI window for Vision Tester"""

    def __init__(self):
        super().__init__()
        
        # Load UI file
        ui_path = Path(__file__).parent / "interface.ui"
        ui_file = QFile(str(ui_path))
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        
        # CRITICAL: Load with None parent, then transfer ALL components
        loaded_window = loader.load(ui_file, None)
        ui_file.close()
        
        # Transfer ALL QMainWindow components to prevent loss
        if loaded_window.menuBar():
            self.setMenuBar(loaded_window.menuBar())
        if loaded_window.statusBar():
            self.setStatusBar(loaded_window.statusBar())
        
        # Transfer central widget
        central = loaded_window.centralWidget()
        self.setCentralWidget(central)
        
        # Get widget references from central widget
        self.lbl_framework_status = central.findChild(QLabel, "lbl_framework_status")
        self.cmb_model = central.findChild(QComboBox, "cmb_model")
        self.txt_model_info = central.findChild(QTextEdit, "txt_model_info")
        self.btn_load_model = central.findChild(QPushButton, "btn_load_model")
        
        self.sld_confidence = central.findChild(QSlider, "sld_confidence")
        self.lbl_confidence_value = central.findChild(QLabel, "lbl_confidence_value")
        self.chk_save_txt = central.findChild(QCheckBox, "chk_save_txt")
        
        self.btn_select_image = central.findChild(QPushButton, "btn_select_image")
        self.lbl_image_path = central.findChild(QLabel, "lbl_image_path")
        self.btn_select_input_folder = central.findChild(QPushButton, "btn_select_input_folder")
        self.lbl_input_folder = central.findChild(QLabel, "lbl_input_folder")
        self.btn_select_output_folder = central.findChild(QPushButton, "btn_select_output_folder")
        self.lbl_output_folder = central.findChild(QLabel, "lbl_output_folder")
        
        self.btn_detect_single = central.findChild(QPushButton, "btn_detect_single")
        self.btn_detect_batch = central.findChild(QPushButton, "btn_detect_batch")
        
        self.prg_progress = central.findChild(QProgressBar, "prg_progress")
        self.txt_log = central.findChild(QTextEdit, "txt_log")
        
        self.tab_display = central.findChild(QTabWidget, "tab_display")
        self.lbl_input_image = central.findChild(QLabel, "lbl_input_image")
        self.lbl_output_image = central.findChild(QLabel, "lbl_output_image")
        
        self.btn_help = central.findChild(QPushButton, "btn_help")
        
        # Initialize state
        self.detector = None
        self.engine_process = None
        self.current_image_path = None
        self.config_path = Path(__file__).parent / "config.json"
        self.status_file = Path(__file__).parent / "logs" / "vision_tester_status.json"
        
        # Setup status monitoring timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_progress_from_status)
        
        # Connect signals
        self.connect_signals()
        
        # Load available models
        self.load_available_models()
        
        self.log("Vision Tester initialized. Select a model to begin.")

    def connect_signals(self):
        """Connect UI signals to methods"""
        if self.btn_load_model:
            self.btn_load_model.clicked.connect(self.load_model)
        
        if self.cmb_model:
            self.cmb_model.currentTextChanged.connect(self.on_model_changed)
        
        if self.sld_confidence:
            self.sld_confidence.valueChanged.connect(self.update_confidence_label)
        
        if self.btn_select_image:
            self.btn_select_image.clicked.connect(self.select_input_image)
        
        if self.btn_select_input_folder:
            self.btn_select_input_folder.clicked.connect(self.select_input_folder)
        
        if self.btn_select_output_folder:
            self.btn_select_output_folder.clicked.connect(self.select_output_folder)
        
        if self.btn_detect_single:
            self.btn_detect_single.clicked.connect(self.detect_single)
        
        if self.btn_detect_batch:
            self.btn_detect_batch.clicked.connect(self.detect_batch)
        
        if self.btn_help:
            self.btn_help.clicked.connect(self.on_help_clicked)

    def load_available_models(self):
        """Load available models from detector factory"""
        try:
            status = DetectorFactory.get_framework_status()
            status_text = "Frameworks: "
            for framework, available in status.items():
                icon = "✓" if available else "✗"
                status_text += f"{framework} {icon}  "
            
            if self.lbl_framework_status:
                self.lbl_framework_status.setText(status_text)
            
            # Get all models
            models_list = DetectorFactory.get_all_models_flat_list()
            if self.cmb_model:
                for model_name in models_list:
                    self.cmb_model.addItem(model_name, model_name)
            
            self.log("System initialized. Select a model to begin.")
            
        except Exception as e:
            self.log(f"Error loading models: {str(e)}", error=True)

    def on_model_changed(self):
        """Update model info when selection changes"""
        if not self.cmb_model:
            return
            
        model_name = self.cmb_model.currentData()
        if not model_name:
            return
        
        info_text = f"Model: {model_name}\n"
        
        # Extract size and version info
        try:
            from ultralytics_detector import UltralyticsDetector
            
            for size_key in ["nano", "small", "medium", "balanced", "large", "xlarge", "compact", "extended"]:
                if size_key in model_name:
                    size_info = UltralyticsDetector.get_model_info(size_key)
                    if size_info:
                        info_text += f"Speed: {size_info.get('speed', 'N/A')}\n"
                        info_text += f"Accuracy: {size_info.get('accuracy', 'N/A')}\n"
                        info_text += f"Parameters: {size_info.get('params', 'N/A')}\n"
                    break
        except Exception:
            pass
        
        if self.txt_model_info:
            self.txt_model_info.setText(info_text)

    def load_model(self):
        """Load the selected model"""
        if not self.cmb_model:
            self.log("No model combo box found", error=True)
            return
        
        model_name = self.cmb_model.currentData()
        if not model_name:
            self.log("Please select a model first.", error=True)
            return
        
        try:
            self.log(f"Loading model: {model_name}...")
            
            conf_threshold = self.sld_confidence.value() / 100 if self.sld_confidence else 0.25
            
            self.detector = DetectorFactory.create_detector(
                model_name=model_name,
                conf_threshold=conf_threshold,
                filter_classes=None
            )
            
            self.log("Model loaded successfully! Ready for detection.")
            
            if self.btn_detect_single:
                self.btn_detect_single.setEnabled(True)
            if self.btn_detect_batch:
                self.btn_detect_batch.setEnabled(True)
            
        except Exception as e:
            self.log(f"Error loading model: {str(e)}", error=True)
            QMessageBox.critical(self, "Error", f"Failed to load model:\n{str(e)}")

    def update_confidence_label(self):
        """Update confidence threshold label"""
        if not self.sld_confidence:
            return
        
        value = self.sld_confidence.value() / 100
        
        if self.lbl_confidence_value:
            self.lbl_confidence_value.setText(f"{value:.2f}")
        
        # Update detector if loaded
        if self.detector:
            self.detector.conf_threshold = value

    def select_input_image(self):
        """Select single input image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            if self.lbl_image_path:
                self.lbl_image_path.setText(os.path.basename(file_path))
            self.log(f"Selected image: {file_path}")
            self.display_image(file_path, self.lbl_input_image)

    def select_input_folder(self):
        """Select input folder for batch processing"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        
        if folder_path and self.lbl_input_folder:
            self.lbl_input_folder.setText(folder_path)
            self.log(f"Selected input folder: {folder_path}")

    def select_output_folder(self):
        """Select output folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        
        if folder_path and self.lbl_output_folder:
            self.lbl_output_folder.setText(folder_path)
            self.log(f"Selected output folder: {folder_path}")

    def display_image(self, image_path, label_widget):
        """Display image in a QLabel widget"""
        if not label_widget:
            return
        
        try:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                label_widget.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            label_widget.setPixmap(scaled_pixmap)
        except Exception as e:
            self.log(f"Error displaying image: {str(e)}", error=True)

    def detect_single(self):
        """Run detection on single image"""
        if not self.detector:
            QMessageBox.warning(self, "Warning", "Please load a model first!")
            return
        
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please select an input image!")
            return
        
        output_folder = self.lbl_output_folder.text() if self.lbl_output_folder else ""
        if output_folder == "No output folder selected":
            output_folder = os.path.join(
                os.path.dirname(self.current_image_path), "output"
            )
            os.makedirs(output_folder, exist_ok=True)
            if self.lbl_output_folder:
                self.lbl_output_folder.setText(output_folder)
        
        output_path = os.path.join(
            output_folder, "detected_" + os.path.basename(self.current_image_path)
        )
        
        self.log("Starting single image detection...")
        if self.prg_progress:
            self.prg_progress.setValue(0)
        
        try:
            if self.prg_progress:
                self.prg_progress.setValue(50)
            
            self.detector.detect_single(
                image_path=self.current_image_path,
                output_path=output_path,
                show=False
            )
            
            if self.prg_progress:
                self.prg_progress.setValue(100)
            
            self.log(f"Detection complete! Saved to: {output_path}")
            
            # Display output image
            if os.path.exists(output_path):
                self.display_image(output_path, self.lbl_output_image)
                if self.tab_display:
                    self.tab_display.setCurrentIndex(1)  # Switch to output tab
            
            QMessageBox.information(self, "Success", f"Detection complete!\nSaved to: {output_path}")
            
        except Exception as e:
            self.log(f"Detection failed: {str(e)}", error=True)
            QMessageBox.critical(self, "Error", f"Detection failed:\n{str(e)}")
            if self.prg_progress:
                self.prg_progress.setValue(0)

    def detect_batch(self):
        """Run detection on batch of images"""
        if not self.detector:
            QMessageBox.warning(self, "Warning", "Please load a model first!")
            return
        
        input_folder = self.lbl_input_folder.text() if self.lbl_input_folder else ""
        if input_folder == "No folder selected":
            QMessageBox.warning(self, "Warning", "Please select an input folder!")
            return
        
        output_folder = self.lbl_output_folder.text() if self.lbl_output_folder else ""
        if output_folder == "No output folder selected":
            output_folder = os.path.join(input_folder, "output")
            os.makedirs(output_folder, exist_ok=True)
            if self.lbl_output_folder:
                self.lbl_output_folder.setText(output_folder)
        
        self.log("Starting batch detection...")
        if self.prg_progress:
            self.prg_progress.setValue(0)
        
        try:
            if self.prg_progress:
                self.prg_progress.setValue(10)
            
            save_txt = self.chk_save_txt.isChecked() if self.chk_save_txt else False
            
            self.detector.detect_batch(
                input_folder=input_folder,
                output_folder=output_folder,
                save_txt=save_txt
            )
            
            if self.prg_progress:
                self.prg_progress.setValue(100)
            
            self.log(f"Batch detection complete! Results in: {output_folder}")
            QMessageBox.information(self, "Success", f"Batch detection complete!\nResults in: {output_folder}")
            
        except Exception as e:
            self.log(f"Detection failed: {str(e)}", error=True)
            QMessageBox.critical(self, "Error", f"Detection failed:\n{str(e)}")
            if self.prg_progress:
                self.prg_progress.setValue(0)

    def update_progress_from_status(self):
        """Update progress from status.json file (for subprocess mode)"""
        if not self.status_file.exists():
            return
        
        try:
            with open(self.status_file, 'r') as f:
                status_data = json.load(f)
            
            progress = status_data.get('progress', 0)
            message = status_data.get('message', '')
            
            if self.prg_progress:
                self.prg_progress.setValue(progress)
            
            if message:
                self.log(message)
            
            # Stop timer if complete
            if status_data.get('status') in ['complete', 'error']:
                self.status_timer.stop()
                
        except Exception:
            pass  # Ignore read errors

    def log(self, message, error=False):
        """Add message to log"""
        if not self.txt_log:
            return
        
        if error:
            message = f"❌ {message}"
        else:
            message = f"✓ {message}"
        
        self.txt_log.append(message)
        # Auto-scroll to bottom
        scrollbar = self.txt_log.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def on_help_clicked(self):
        """Open help documentation viewer."""
        help_dialog = HelpViewer(self)
        help_dialog.exec()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern look
    
    window = VisionTesterGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

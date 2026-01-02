"""
Vision Tester Engine - Headless CLI Detection Engine
Runs YOLO object detection without GUI (AWS-compatible)
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from detector_factory import DetectorFactory


class VisionTesterEngine:
    """Headless YOLO detection engine for CLI and AWS execution"""

    def __init__(self, config_path):
        """
        Initialize engine with configuration

        Args:
            config_path: Path to config.json file
        """
        self.config = self.load_config(config_path)
        self.config_path = config_path
        self.tool_dir = Path(__file__).parent
        self.logs_dir = self.tool_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        self.setup_logging()
        self.detector = None
        self.status_file = self.logs_dir / "vision_tester_status.json"

    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)

    def setup_logging(self):
        """Setup twin-stream logging (console + file)"""
        log_filename = f"vision_tester_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = self.logs_dir / log_filename

        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup root logger
        self.logger = logging.getLogger('VisionTester')
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info("=" * 60)
        self.logger.info("Vision Tester Engine Starting")
        self.logger.info(f"Config: {self.config_path}")
        self.logger.info(f"Log file: {log_path}")
        self.logger.info("=" * 60)

    def update_status(self, status, progress, message):
        """
        Update status JSON file for GUI monitoring

        Args:
            status: Current status ('running', 'complete', 'error')
            progress: Progress percentage (0-100)
            message: Status message
        """
        status_data = {
            'status': status,
            'progress': progress,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update status file: {e}")

    def load_model(self):
        """Load YOLO model based on config"""
        try:
            model_name = self.config.get('model', {}).get('name', 'yolo11x.pt')
            conf_threshold = self.config.get('model', {}).get('confidence_threshold', 0.25)
            filter_classes = self.config.get('model', {}).get('filter_classes', None)

            self.logger.info(f"Loading model: {model_name}")
            self.logger.info(f"Confidence threshold: {conf_threshold}")
            
            if filter_classes:
                self.logger.info(f"Filtering classes: {filter_classes}")

            self.update_status('running', 10, f'Loading model: {model_name}')

            self.detector = DetectorFactory.create_detector(
                model_name=model_name,
                conf_threshold=conf_threshold,
                filter_classes=filter_classes
            )

            self.logger.info("Model loaded successfully!")
            self.update_status('running', 20, 'Model loaded')
            return True

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.update_status('error', 0, f'Model loading failed: {str(e)}')
            return False

    def run_detection(self, mode, input_path, output_path, save_txt=False):
        """
        Run detection (single or batch)

        Args:
            mode: 'single' or 'batch'
            input_path: Path to image or folder
            output_path: Path to save results
            save_txt: Save detection results as text files
        """
        try:
            if mode == 'single':
                self.logger.info(f"Running single image detection: {input_path}")
                self.update_status('running', 50, f'Processing: {Path(input_path).name}')

                self.detector.detect_single(
                    image_path=input_path,
                    output_path=output_path,
                    show=False
                )

                self.logger.info(f"Detection complete! Saved to: {output_path}")
                self.update_status('complete', 100, 'Single image detection complete')

            elif mode == 'batch':
                self.logger.info(f"Running batch detection on folder: {input_path}")
                self.update_status('running', 30, 'Starting batch processing')

                self.detector.detect_batch(
                    input_folder=input_path,
                    output_folder=output_path,
                    save_txt=save_txt
                )

                self.logger.info(f"Batch detection complete! Results in: {output_path}")
                self.update_status('complete', 100, 'Batch detection complete')

            else:
                raise ValueError(f"Unknown mode: {mode}. Use 'single' or 'batch'")

            return True

        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            self.update_status('error', 0, f'Detection failed: {str(e)}')
            return False

    def run(self, args):
        """Main execution logic"""
        try:
            self.update_status('running', 0, 'Starting Vision Tester Engine')

            # Load model
            if not self.load_model():
                return False

            # Run detection
            mode = args.mode
            input_path = args.input
            output_path = args.output
            save_txt = args.save_txt

            # Validate input
            if mode == 'single' and not os.path.isfile(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            elif mode == 'batch' and not os.path.isdir(input_path):
                raise FileNotFoundError(f"Input folder not found: {input_path}")

            # Create output directory
            os.makedirs(Path(output_path).parent, exist_ok=True)

            # Run detection
            success = self.run_detection(mode, input_path, output_path, save_txt)

            if success:
                self.logger.info("Vision Tester Engine completed successfully!")
                return True
            else:
                return False

        except KeyboardInterrupt:
            self.logger.warning("Process interrupted by user")
            self.update_status('error', 0, 'Process interrupted by user')
            return False

        except Exception as e:
            self.logger.error(f"Engine failed: {e}", exc_info=True)
            self.update_status('error', 0, f'Engine error: {str(e)}')
            return False

        finally:
            self.logger.info("Vision Tester Engine shutdown")


def main():
    """Main entry point for CLI execution"""
    parser = argparse.ArgumentParser(
        description='Vision Tester Engine - Headless YOLO Object Detection'
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to config.json file'
    )

    parser.add_argument(
        '--mode',
        choices=['single', 'batch'],
        required=True,
        help='Detection mode: single image or batch folder'
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input image path (single) or folder path (batch)'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Output image path (single) or folder path (batch)'
    )

    parser.add_argument(
        '--save-txt',
        action='store_true',
        help='Save detection results as text files (batch mode only)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (quick validation)'
    )

    args = parser.parse_args()

    # Test mode - just validate config and model loading
    if args.test:
        print("=== Test Mode ===")
        print(f"Config: {args.config}")
        engine = VisionTesterEngine(args.config)
        if engine.load_model():
            print("✓ Test passed! Model loaded successfully.")
            sys.exit(0)
        else:
            print("✗ Test failed! Model loading error.")
            sys.exit(1)

    # Normal execution
    engine = VisionTesterEngine(args.config)
    success = engine.run(args)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

"""
MD Converter Engine - Headless document conversion to markdown
This engine can be run from CLI without GUI dependencies for AWS/batch processing
"""

import argparse
import logging
import json
import sys
from pathlib import Path
from datetime import datetime
import convert
import foldersandfiles


class MDConverterEngine:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.status_file = Path(__file__).parent / "logs" / "md_converter_status.json"
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        """Setup twin-stream logging (console + file)"""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"md_converter_{timestamp}.log"
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Configure logger
        self.logger = logging.getLogger('MDConverterEngine')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("MD Converter Engine initialized")
    
    def update_status(self, status, progress, message):
        """Write status to JSON file for GUI monitoring"""
        status_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
    def convert_single_file(self, input_file, output_folder):
        """Convert a single file to markdown"""
        self.logger.info(f"Converting file: {input_file}")
        self.update_status("running", 0, f"Converting {Path(input_file).name}")
        
        success, message, output_file = convert.convert_file(input_file, output_folder)
        
        if success:
            self.logger.info(f"✓ {message}")
            self.update_status("completed", 100, message)
        else:
            self.logger.error(f"✗ {message}")
            self.update_status("error", 0, message)
        
        return success, message, output_file
    
    def convert_folder(self, input_folder, output_folder):
        """Scan folder and convert all compatible files"""
        self.logger.info("="*60)
        self.logger.info(f"Scanning folder: {input_folder}")
        
        # Get list of convertible files
        files = foldersandfiles.get_convertible_files(input_folder)
        
        if not files:
            self.logger.warning("No convertible files found")
            self.update_status("completed", 100, "No files to convert")
            return 0, 0
        
        self.logger.info(f"Found {len(files)} files to convert")
        self.update_status("running", 0, f"Converting {len(files)} files")
        
        # Convert each file
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(files, 1):
            filename = Path(file_path).name
            progress = int((i / len(files)) * 100)
            
            self.logger.info(f"[{i}/{len(files)}] {filename}")
            self.update_status("running", progress, f"Converting {filename}")
            
            success, message, output_file = convert.convert_file(file_path, output_folder)
            
            if success:
                successful += 1
                self.logger.info(f"  ✓ {message}")
            else:
                failed += 1
                self.logger.error(f"  ✗ {message}")
        
        # Final status
        final_msg = f"Completed: {successful} successful, {failed} failed"
        self.logger.info("="*60)
        self.logger.info(final_msg)
        self.update_status("completed", 100, final_msg)
        
        return successful, failed
    
    def run(self, test_mode=False):
        """Main execution method"""
        try:
            self.logger.info("="*60)
            self.logger.info("MD Converter Engine started")
            self.logger.info(f"Test mode: {test_mode}")
            self.logger.info("="*60)
            
            self.update_status("running", 0, "Engine started")
            
            if test_mode:
                self.logger.info("Running in TEST mode")
                self.logger.info("Configuration loaded successfully")
                self.logger.info(f"Tool: {self.config.get('tool_name')}")
                self.logger.info(f"Version: {self.config.get('version')}")
                self.update_status("completed", 100, "Test completed successfully")
                return True
            
            # In normal mode, engine waits for commands (or use CLI args)
            self.logger.info("Engine ready for conversion")
            self.update_status("ready", 0, "Waiting for commands")
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Engine stopped by user")
            self.update_status("stopped", 0, "Stopped by user")
            return False
        except Exception as e:
            self.logger.error(f"Engine error: {e}", exc_info=True)
            self.update_status("error", 0, f"Error: {str(e)}")
            raise


def main():
    parser = argparse.ArgumentParser(description='MD Converter - Document to Markdown Engine')
    parser.add_argument('--config', required=True, help='Path to config.json')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--file', help='Path to single file to convert')
    parser.add_argument('--folder', help='Path to folder to scan and convert')
    parser.add_argument('--output', help='Output folder for converted files')
    
    args = parser.parse_args()
    
    try:
        engine = MDConverterEngine(args.config)
        
        if args.file and args.output:
            # Convert single file
            success, message, output_file = engine.convert_single_file(args.file, args.output)
            print(f"\nResult: {message}")
            if success:
                print(f"Output: {output_file}")
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.folder and args.output:
            # Convert folder
            successful, failed = engine.convert_folder(args.folder, args.output)
            print(f"\nResults: {successful} successful, {failed} failed")
            sys.exit(0 if failed == 0 else 1)
        
        else:
            # Default: test mode or wait for commands
            engine.run(test_mode=args.test)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

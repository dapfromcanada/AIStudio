"""
Tool Tester Engine - AIStudio Tool Testing System
Tests all registered AIStudio tools in headless mode
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class ToolTesterEngine:
    """Engine for testing AIStudio tools in headless mode"""
    
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent
        self.studio_config_path = self.base_path / "studio_config.json"
        self.setup_logging()
        self.test_results = []
        
    def load_config(self, config_path):
        """Load tool configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup twin-stream logging (console + file)"""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"tool_tester_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Tool Tester Engine initialized")
        self.logger.info(f"Log file: {log_file}")
    
    def update_status(self, status, progress, message):
        """Update status JSON for GUI monitoring"""
        status_file = Path(__file__).parent / "logs" / "tool_tester_status.json"
        status_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def load_studio_config(self):
        """Load studio_config.json to get registered tools"""
        try:
            with open(self.studio_config_path, 'r') as f:
                config = json.load(f)
                return config.get('tools', [])
        except FileNotFoundError:
            self.logger.error(f"Studio config not found: {self.studio_config_path}")
            return []
    
    def test_tool(self, tool_info):
        """
        Test a single tool's engine.py
        
        Args:
            tool_info: Tool configuration dict from studio_config.json
            
        Returns:
            dict: Test result with status and details
        """
        tool_id = tool_info['id']
        tool_path = Path(tool_info['path'])
        
        self.logger.info(f"Testing tool: {tool_id}")
        self.update_status("running", 0, f"Testing {tool_id}...")
        
        result = {
            "tool_id": tool_id,
            "tool_name": tool_info['display_name'],
            "status": "unknown",
            "message": "",
            "details": {}
        }
        
        # Check if tool directory exists
        if not tool_path.exists():
            result['status'] = 'fail'
            result['message'] = f"Tool directory not found: {tool_path}"
            self.logger.error(result['message'])
            return result
        
        # Check for engine.py
        engine_path = tool_path / "engine.py"
        if not engine_path.exists():
            result['status'] = 'skip'
            result['message'] = "No engine.py found (GUI-only tool)"
            self.logger.warning(result['message'])
            return result
        
        # Check for config.json
        config_path = tool_path / "config.json"
        if not config_path.exists():
            result['status'] = 'fail'
            result['message'] = "No config.json found"
            self.logger.error(result['message'])
            return result
        
        # Check for virtual environment
        venv_python = tool_path / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            result['status'] = 'fail'
            result['message'] = "Virtual environment not found"
            self.logger.error(result['message'])
            return result
        
        # Run engine.py --test
        try:
            self.logger.info(f"Running: {venv_python} engine.py --config config.json --test")
            
            process = subprocess.run(
                [str(venv_python), "engine.py", "--config", "config.json", "--test"],
                cwd=str(tool_path),
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            result['details']['exit_code'] = process.returncode
            result['details']['stdout'] = process.stdout
            result['details']['stderr'] = process.stderr
            
            if process.returncode == 0:
                result['status'] = 'pass'
                result['message'] = "Test passed successfully"
                self.logger.info(f"✓ {tool_id} test passed")
            else:
                result['status'] = 'fail'
                result['message'] = f"Test failed with exit code {process.returncode}"
                self.logger.error(f"✗ {tool_id} test failed")
                if process.stderr:
                    self.logger.error(f"Error output: {process.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            result['status'] = 'fail'
            result['message'] = "Test timed out (>30s)"
            self.logger.error(f"✗ {tool_id} test timed out")
        
        except Exception as e:
            result['status'] = 'fail'
            result['message'] = f"Exception: {str(e)}"
            self.logger.error(f"✗ {tool_id} test error: {e}")
        
        return result
    
    def test_all_tools(self):
        """Test all registered tools"""
        self.logger.info("Starting test suite for all tools")
        self.update_status("running", 0, "Loading tools...")
        
        tools = self.load_studio_config()
        if not tools:
            self.logger.error("No tools found in studio_config.json")
            self.update_status("error", 0, "No tools to test")
            return
        
        self.logger.info(f"Found {len(tools)} registered tools")
        
        # Test each tool
        total_tools = len(tools)
        for i, tool_info in enumerate(tools):
            progress = int(((i + 1) / total_tools) * 100)
            result = self.test_tool(tool_info)
            self.test_results.append(result)
            self.update_status("running", progress, f"Tested {i + 1}/{total_tools} tools")
        
        # Generate summary
        self.generate_summary()
    
    def test_single_tool(self, tool_id):
        """Test a specific tool by ID"""
        self.logger.info(f"Testing single tool: {tool_id}")
        
        tools = self.load_studio_config()
        tool_info = next((t for t in tools if t['id'] == tool_id), None)
        
        if not tool_info:
            self.logger.error(f"Tool not found: {tool_id}")
            self.update_status("error", 0, f"Tool '{tool_id}' not found")
            return
        
        result = self.test_tool(tool_info)
        self.test_results.append(result)
        self.generate_summary()
    
    def generate_summary(self):
        """Generate and log test summary"""
        passed = sum(1 for r in self.test_results if r['status'] == 'pass')
        failed = sum(1 for r in self.test_results if r['status'] == 'fail')
        skipped = sum(1 for r in self.test_results if r['status'] == 'skip')
        
        self.logger.info("\n" + "="*60)
        self.logger.info("TEST SUMMARY")
        self.logger.info("="*60)
        self.logger.info(f"Total tests: {len(self.test_results)}")
        self.logger.info(f"✓ Passed: {passed}")
        self.logger.info(f"✗ Failed: {failed}")
        self.logger.info(f"⊘ Skipped: {skipped}")
        self.logger.info("="*60)
        
        # Detailed results
        for result in self.test_results:
            status_icon = {
                'pass': '✓',
                'fail': '✗',
                'skip': '⊘',
                'unknown': '?'
            }.get(result['status'], '?')
            
            self.logger.info(f"{status_icon} {result['tool_name']}: {result['message']}")
        
        self.logger.info("="*60)
        
        # Update final status
        if failed > 0:
            self.update_status("completed_with_errors", 100, f"{passed} passed, {failed} failed")
        else:
            self.update_status("completed", 100, f"All {passed} tests passed")
        
        # Save results to JSON
        results_file = Path(__file__).parent / "logs" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.logger.info(f"Results saved to: {results_file}")
    
    def run(self, args):
        """Main execution method"""
        try:
            if args.test:
                self.logger.info("Running in TEST mode")
                self.logger.info("Tool Tester Engine is operational")
                self.update_status("test_mode", 100, "Test mode: Engine operational")
                return 0
            
            if args.tool:
                self.test_single_tool(args.tool)
            else:
                self.test_all_tools()
            
            # Exit code based on results
            failed = sum(1 for r in self.test_results if r['status'] == 'fail')
            return 0 if failed == 0 else 1
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self.update_status("error", 0, str(e))
            return 1


def main():
    """Entry point for CLI execution"""
    parser = argparse.ArgumentParser(description="AIStudio Tool Tester")
    parser.add_argument('--config', required=True, help='Path to config.json')
    parser.add_argument('--test', action='store_true', help='Test mode (validate engine works)')
    parser.add_argument('--tool', help='Test specific tool by ID (e.g., md_converter)')
    
    args = parser.parse_args()
    
    engine = ToolTesterEngine(args.config)
    exit_code = engine.run(args)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

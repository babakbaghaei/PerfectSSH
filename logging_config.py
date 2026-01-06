"""
PerfectSSH - Logging Configuration
Centralized logging setup for the application.
"""

import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file=None):
    """Setup logging configuration for the application."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    if log_file is None:
        log_file = log_dir / "perfectssh.log"
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from libraries
    logging.getLogger('paramiko').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger('perfectssh')
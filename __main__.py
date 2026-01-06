#!/usr/bin/env python3
"""
PerfectSSH - Main Entry Point
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import and run main
import main
main.main()
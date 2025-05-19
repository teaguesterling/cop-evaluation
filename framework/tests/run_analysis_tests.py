#!/usr/bin/env python
"""
Run all tests for the COP static analysis module.
"""

import unittest
import sys
import os

if __name__ == "__main__":
    # Add project root to Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    
    # Discover and run all analysis tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = 'test_analysis_*.py'
    
    suite = loader.discover(start_dir, pattern)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Set the exit code based on test results
    sys.exit(not result.wasSuccessful())
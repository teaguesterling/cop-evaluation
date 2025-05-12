# config.py
import os

# Path to Claude CLI executable
CLAUDE_PATH = os.environ.get("CLAUDE_PATH", "/home/teague/.claude/local/claude")

# Directory for results
RESULTS_DIR = "results"

# Default models to test with
DEFAULT_MODELS = ["claude-3-5-haiku-20241022", "claude-3-7-sonnet-20250219"]

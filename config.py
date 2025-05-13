# config.py
import os

# Path to Claude CLI executable
CLAUDE_PATH = os.environ.get("CLAUDE_PATH", "/home/teague/.claude/local/claude")

# Directory for results
RESULTS_DIR = "results"

# Default models to test with
DEFAULT_MODELS = ["claude-3-5-haiku-20241022", "claude-3-7-sonnet-20250219"]
DEFAULT_MODELS = ["claude-3-5-haiku-20241022"]

# Maps test cases to relevant prompts
# Format: {test_category/test_case: [list_of_applicable_prompt_names]}
TEST_PROMPT_MAPPING = {
    # Default mapping (applied if no specific mapping exists)
    "DEFAULT": ["understanding", "code_review"],
    
    # Category-level mappings (applied to all tests in the category)
    "anti_patterns/*": ["problem_detection", "refactoring", "code_review"],
    "debugging/*": ["debugging", "problem_detection", "code_review"],
    "design_patterns/*": ["understanding", "feature_implementation", "knowledge_transfer"],
    
    # Test-specific mappings
    "debugging/buggy_cart": ["debugging", "problem_detection"],
    "hallucination/contradictory_docs": ["understanding", "problem_detection", "code_review"],
    "hallucination/misleading_docs": ["understanding", "problem_detection", "code_review"],
    "hallucination/missing_implementation": ["problem_detection", "feature_implementation"]
}

VARIANTS = ["base", "cop", "docstring", "comments"]

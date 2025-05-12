# test_mapping.py

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


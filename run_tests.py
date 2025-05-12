# run_tests.py
import argparse
from pathlib import Path
import json
import sys
import importlib.util

from framework.runner import TestRunner
from framework.evaluator import TestEvaluator
from framework.reporter import TestReporter

def load_config(config_path="config.py"):
    """Load configuration from file"""
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def discover_tests():
    """Discover all available test cases"""
    tests = []
    test_dir = Path("test_cases")
    
    # Look at all subdirectories
    for path in Path("test_cases").glob("**/*"):
        if not path.is_dir():
            continue
            
        for varaint_file in path.glob("*.py"):
            rel_path = path.relative_to(test_dir)
            tests.append(rel_path)
        
        # Check if this directory contains both base.py and cop.py
        if all(crit in [t.stem for t in tests] for crit in ["base", "cop"]):
            # Get relative path from test_cases directory
            print(f"Found test: {rel_path}")
    
    return [test.as_posix() for test in tests]


def discover_prompts():
    """Discover all available prompt types"""
    prompts = []
    prompt_dir = Path("prompts")
    
    for prompt_file in prompt_dir.glob("*.txt"):
        prompts.append(prompt_file.stem)
        
    return prompts

def get_applicable_prompts(config, test_path):
    """
    Determine which prompts apply to a specific test case.
    
    Args:
        test_path: Path to test case (category/test_case)
        
    Returns:
        List of applicable prompt names
    """
    TEST_PROMPT_MAPPING = getattr(config, "TEST_PROMPT_MAPPING", {})
    # Check for exact match
    if test_path in TEST_PROMPT_MAPPING:
        return TEST_PROMPT_MAPPING[test_path]
    
    # Check for category match
    category = test_path.split("/")[0]
    category_wildcard = f"{category}/*"
    if category_wildcard in TEST_PROMPT_MAPPING:
        return TEST_PROMPT_MAPPING[category_wildcard]
    
    # Fall back to default
    return TEST_PROMPT_MAPPING.get("DEFAULT")


def run_all_tests(config, models, force_rerun=False):
    """Run all tests for specified models, skipping those already run unless forced"""
    all_tests = discover_tests()
    all_prompts = discover_prompts()
    
    if not all_tests:
        print("No tests found!")
        return
        
    if not all_prompts:
        print("No prompts found!")
        return
        
    print(f"Found {len(all_tests)} tests and {len(all_prompts)} prompt types")
    
    runner = TestRunner(config)
    evaluator = TestEvaluator(config)
    
    # Statistics for test execution
    stats = {
        "run": 0,
        "skipped": 0,
        "failed": 0
    }
    
    # Run all combinations of tests
    for model in models:
        print(f"    For model: {model}")
        for test in all_tests:
            print(f"Running test: {test}")
            applicable_prompts = get_applicable_prompts(config, test)
            if applicable_prompts is None:
                applicable_prompts = all_prompts
            print(f"  Applicable prompts: {applicable_prompts}")
            for prompt in applicable_prompts:

                print(f"  With prompt: {prompt}")       
                model_short = model.split('-')[1:3]  # Extract model short name
                model_short = '-'.join(model_short)
                
                # For each variant (base, cop, docstring, comments)
                for variant in ["base", "cop", "comments", "docstring"]:
                    # Check if test result already exists
                    result_dir = Path(f"{config.RESULTS_DIR}/{model_short}/{test}/{variant}/{prompt}")
                    response_file = result_dir / "response.txt"
                    
                    if response_file.exists() and not force_rerun:
                        print(f"      Skipping {variant} (already run)")
                        stats["skipped"] += 1
                        
                        # Make sure metrics are evaluated even for skipped tests
                        if (result_dir / "metrics.json").exists():
                            continue
                            
                        # Find ground truth file if available
                        category, test_case = test.split("/", 1)
                        ground_truth_file = Path(f"ground_truth/{category}/{test_case}.json")
                        
                        if ground_truth_file.exists():
                            evaluator.evaluate_test(result_dir, ground_truth_file)
                        else:
                            evaluator.evaluate_test(result_dir)
                        
                        continue
                    
                    print(f"      Running {variant}")
                    # Run the test
                    result = runner.run_test(test, variant, prompt, model)
                    
                    if result["success"]:
                        stats["run"] += 1
                        
                        # Find ground truth file if available
                        category, test_case = test.split("/", 1)
                        ground_truth_file = Path(f"ground_truth/{category}/{test_case}.json")
                        
                        if ground_truth_file.exists():
                            evaluator.evaluate_test(result["output_dir"], ground_truth_file)
                        else:
                            evaluator.evaluate_test(result["output_dir"])
                    else:
                        stats["failed"] += 1
                        print(f"      Error running test: {result.get('error', 'Unknown error')}")
                
                # Check for and run docstring and comments variants if they exist
                for variant in ["docstring", "comments"]:
                    source_dir = f"test_cases_{variant}"
                    variant_file = Path(f"{source_dir}/{test}/cop.py")
                    
                    if not variant_file.exists():
                        continue
                        
                    # Check if test result already exists
                    result_dir = Path(f"{config.RESULTS_DIR}/{model_short}/{test}/{variant}/{prompt}")
                    response_file = result_dir / "response.txt"
                    
                    if response_file.exists() and not force_rerun:
                        print(f"      Skipping {variant} (already run)")
                        stats["skipped"] += 1
                        
                        # Make sure metrics are evaluated even for skipped tests
                        if (result_dir / "metrics.json").exists():
                            continue
                            
                        # Find ground truth file if available
                        category, test_case = test.split("/", 1)
                        ground_truth_file = Path(f"ground_truth/{category}/{test_case}.json")
                        
                        if ground_truth_file.exists():
                            evaluator.evaluate_test(result_dir, ground_truth_file)
                        else:
                            evaluator.evaluate_test(result_dir)
                        
                        continue
                    
                    print(f"      Running {variant}")
                    # Run the test
                    result = runner.run_test(test, variant, prompt, model, source_dir=source_dir)
                    
                    if result["success"]:
                        stats["run"] += 1
                        
                        # Find ground truth file if available
                        category, test_case = test.split("/", 1)
                        ground_truth_file = Path(f"ground_truth/{category}/{test_case}.json")
                        
                        if ground_truth_file.exists():
                            evaluator.evaluate_test(result["output_dir"], ground_truth_file)
                        else:
                            evaluator.evaluate_test(result["output_dir"])
                    else:
                        stats["failed"] += 1
                        print(f"      Error running test: {result.get('error', 'Unknown error')}")
    
    # Generate reports
    reporter = TestReporter(config)
    reporter.generate_reports()
    
    # Print execution summary
    print("\nExecution Summary:")
    print(f"  Run: {stats['run']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")


def main():
    parser = argparse.ArgumentParser(description="Run COP tests")
    parser.add_argument("--config", default="config.py", help="Path to config file")
    parser.add_argument("--models", nargs="+", 
                        default=["claude-3-5-haiku-20241022", "claude-3-7-sonnet-20250219"], 
                        help="Models to test with")
    parser.add_argument("--force", default=False, action="store_true", help="Rurun all tests")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Run tests
    run_all_tests(config, args.models, force_rerun=args.force)

if __name__ == "__main__":
    main()

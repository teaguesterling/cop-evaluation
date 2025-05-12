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
            
        # Check if this directory contains both base.py and cop.py
        base_file = path / "base.py"
        cop_file = path / "cop.py"
        
        if base_file.exists() and cop_file.exists():
            # Get relative path from test_cases directory
            rel_path = path.relative_to(test_dir)
            tests.append(str(rel_path))
            print(f"Found test: {rel_path}")
    
    return tests


def discover_prompts():
    """Discover all available prompt types"""
    prompts = []
    prompt_dir = Path("prompts")
    
    for prompt_file in prompt_dir.glob("*.txt"):
        prompts.append(prompt_file.stem)
        
    return prompts

def run_all_tests(config, models):
    """Run all tests for specified models"""
    tests = discover_tests()
    prompts = discover_prompts()
    
    if not tests:
        print("No tests found!")
        return
        
    if not prompts:
        print("No prompts found!")
        return
        
    print(f"Found {len(tests)} tests and {len(prompts)} prompt types")
    
    runner = TestRunner(config)
    evaluator = TestEvaluator(config)
    
    # Run all combinations of tests
    for test in tests:
        print(f"Running test: {test}")
        for prompt in prompts:
            print(f"  With prompt: {prompt}")
            for model in models:
                print(f"    For model: {model}")
                
                # Base variant
                result = runner.run_test(test, "base", prompt, model)
                if result["success"]:
                    # Find ground truth file if available
                    category, test_case = test.split("/")
                    ground_truth_file = Path(f"ground_truth/{category}/{test_case}.json")
                    
                    if ground_truth_file.exists():
                        evaluator.evaluate_test(result["output_dir"], ground_truth_file)
                    else:
                        evaluator.evaluate_test(result["output_dir"])
                        
                # COP variant
                result = runner.run_test(test, "cop", prompt, model)
                if result["success"]:
                    # Find ground truth file if available
                    category, test_case = test.split("/")
                    ground_truth_file = Path(f"ground_truth/{category}/{test_case}.json")
                    
                    if ground_truth_file.exists():
                        evaluator.evaluate_test(result["output_dir"], ground_truth_file)
                    else:
                        evaluator.evaluate_test(result["output_dir"])
    
    # Generate reports
    reporter = TestReporter(config)
    reporter.generate_reports()

def main():
    parser = argparse.ArgumentParser(description="Run COP tests")
    parser.add_argument("--config", default="config.py", help="Path to config file")
    parser.add_argument("--models", nargs="+", default=["claude-3-5-haiku-20241022", "claude-3-7-sonnet-20250219"], 
                        help="Models to test with")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Run tests
    run_all_tests(config, args.models)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from pathlib import Path

def test_claude_call(model, claude_path=None):
    """
    Run a simple test call to Claude to verify everything is working.
    
    Args:
        model: The Claude model to use
        claude_path: Optional path to Claude executable
    """
    # Use default claude command if not specified
    if not claude_path:
        claude_path = os.environ.get("CLAUDE_PATH", "claude")
    
    # Create a simple test prompt
    prompt = "Hello Claude! Please respond with a short message confirming you received this test prompt."
    command = [claude_path, "--print"]
    
    print(f"Testing Claude call with model: {model}")
    print(f"Using Claude executable: {claude_path}")
    print(f"Sending test prompt... {prompt}")
    print(f"Command is: {' '.join(command)}")
    
    # Measure execution time
    start_time = time.time()
    
    try:
        # Set up environment with the model
        env = os.environ.copy()
        env["ANTHROPIC_MODEL"] = model
        
        # Run Claude with the test prompt
        process = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            env=env
        )
        
        # Get execution time
        try:
            with open("claude_test_time.txt", "r") as f:
                execution_time = float(f.read().strip())
        except:
            execution_time = time.time() - start_time
        
        # Print results
        print("\n" + "="*50)
        print("Test Results:")
        print("="*50)
        print(f"Exit code: {process.returncode}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Response length: {len(process.stdout)} characters")
        print("\nResponse content:")
        print("-"*50)
        print(process.stdout)
        print("-"*50)
        
        if process.stderr:
            print("\nWarnings/Errors:")
            print(process.stderr)
        
        # Cleanup
        if os.path.exists("claude_test_time.txt"):
            os.remove("claude_test_time.txt")
        
        if process.returncode == 0 and len(process.stdout) > 0:
            print("\n✅ Claude test successful!")
            return True
        else:
            print("\n❌ Claude test failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error executing Claude: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Claude API call")
    parser.add_argument("--model", default="claude-3-5-haiku-20241022", 
                      help="Claude model to test")
    parser.add_argument("--claude-path", default=None,
                      help="Path to Claude executable")
    
    args = parser.parse_args()
    test_claude_call(args.model, args.claude_path)

if __name__ == "__main__":
    main()

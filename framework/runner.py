import os
import subprocess
import json
import time
from pathlib import Path

class TestRunner:
    def __init__(self, config):
        self.config = config
        self.results_dir = Path(config.RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True, parents=True)

    def run_test(self, test_case, variant, prompt_type, model, source_dir="test_cases"):
        """Run a single test with Claude and capture the response"""
        test_dir = Path(f"{source_dir}/{test_case}")
        prompt_file = Path(f"prompts/{prompt_type}.txt")

        variant_file_patterns = [f"{variant}.py", f"{variant}_*.py"]
        
        # Create output directory
        model_short = model.split('-')[1:3]  # Extract model short name
        model_short = '-'.join(model_short)
        
        output_dir = self.results_dir / model_short / test_case / variant / prompt_type
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Build command to run Claude
        cmd = [self.config.CLAUDE_PATH, "--print"]
        
        # Prepare environment
        env = os.environ.copy()
        env["ANTHROPIC_MODEL"] = model
        
        # Run Claude and capture output
        try:
            # Combine prompt with code
  
            combined_prompt = self._prepare_prompt(prompt_file, test_dir, variant_file_patterns)
            with open(output_dir / "prompt.txt", "w") as f:
                f.write(combined_prompt)
                
            # Execute Claude
            start_time = time.time()
            process = subprocess.run(
                cmd,
                input=combined_prompt,
                text=True,
                capture_output=True,
                env=env
            )
            end_time = time.time()
            
            # Save response
            with open(output_dir / "response.txt", "w") as f:
                f.write(process.stdout)
                
            # Save metadata
            metadata = {
                "test_case": test_case,
                "variant": variant,
                "prompt_type": prompt_type,
                "model": model,
                "execution_time": end_time - start_time,
                "exit_code": process.returncode
            }
            
            with open(output_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
            return {
                "success": True,
                "output_dir": output_dir,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error running test: {e}")
            return {"success": False, "error": str(e)}
        
    def _prepare_prompt(self, prompt_file, test_dir, code_patterns=("*.py",)):
        """Combine prompt with code files"""
        # Read the prompt
        with open(prompt_file, "r") as f:
            prompt = f.read()

        # Find all Python files in the test directoris
        code_files = list(set(code for pat in code_patterns for code in test_dir.glob(pat)))
        
        # Add code content to prompt
        code_sections = []
        for file in code_files:
            with open(file, "r") as f:
                code = f.read()
            code_sections.append(f"File: {file.name}\n\n```python\n{code}\n```\n")

        if not code_sections:
            print(f"WARNING: NO CODE ADDED TO {prompt_file} in {test_dir}")
            
        # Combine everything
        combined = prompt + "\n\n" + "\n\n".join(code_sections)
        return combined

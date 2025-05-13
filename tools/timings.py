#!/usr/bin/env python3
# preprocess_metrics.py

import json
from pathlib import Path
import argparse

def consolidate_timing_data(results_dir):
    """Consolidate timing data from metadata.json into metrics.json"""
    results_dir = Path(results_dir)
    count = 0
    
    # Walk through all test result directories
    for metrics_file in results_dir.glob("**/**/metrics.json"):
        metadata_file = metrics_file.parent / "metadata.json"
        
        # Skip if no metadata file exists
        if not metadata_file.exists():
            continue
            
        # Read current metrics
        with open(metrics_file, "r") as f:
            metrics = json.load(f)
            
        # Skip if metrics already has execution_time
        if metrics.get("execution_time"):
            continue
            
        # Read metadata for execution_time
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                
            # Update metrics with execution_time from metadata
            if "execution_time" in metadata:
                metrics["execution_time"] = metadata["execution_time"]
                
                # Write updated metrics back
                with open(metrics_file, "w") as f:
                    json.dump(metrics, f, indent=2)
                    
                count += 1
        except Exception as e:
            print(f"Error processing {metadata_file}: {e}")
    
    print(f"Updated {count} metrics files with execution time data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidate timing data from metadata.json into metrics.json")
    parser.add_argument("results_dir", help="Path to results directory")
    args = parser.parse_args()
    
    consolidate_timing_data(args.results_dir)

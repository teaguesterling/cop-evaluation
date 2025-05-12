import re
import json
from pathlib import Path

class TestEvaluator:
    def __init__(self, config):
        self.config = config
        
    def evaluate_test(self, output_dir, ground_truth_file=None):
        """Evaluate test results against ground truth"""
        output_dir = Path(output_dir)
        
        # Load response
        with open(output_dir / "response.txt", "r") as f:
            response = f.read()
            
        # Load timing info
        try:
            with open(output_dir / "time_real.txt", "r") as f:
                execution_time = float(f.read().strip())
        except:
            execution_time = None
            
        # Calculate basic metrics
        basic_metrics = self._calculate_basic_metrics(response, execution_time)
        
        # Calculate hallucination metrics if ground truth available
        hallucination_metrics = {}
        if ground_truth_file:
            with open(ground_truth_file, "r") as f:
                ground_truth = json.load(f)
            hallucination_metrics = self._evaluate_hallucination(response, ground_truth)
            
        # Calculate annotation utilization
        annotation_metrics = self._evaluate_annotation_utilization(response)
        
        # Combine all metrics
        metrics = {
            **basic_metrics,
            **hallucination_metrics,
            **annotation_metrics
        }
        
        # Save metrics
        with open(output_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
            
        return metrics
    
    def _calculate_basic_metrics(self, response, execution_time):
        """Calculate basic metrics like word count, etc."""
        words = response.split()
        
        return {
            "word_count": len(words),
            "execution_time": execution_time,
            "words_per_second": len(words) / execution_time if execution_time else None,
            "character_count": len(response),
            "line_count": len(response.splitlines())
        }
        
    def _evaluate_hallucination(self, response, ground_truth):
        """Evaluate response for hallucinations against ground truth"""
        metrics = {
            "factual_accuracy": 0.0,
            "fabricated_elements": [],
            "contradictions_detected": 0
        }
        
        # Check for mentions of non-existent elements
        for non_existent in ground_truth.get("non_existent_elements", []):
            if non_existent in response:
                metrics["fabricated_elements"].append(non_existent)
                
        # Check factual questions
        correct = 0
        total = len(ground_truth.get("factual_questions", []))
        
        for question in ground_truth.get("factual_questions", []):
            if question["correct_answer"] in response:
                correct += 1
                
        if total > 0:
            metrics["factual_accuracy"] = correct / total
            
        # Check for contradiction detection
        for contradiction in ground_truth.get("contradictions", []):
            if any(term in response for term in contradiction["detection_terms"]):
                metrics["contradictions_detected"] += 1
                
        return metrics
    
    def _evaluate_annotation_utilization(self, response):
        """Evaluate how annotations are utilized in the response"""
        metrics = {
            "intent_mentions": 0,
            "invariant_mentions": 0,
            "human_decision_mentions": 0,
            "ai_implement_mentions": 0
        }
        
        metrics["intent_mentions"] = response.lower().count("intent")
        metrics["invariant_mentions"] = response.lower().count("invariant")
        metrics["human_decision_mentions"] = response.lower().count("human decision") + response.lower().count("human judgment")
        metrics["ai_implement_mentions"] = response.lower().count("ai implement")
        
        return metrics

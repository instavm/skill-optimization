"""
Main Skill Optimizer

This module orchestrates the optimization of Claude Skills using DSPy techniques.
"""

import json
import dspy
from typing import List, Dict, Any, Optional
from pathlib import Path
import anthropic
from .models import CodeReviewModule, FewShotCodeReview, module_to_skill_prompt
from .evaluator import CodeReviewEvaluator, create_metric_function
from .utils import load_json, save_json, read_code_file


class SkillOptimizer:
    """
    Optimizes Claude Skills using DSPy-inspired techniques.
    """

    def __init__(
        self,
        skill_path: str,
        training_data_path: str,
        validation_data_path: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the optimizer.

        Args:
            skill_path: Path to the baseline skill markdown file
            training_data_path: Path to training data JSON
            validation_data_path: Optional path to validation data
            openai_api_key: OpenAI API key for DSPy (uses GPT as optimizer)
        """
        self.skill_path = Path(skill_path)
        self.training_data = load_json(training_data_path)
        self.validation_data = load_json(validation_data_path) if validation_data_path else None

        # Initialize DSPy with language model
        # Note: DSPy typically uses OpenAI, but can be configured for other models
        if openai_api_key:
            lm = dspy.OpenAI(model="gpt-4", api_key=openai_api_key)
            dspy.settings.configure(lm=lm)

        # Initialize evaluator
        self.evaluator = CodeReviewEvaluator()
        self.metric = create_metric_function(self.evaluator)

    def prepare_training_set(self) -> List[dspy.Example]:
        """
        Convert training data to DSPy Examples.

        Returns:
            List of DSPy Example objects
        """
        examples = []

        for case in self.training_data.get("training_cases", []):
            # Read the code file
            code = read_code_file(case["file_path"])

            # Create DSPy Example
            example = dspy.Example(
                code=code,
                language=case["language"],
                expected_issues=case["expected_issues"],
                severity_distribution=case.get("severity_distribution", {}),
                overall_quality=case.get("overall_quality", "")
            ).with_inputs("code", "language")

            examples.append(example)

        return examples

    def optimize_with_bootstrap_fewshot(
        self,
        max_bootstrapped_demos: int = 4,
        max_labeled_demos: int = 8
    ) -> dspy.Module:
        """
        Optimize using DSPy's BootstrapFewShot.

        This automatically selects the best few-shot examples.

        Args:
            max_bootstrapped_demos: Max examples to generate
            max_labeled_demos: Max labeled examples to use

        Returns:
            Optimized module
        """
        print("🔧 Preparing training data...")
        trainset = self.prepare_training_set()

        print(f"📚 Training set size: {len(trainset)}")

        print("🚀 Starting BootstrapFewShot optimization...")

        # Initialize the module to optimize
        module = FewShotCodeReview()

        # Create optimizer
        optimizer = dspy.BootstrapFewShot(
            metric=self.metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos
        )

        # Compile (optimize)
        print("⚙️  Compiling optimized module...")
        optimized_module = optimizer.compile(
            module,
            trainset=trainset
        )

        print("✅ Optimization complete!")
        return optimized_module

    def optimize_with_mipro(
        self,
        num_candidates: int = 10,
        init_temperature: float = 1.0
    ) -> dspy.Module:
        """
        Optimize using DSPy's MIPRO (Multi-prompt Instruction Proposal Optimizer).

        This optimizes both instructions and examples.

        Args:
            num_candidates: Number of instruction candidates to try
            init_temperature: Temperature for prompt generation

        Returns:
            Optimized module
        """
        print("🔧 Preparing training data...")
        trainset = self.prepare_training_set()

        # Split into train/val if validation data not provided
        if self.validation_data:
            valset = self._prepare_validation_set()
        else:
            # Use 20% for validation
            split_idx = int(len(trainset) * 0.8)
            valset = trainset[split_idx:]
            trainset = trainset[:split_idx]

        print(f"📚 Train set: {len(trainset)}, Val set: {len(valset)}")

        print("🚀 Starting MIPRO optimization...")

        module = CodeReviewModule()

        # MIPRO optimizer
        optimizer = dspy.MIPROv2(
            metric=self.metric,
            num_candidates=num_candidates,
            init_temperature=init_temperature
        )

        print("⚙️  Running optimization (this may take a while)...")
        optimized_module = optimizer.compile(
            module,
            trainset=trainset,
            valset=valset,
            num_trials=20
        )

        print("✅ Optimization complete!")
        return optimized_module

    def _prepare_validation_set(self) -> List[dspy.Example]:
        """Prepare validation set from validation data."""
        examples = []

        for case in self.validation_data.get("validation_cases", []):
            example = dspy.Example(
                code=case.get("code_snippet", ""),
                language=case.get("language", ""),
                expected_issues=case.get("expected_issues", [])
            ).with_inputs("code", "language")

            examples.append(example)

        return examples

    def evaluate_module(
        self,
        module: dspy.Module,
        test_data_path: str
    ) -> Dict[str, Any]:
        """
        Evaluate a module on test data.

        Args:
            module: The DSPy module to evaluate
            test_data_path: Path to test data

        Returns:
            Dictionary with evaluation results
        """
        test_data = load_json(test_data_path)
        results = []

        print(f"📊 Evaluating on {len(test_data.get('test_cases', []))} test cases...")

        for case in test_data.get("test_cases", []):
            code = read_code_file(case["file_path"])
            language = case["language"]

            # Run module
            prediction = module(code=code, language=language)

            # Create expected format
            expected_issues = []
            # We need to load from training data for this case
            # For now, simplified
            expected_issues = self._get_expected_for_test_case(case["id"])

            # Evaluate
            eval_result = self.evaluator.evaluate(
                predicted_issues=self._parse_prediction(prediction),
                expected_issues=expected_issues
            )

            results.append({
                "test_id": case["id"],
                "precision": eval_result.precision,
                "recall": eval_result.recall,
                "f1_score": eval_result.f1_score,
                "critical_recall": eval_result.critical_recall,
                "overall_score": eval_result.overall_score
            })

        # Aggregate results
        avg_results = {
            "average_precision": sum(r["precision"] for r in results) / len(results),
            "average_recall": sum(r["recall"] for r in results) / len(results),
            "average_f1": sum(r["f1_score"] for r in results) / len(results),
            "average_critical_recall": sum(r["critical_recall"] for r in results) / len(results),
            "average_overall": sum(r["overall_score"] for r in results) / len(results),
            "individual_results": results
        }

        return avg_results

    def _parse_prediction(self, prediction: dspy.Prediction) -> List[Dict]:
        """Parse prediction into list of issues."""
        if hasattr(prediction, 'issues'):
            issues = prediction.issues

            # If it's a string, try to parse as JSON
            if isinstance(issues, str):
                try:
                    return json.loads(issues)
                except:
                    # Try to extract issues from text
                    return self._extract_issues_from_text(issues)

            return issues if isinstance(issues, list) else []

        return []

    def _extract_issues_from_text(self, text: str) -> List[Dict]:
        """Extract issues from free-form text output."""
        # Simplified extraction - real implementation would be more robust
        issues = []
        # This is a placeholder - you'd implement proper parsing
        return issues

    def _get_expected_for_test_case(self, test_id: str) -> List[Dict]:
        """Get expected issues for a test case."""
        # Map test case to training data
        # Simplified for this example
        for case in self.training_data.get("training_cases", []):
            if case["file_path"] in test_id:
                return case.get("expected_issues", [])
        return []

    def export_to_skill_md(
        self,
        module: dspy.Module,
        output_path: str,
        include_examples: bool = True
    ):
        """
        Export optimized module to Skill.md format.

        Args:
            module: Optimized module
            output_path: Where to save the skill
            include_examples: Whether to include few-shot examples
        """
        print(f"📝 Exporting optimized skill to {output_path}...")

        # Extract examples if using FewShot
        examples = []
        if include_examples and hasattr(module, 'demos'):
            examples = module.demos

        # Convert to markdown
        skill_md = module_to_skill_prompt(module, examples)

        # Save
        Path(output_path).write_text(skill_md)

        print("✅ Skill exported!")

    def compare_baseline_vs_optimized(
        self,
        optimized_module: dspy.Module,
        test_data_path: str
    ) -> Dict[str, Any]:
        """
        Compare baseline skill against optimized version.

        Args:
            optimized_module: The optimized module
            test_data_path: Test data path

        Returns:
            Comparison results
        """
        print("📊 Comparing baseline vs optimized...")

        # For baseline, we'd need to run Claude with original skill
        # For this example, we'll just evaluate the optimized version

        optimized_results = self.evaluate_module(optimized_module, test_data_path)

        comparison = {
            "optimized": optimized_results,
            "improvement_summary": "Baseline comparison requires Claude API integration"
        }

        return comparison

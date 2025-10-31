"""
Evaluation interface for security and functionality testing.

⚠️ OWNERSHIP: Kush implements these classes
⚠️ USAGE: Rohit's training loop calls these for validation

DO NOT modify interface signatures without team coordination!
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from data.schemas import GeneratedCode


class BaseSecurityEvaluator(ABC):
    """
    Base interface for security evaluation (CodeQL).
    
    Kush implements:
    - CodeQLEvaluator
    - PythonSecurityChecker
    - JavaSecurityChecker
    - CppSecurityChecker
    
    Rohit uses:
    - In training/train.py for validation after each epoch
    - To compute Security Rate metric
    """
    
    @abstractmethod
    def analyze_code(self, code: str, language: str) -> List[str]:
        """
        Analyze code for security vulnerabilities.
        
        Args:
            code: Source code to analyze
            language: Programming language ("python", "java", "cpp")
            
        Returns:
            List of CWE IDs found (e.g., ["CWE-089", "CWE-022"])
            Empty list if no vulnerabilities found
            
        Example:
            >>> evaluator = CodeQLEvaluator()
            >>> cwe_list = evaluator.analyze_code("SELECT * FROM users WHERE id = " + user_input, "python")
            >>> print(cwe_list)  # ["CWE-089"]
        """
        pass
    
    @abstractmethod
    def compute_security_rate(self, generated_codes: List[GeneratedCode]) -> float:
        """
        Compute Security Rate: % of code without vulnerabilities.
        
        Args:
            generated_codes: List of GeneratedCode objects to evaluate
            
        Returns:
            Security rate as percentage (0.0 to 100.0)
            
        Example:
            >>> codes = [model.generate(prompt) for prompt in test_prompts]
            >>> security_rate = evaluator.compute_security_rate(codes)
            >>> print(f"Security Rate: {security_rate}%")
        """
        pass


class BaseFunctionalEvaluator(ABC):
    """
    Base interface for functional correctness evaluation (HumanEval).
    
    Kush implements:
    - HumanEvalRunner
    
    Rohit uses:
    - In training/train.py for validation
    - To compute Pass@k metric
    """
    
    @abstractmethod
    def run_humaneval(
        self,
        generated_codes: List[str],
        k_values: List[int] = [1, 10, 100]
    ) -> Dict[str, float]:
        """
        Run HumanEval benchmark and compute Pass@k.
        
        Args:
            generated_codes: List of generated code solutions
            k_values: Values of k for Pass@k metric
            
        Returns:
            Dictionary mapping k to pass rate:
            {"pass@1": 0.65, "pass@10": 0.82, "pass@100": 0.91}
            
        Example:
            >>> evaluator = HumanEvalRunner()
            >>> codes = [model.generate(problem.prompt) for problem in humaneval_problems]
            >>> results = evaluator.run_humaneval(codes, k_values=[1, 10])
        """
        pass
    
    @abstractmethod
    def test_single_solution(self, code: str, test_cases: List[Dict]) -> bool:
        """
        Test a single code solution against test cases.
        
        Args:
            code: Generated code to test
            test_cases: List of test case dicts with 'input' and 'expected_output'
            
        Returns:
            True if all test cases pass, False otherwise
        """
        pass


class EvaluationMetrics:
    """
    Container for evaluation metrics.
    
    Both Rohit and Kush use this to store/report results.
    """
    
    def __init__(
        self,
        security_rate: Optional[float] = None,
        pass_at_k: Optional[Dict[str, float]] = None,
        total_vulnerabilities: Optional[int] = None,
        cwe_breakdown: Optional[Dict[str, int]] = None
    ):
        self.security_rate = security_rate
        self.pass_at_k = pass_at_k or {}
        self.total_vulnerabilities = total_vulnerabilities
        self.cwe_breakdown = cwe_breakdown or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/saving"""
        return {
            "security_rate": self.security_rate,
            "pass_at_k": self.pass_at_k,
            "total_vulnerabilities": self.total_vulnerabilities,
            "cwe_breakdown": self.cwe_breakdown
        }
    
    def __str__(self) -> str:
        """Pretty print metrics"""
        lines = ["Evaluation Metrics:"]
        if self.security_rate is not None:
            lines.append(f"  Security Rate: {self.security_rate:.2f}%")
        if self.pass_at_k:
            for k, rate in self.pass_at_k.items():
                lines.append(f"  {k}: {rate:.2f}%")
        if self.total_vulnerabilities is not None:
            lines.append(f"  Total Vulnerabilities: {self.total_vulnerabilities}")
        return "\n".join(lines)

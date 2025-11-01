"""
Shared data schemas for SVEN project.

⚠️ CRITICAL: These schemas are the contract between Rohit and Kush's code.
DO NOT modify without team discussion and coordination!

Usage:
    from sven_data.schemas import VulnerabilityPair, DatasetConfig
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"


class CWE(Enum):
    """Common Weakness Enumeration types we're targeting"""
    SQL_INJECTION = "CWE-089"
    PATH_TRAVERSAL = "CWE-022"
    BUFFER_OVERFLOW = "CWE-787"


@dataclass
class VulnerabilityPair:
    """
    Standard format for vulnerability-fix pairs.
    
    This is consumed by:
    - Rohit's training loop (training/train.py)
    - Kush's evaluation pipeline (evaluation/security_rate.py)
    
    Produced by:
    - Kush's dataset loaders (sven_data/big_vul.py, sven_data/cross_vul.py, etc.)
    """
    vulnerable_code: str          # Code WITH vulnerability
    fixed_code: str               # Code AFTER security fix
    diff_mask: List[int]          # Token indices that changed (1=changed, 0=same)
    cwe_id: str                   # e.g., "CWE-089"
    language: str                 # "python", "java", or "cpp"
    
    # Optional metadata
    commit_id: Optional[str] = None
    repo_name: Optional[str] = None
    file_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields"""
        assert self.vulnerable_code, "vulnerable_code cannot be empty"
        assert self.fixed_code, "fixed_code cannot be empty"
        assert len(self.diff_mask) > 0, "diff_mask must have at least one element"
        assert self.language in ["python", "java", "cpp"], f"Invalid language: {self.language}"


@dataclass
class GeneratedCode:
    """
    Output from the model generation.
    
    Produced by:
    - Rohit's prefix-tuned model (models/codegen_wrapper.py)
    
    Consumed by:
    - Kush's evaluation (evaluation/security_rate.py, evaluation/humaneval.py)
    - Kush's webapp (webapp/app.py)
    """
    code: str                     # Generated code snippet
    is_secure_mode: bool          # True if generated with secure prefix, False for vulnerable
    prompt: str                   # Original prompt used
    language: str                 # Programming language
    
    # Evaluation results (filled by evaluation pipeline)
    security_violations: Optional[List[str]] = None  # List of CWE IDs found by CodeQL
    is_functionally_correct: Optional[bool] = None   # HumanEval pass/fail
    

@dataclass
class DatasetConfig:
    """
    Configuration for dataset loading.
    
    Used by:
    - Kush's dataset loaders
    """
    name: str                     # "big_vul", "cross_vul", "vudenc"
    language: str                 # Filter by language
    split: str                    # "train", "val", "test"
    max_samples: Optional[int] = None
    filter_cwe: Optional[List[str]] = None  # Only include specific CWEs


@dataclass
class ModelOutput:
    """
    Standard output from prefix-tuned model.
    
    Produced by:
    - Rohit's SecurePrefixTuning.generate()
    
    Consumed by:
    - Training evaluation
    - Webapp demo
    """
    generated_tokens: List[int]   # Token IDs
    generated_text: str           # Decoded text
    logits: Optional[Any] = None  # For loss computation
    prefix_embeddings: Optional[Any] = None  # The prefix vectors used


# Version tracking - increment when schema changes
SCHEMA_VERSION = "1.0.0"

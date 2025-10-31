"""
Model interface for prefix-tuned code generation.

⚠️ OWNERSHIP: Rohit implements these classes
⚠️ USAGE: Kush's evaluation and webapp use these

DO NOT modify interface signatures without team coordination!
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import torch
from data.schemas import GeneratedCode, ModelOutput


class BasePrefixModel(ABC):
    """
    Base interface for prefix-tuned code generation models.
    
    Rohit implements:
    - SecurePrefixTuning
    - VulnerablePrefixTuning (for contrastive learning)
    - CodeGenWrapper (base model wrapper)
    
    Kush uses:
    - In evaluation/security_rate.py to generate code for testing
    - In webapp/app.py to demonstrate secure vs vulnerable generation
    """
    
    @abstractmethod
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """
        Load trained prefix vectors from checkpoint.
        
        Args:
            checkpoint_path: Path to .pt or .pth checkpoint file
            
        Example:
            >>> model = SecurePrefixTuning()
            >>> model.load_checkpoint("checkpoints/secure_prefix_epoch10.pt")
        """
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_length: int = 128,
        temperature: float = 0.8,
        top_p: float = 0.95,
        **kwargs
    ) -> GeneratedCode:
        """
        Generate code from prompt using prefix-tuned model.
        
        Args:
            prompt: Code prompt/context
            max_length: Max tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            GeneratedCode object with generated code and metadata
            
        Example:
            >>> model = SecurePrefixTuning()
            >>> result = model.generate("def connect_to_database(user_input):")
            >>> print(result.code)
        """
        pass
    
    @abstractmethod
    def get_prefix_embeddings(self) -> torch.Tensor:
        """
        Return the learned prefix embeddings.
        
        Returns:
            Tensor of shape [prefix_length, hidden_dim]
            
        Used for:
        - Visualization in webapp
        - Analysis of what security patterns were learned
        """
        pass
    
    @abstractmethod
    def compute_loss(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor,
        diff_mask: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Compute training losses.
        
        Args:
            input_ids: Token IDs of input code
            labels: Token IDs of target code (secure)
            diff_mask: Mask indicating changed tokens
            
        Returns:
            Dictionary with loss components:
            {
                "lm_loss": conditional language modeling loss,
                "contrastive_loss": secure vs vulnerable distinction,
                "kl_loss": KL divergence regularization,
                "total_loss": weighted sum
            }
            
        Note: This is Rohit's implementation detail, but the return format
              is needed for training monitoring/logging.
        """
        pass


class ModelRegistry:
    """
    Registry for model classes.
    
    Rohit registers models here.
    Kush loads models by name.
    """
    _models = {}
    
    @classmethod
    def register(cls, name: str, model_class: type):
        """Register a model class"""
        cls._models[name] = model_class
    
    @classmethod
    def get_model(cls, name: str, **kwargs) -> BasePrefixModel:
        """Get model instance by name"""
        if name not in cls._models:
            raise ValueError(f"Unknown model: {name}. Available: {list(cls._models.keys())}")
        return cls._models[name](**kwargs)


# Model configuration (shared constants)
class ModelConfig:
    """Shared model configuration constants"""
    
    # CodeGen variants
    CODEGEN_350M = "Salesforce/codegen-350M-mono"
    CODEGEN_2B7 = "Salesforce/codegen-2B7-mono"
    
    # Default hyperparameters (Rohit can override in training.yaml)
    DEFAULT_PREFIX_LENGTH = 20
    DEFAULT_PREFIX_HIDDEN_DIM = 512
    DEFAULT_MAX_SEQ_LENGTH = 512

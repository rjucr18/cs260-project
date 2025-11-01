"""
Dataset loader interface.

⚠️ OWNERSHIP: Kush implements these classes
⚠️ USAGE: Rohit's training code imports and uses these

DO NOT modify interface signatures without team coordination!
"""

from abc import ABC, abstractmethod
from typing import List, Iterator
from sven_data.schemas import VulnerabilityPair, DatasetConfig


class BaseDatasetLoader(ABC):
    """
    Base class for all dataset loaders.
    
    Kush implements:
    - BigVulDataset
    - CrossVulDataset  
    - VUDENCDataset
    
    Rohit uses:
    - In training/train.py to load vulnerability pairs
    """
    
    @abstractmethod
    def load(self, config: DatasetConfig) -> List[VulnerabilityPair]:
        """
        Load dataset and return vulnerability pairs.
        
        Args:
            config: Dataset configuration (language, split, etc.)
            
        Returns:
            List of VulnerabilityPair objects
        """
        pass
    
    @abstractmethod
    def get_iterator(self, config: DatasetConfig, batch_size: int) -> Iterator[List[VulnerabilityPair]]:
        """
        Return iterator for batched loading (memory efficient).
        """
        pass
    
    @abstractmethod
    def apply_diff_masking(self, vulnerable: str, fixed: str) -> List[int]:
        """
        Compute diff mask between vulnerable and fixed code.
        """
        pass


class DatasetRegistry:
    """Registry for dataset loaders."""
    _loaders = {}
    
    @classmethod
    def register(cls, name: str, loader_class: type):
        cls._loaders[name] = loader_class
    
    @classmethod
    def get_loader(cls, name: str) -> BaseDatasetLoader:
        if name not in cls._loaders:
            raise ValueError(f"Unknown dataset: {name}. Available: {list(cls._loaders.keys())}")
        return cls._loaders[name]()

"""
BigVul dataset loader with diff-based masking.

⚠️ OWNERSHIP: Kush (data pipeline)
This is a scaffold implementation - Kush will add real data loading logic.
"""
from typing import List, Iterator
import difflib
from sven_data.interfaces import BaseDatasetLoader, DatasetRegistry
from sven_data.schemas import VulnerabilityPair, DatasetConfig


class BigVulDataset(BaseDatasetLoader):
    """Loader for Big-Vul dataset"""
    
    def __init__(self):
        self.data_dir = "data/big_vul"
        self._cached_data = None
    
    def load(self, config: DatasetConfig) -> List[VulnerabilityPair]:
        """
        Load Big-Vul dataset.
        
        TODO (Kush): Implement actual data loading from Big-Vul source
        - Download/extract dataset if not present
        - Filter by language and CWE if specified
        - Clean and deduplicate
        - Apply split (train/val/test)
        """
        # Placeholder: return empty list for now
        # Kush will implement with actual Big-Vul data
        print(f"[BigVul] Loading {config.split} split for {config.language}")
        return []
    
    def get_iterator(self, config: DatasetConfig, batch_size: int) -> Iterator[List[VulnerabilityPair]]:
        """
        Memory-efficient iterator for batched loading.
        
        TODO (Kush): Implement streaming from disk to avoid loading all data
        """
        data = self.load(config)
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]
    
    def apply_diff_masking(self, vulnerable: str, fixed: str) -> List[int]:
        """
        Compute token-level diff mask between vulnerable and fixed code.
        
        Returns binary mask where 1 = token changed, 0 = unchanged.
        This helps focus training on security-critical regions.
        
        Algorithm:
        1. Tokenize both strings (by whitespace for simplicity)
        2. Run difflib sequence matching
        3. Mark changed/added/removed tokens as 1, kept tokens as 0
        """
        # Simple whitespace tokenization
        # TODO (Kush): Use proper tokenizer matching the model
        vuln_tokens = vulnerable.split()
        fixed_tokens = fixed.split()
        
        # Use difflib to find matching blocks
        matcher = difflib.SequenceMatcher(None, vuln_tokens, fixed_tokens)
        
        # Initialize mask (all changed by default)
        mask = [1] * len(vuln_tokens)
        
        # Mark unchanged tokens as 0
        for block in matcher.get_matching_blocks():
            vuln_start, fixed_start, size = block
            for i in range(size):
                if vuln_start + i < len(mask):
                    mask[vuln_start + i] = 0
        
        return mask


class CrossVulDataset(BaseDatasetLoader):
    """Loader for CrossVul dataset (cross-language vulnerabilities)"""
    
    def __init__(self):
        self.data_dir = "data/cross_vul"
    
    def load(self, config: DatasetConfig) -> List[VulnerabilityPair]:
        """TODO (Kush): Implement CrossVul loading"""
        print(f"[CrossVul] Loading {config.split} split for {config.language}")
        return []
    
    def get_iterator(self, config: DatasetConfig, batch_size: int) -> Iterator[List[VulnerabilityPair]]:
        """TODO (Kush): Implement iterator"""
        data = self.load(config)
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]
    
    def apply_diff_masking(self, vulnerable: str, fixed: str) -> List[int]:
        """Reuse BigVul's diff masking logic"""
        loader = BigVulDataset()
        return loader.apply_diff_masking(vulnerable, fixed)


class VUDENCDataset(BaseDatasetLoader):
    """Loader for VUDENC dataset"""
    
    def __init__(self):
        self.data_dir = "data/vudenc"
    
    def load(self, config: DatasetConfig) -> List[VulnerabilityPair]:
        """TODO (Kush): Implement VUDENC loading"""
        print(f"[VUDENC] Loading {config.split} split for {config.language}")
        return []
    
    def get_iterator(self, config: DatasetConfig, batch_size: int) -> Iterator[List[VulnerabilityPair]]:
        """TODO (Kush): Implement iterator"""
        data = self.load(config)
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]
    
    def apply_diff_masking(self, vulnerable: str, fixed: str) -> List[int]:
        """Reuse BigVul's diff masking logic"""
        loader = BigVulDataset()
        return loader.apply_diff_masking(vulnerable, fixed)


# Register datasets
DatasetRegistry.register("big_vul", BigVulDataset)
DatasetRegistry.register("cross_vul", CrossVulDataset)
DatasetRegistry.register("vudenc", VUDENCDataset)

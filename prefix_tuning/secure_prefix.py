"""
Secure/Vulnerable Prefix-Tuning modules for SVEN (Week 1 scaffolding)

These classes own the learnable prefix embeddings and simple save/load helpers.
They do not implement the full training logic yet; that is wired via the model wrapper.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn


@dataclass
class PrefixConfig:
    prefix_length: int = 20
    hidden_dim: int = 512
    init: str = "random"  # or "vocab" in future


class BasePrefixTuning(nn.Module):
    """Base class for learnable prefix vectors."""

    def __init__(self, config: PrefixConfig):
        super().__init__()
        self.config = config
        # Learnable prefix embeddings [prefix_length, hidden_dim]
        self.prefix = nn.Parameter(
            torch.randn(config.prefix_length, config.hidden_dim) * 0.02
        )

    @torch.no_grad()
    def get_prefix_embeddings(self) -> torch.Tensor:
        """Return the current prefix embeddings."""
        return self.prefix.detach()

    def forward(self) -> torch.Tensor:  # noqa: D401
        """Alias for get_prefix_embeddings so it can be called in forward graphs."""
        return self.prefix

    def save(self, path: str) -> None:
        torch.save({"state_dict": self.state_dict(), "config": self.config.__dict__}, path)

    @classmethod
    def load(cls, path: str) -> "BasePrefixTuning":
        ckpt = torch.load(path, map_location="cpu")
        cfg = PrefixConfig(**ckpt.get("config", {}))
        obj = cls(cfg)
        obj.load_state_dict(ckpt["state_dict"])  # type: ignore[index]
        return obj


class SecurePrefixTuning(BasePrefixTuning):
    """Prefix meant to bias towards secure code generation."""

    pass


class VulnerablePrefixTuning(BasePrefixTuning):
    """Prefix meant to bias towards intentionally vulnerable code (for contrastive)."""

    pass

"""
Minimal Trainer scaffolding (Week 1).
- Supports dry-run to validate plumbing without datasets.
- Uses BasePrefixModel interface; dataset loaders will plug in during Week 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]

from models.codegen_wrapper import CodeGenWrapper
from models.interfaces import BasePrefixModel


@dataclass
class TrainerConfig:
    num_epochs: int = 1
    dry_run: bool = True


class Trainer:
    def __init__(self, model: BasePrefixModel, config: TrainerConfig):
        self.model = model
        self.cfg = config

    def train(self) -> None:
        if self.cfg.dry_run:
            # Just perform a quick generation to make sure stack is wired
            sample = self.model.generate("def add(a, b):\n    return a + b\n")
            print("[DRY-RUN] Sample generation (first 120 chars):\n", sample.code[:120])
            return

        # Placeholder training loop (no real data yet)
        for epoch in range(self.cfg.num_epochs):
            print(f"Epoch {epoch+1}/{self.cfg.num_epochs}")
            # Fake tensors to exercise compute_loss API
            if torch is None:
                losses = {"total_loss": 0.0}
            else:
                input_ids = torch.randint(0, 100, (1, 32))
                labels = torch.randint(0, 100, (1, 32))
                diff_mask = torch.zeros_like(input_ids)
                losses = self.model.compute_loss(input_ids, labels, diff_mask)
            print("Losses:", {k: (float(v) if hasattr(v, "item") else v) for k, v in losses.items()})

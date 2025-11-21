"""
Trainer with three-loss SVEN objective and AMP support.
- Supports dry-run, timing-only, and full training modes
- Uses batch-based interface with diff masking
- Enables mixed precision (AMP) for T4 GPUs
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import json
from pathlib import Path
import random
import numpy as np

try:
    import torch
    import torch.cuda.amp as amp
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]
    amp = None  # type: ignore[assignment]

from models.codegen_wrapper import CodeGenWrapper
from models.interfaces import BasePrefixModel


@dataclass
class TrainerConfig:
    num_epochs: int = 1
    dry_run: bool = True
    steps: int = 0  # if >0 overrides epochs
    timing_only: bool = False
    output_dir: str = "logs"
    learning_rate: float = 5e-3
    batch_size: int = 8
    max_grad_norm: float = 1.0
    amp_enabled: bool = True  # Mixed precision for T4
    seed: int = 42
    loss_weights: Optional[Dict[str, float]] = None


class Trainer:
    def __init__(self, model: BasePrefixModel, config: TrainerConfig):
        self.model = model
        self.cfg = config

    def _ensure_output_dir(self):
        Path(self.cfg.output_dir).mkdir(parents=True, exist_ok=True)

    def _parameter_report(self) -> Dict[str, Any]:
        """Return lightweight parameter counts without relying on interface internals.

        Uses duck-typing: only accesses attributes that actually exist on concrete implementation.
        """
        if torch is None:
            return {"error": "torch_not_available"}
        report: Dict[str, Any] = {}
        prefix_module = getattr(self.model, "prefix_module", None)
        if prefix_module is not None:
            prefix_params = sum(p.numel() for p in prefix_module.parameters())
            report["prefix_params"] = prefix_params
        base = getattr(self.model, "_model", None)
        if base is not None:
            total_trainable = sum(p.numel() for p in base.parameters() if p.requires_grad)
            report["base_trainable_params"] = total_trainable
        return report

    def train(self) -> None:
        self._ensure_output_dir()
        metrics_path = Path(self.cfg.output_dir) / "metrics.json"
        
        # Set seed for reproducibility
        if self.cfg.seed is not None:
            self._set_seed(self.cfg.seed)

        if self.cfg.dry_run:
            sample = self.model.generate("def add(a, b):\n    return a + b\n")
            print("[DRY-RUN] Sample generation (first 120 chars):\n", sample.code[:120])
            report = {"mode": "dry_run", "sample_head": sample.code[:120]}
            metrics_path.write_text(json.dumps(report, indent=2))
            return

        # Setup optimizer and scaler
        if torch is None:
            print("[WARNING] torch not available, running in stub mode")
            return
        
        # Only train prefix parameters
        prefix_params = list(self.model.prefix_module.parameters())
        optimizer = torch.optim.AdamW(prefix_params, lr=self.cfg.learning_rate)
        scaler = amp.GradScaler() if self.cfg.amp_enabled and amp is not None else None
        
        # Freeze base model
        if hasattr(self.model, '_model') and self.model._model is not None:
            for param in self.model._model.parameters():
                param.requires_grad = False
            print(f"[TRAIN] Frozen base model, training {sum(p.numel() for p in prefix_params)} prefix params")
        
        steps_target = self.cfg.steps if self.cfg.steps > 0 else self.cfg.num_epochs
        timing: Dict[str, Any] = {"step_times": [], "losses": []}

        for idx in range(steps_target):
            start = time.perf_counter()
            
            # Create dummy batch (TODO: replace with real data loader)
            batch = {
                "input_ids": torch.randint(0, 100, (self.cfg.batch_size, 32)),
                "labels": torch.randint(0, 100, (self.cfg.batch_size, 32)),
                "diff_mask": torch.randint(0, 2, (self.cfg.batch_size, 32))
            }
            
            # Forward + backward with AMP
            optimizer.zero_grad()
            
            if scaler is not None:
                with amp.autocast():
                    losses = self.model.compute_loss(batch, self.cfg.loss_weights)
                    loss_tensor = losses.get("total_loss_tensor", torch.tensor(losses["total_loss"]))
                scaler.scale(loss_tensor).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(prefix_params, self.cfg.max_grad_norm)
                scaler.step(optimizer)
                scaler.update()
            else:
                losses = self.model.compute_loss(batch, self.cfg.loss_weights)
                loss_tensor = losses.get("total_loss_tensor", torch.tensor(losses["total_loss"]))
                if loss_tensor.requires_grad:
                    loss_tensor.backward()
                    torch.nn.utils.clip_grad_norm_(prefix_params, self.cfg.max_grad_norm)
                    optimizer.step()
            
            elapsed = time.perf_counter() - start
            timing["step_times"].append(elapsed)
            timing["losses"].append({
                "lm": losses["lm_loss"],
                "contrastive": losses["contrastive_loss"],
                "kl": losses["kl_loss"],
                "total": losses["total_loss"]
            })
            
            if idx % 10 == 0:
                print(f"Step {idx+1}/{steps_target} "
                      f"LM={losses['lm_loss']:.4f} "
                      f"Contrast={losses['contrastive_loss']:.4f} "
                      f"KL={losses['kl_loss']:.4f} "
                      f"Total={losses['total_loss']:.4f} "
                      f"time={elapsed:.3f}s")
            
            if self.cfg.timing_only:
                continue
                
        summary = {
            "mode": "timing_only" if self.cfg.timing_only else "train",
            "steps": steps_target,
            "avg_step_time": (sum(timing["step_times"]) / len(timing["step_times"])) if timing["step_times"] else 0,
            "final_losses": timing["losses"][-1] if timing["losses"] else {},
            "parameter_report": self._parameter_report(),
            "amp_enabled": self.cfg.amp_enabled,
            "seed": self.cfg.seed
        }
        metrics_path.write_text(json.dumps(summary, indent=2))
        print(f"[METRICS] Saved to {metrics_path}")
    
    def _set_seed(self, seed: int):
        """Set random seeds for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        if torch is not None:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)

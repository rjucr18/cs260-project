"""
Minimal Trainer scaffolding (Week 1).
- Supports dry-run to validate plumbing without datasets.
- Uses BasePrefixModel interface; dataset loaders will plug in during Week 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
import time
import json
from pathlib import Path

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
    steps: int = 0  # if >0 overrides epochs
    timing_only: bool = False
    output_dir: str = "logs"


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

        if self.cfg.dry_run:
            sample = self.model.generate("def add(a, b):\n    return a + b\n")
            print("[DRY-RUN] Sample generation (first 120 chars):\n", sample.code[:120])
            report = {"mode": "dry_run", "sample_head": sample.code[:120]}
            metrics_path.write_text(json.dumps(report, indent=2))
            return

        steps_target = self.cfg.steps if self.cfg.steps > 0 else self.cfg.num_epochs
        use_steps = self.cfg.steps > 0
        timing: Dict[str, Any] = {"step_times": []}

        for idx in range(steps_target):
            start = time.perf_counter()
            if torch is None:
                losses = {"total_loss": 0.0}
            else:
                input_ids = torch.randint(0, 100, (1, 32))
                labels = torch.randint(0, 100, (1, 32))
                diff_mask = torch.zeros_like(input_ids)
                losses = self.model.compute_loss(input_ids, labels, diff_mask)
            elapsed = time.perf_counter() - start
            timing["step_times"].append(elapsed)
            if idx % 10 == 0:
                print(f"Step {idx+1}/{steps_target} total_loss={losses['total_loss']} time={elapsed:.3f}s")
            if self.cfg.timing_only:
                continue
        summary = {
            "mode": "timing_only" if self.cfg.timing_only else "train_stub",
            "steps": steps_target,
            "avg_step_time": (sum(timing["step_times"]) / len(timing["step_times"])) if timing["step_times"] else 0,
            "parameter_report": self._parameter_report(),
        }
        metrics_path.write_text(json.dumps(summary, indent=2))
        print(f"[METRICS] Saved to {metrics_path}")

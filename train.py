"""
CLI runner for training scaffolding (Week 1).
- Loads configs/training.yaml
- Initializes CodeGenWrapper + SecurePrefixTuning
- Supports --dry-run to validate setup without datasets or downloads
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from models.codegen_wrapper import CodeGenWrapper
from training.train import Trainer, TrainerConfig


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SVEN Training Runner (Week 1)")
    p.add_argument("--config", type=str, default="configs/training.yaml", help="Path to training config YAML")
    p.add_argument("--dry-run", action="store_true", help="Run without loading datasets or training")
    p.add_argument("--model", type=str, default="Salesforce/codegen-350M-mono", help="HF model name")
    return p.parse_args()


def load_cfg(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    args = parse_args()
    cfg = load_cfg(args.config)

    model = CodeGenWrapper(
        model_name=args.model,
        secure=True,
        prefix_length=cfg.get("model", {}).get("prefix_length", 20),
        prefix_hidden_dim=cfg.get("model", {}).get("prefix_hidden_dim", 512),
        lazy_load=True,
    )

    trainer = Trainer(model=model, config=TrainerConfig(num_epochs=cfg.get("training", {}).get("num_epochs", 1), dry_run=args.dry_run or True))
    trainer.train()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

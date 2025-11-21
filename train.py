"""CLI runner for SVEN training."""
from __future__ import annotations

import argparse
import yaml

from models.codegen_wrapper import CodeGenWrapper
from training.train import Trainer, TrainerConfig


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="SVEN Training Runner")
    p.add_argument("--config", type=str, default="configs/python.yaml", help="Path to training config YAML")
    p.add_argument("--dry-run", action="store_true", help="Run without training")
    p.add_argument("--steps", type=int, default=0, help="Number of training steps (0 = use epochs)")
    p.add_argument("--timing-only", action="store_true", help="Run timing loop only")
    return p.parse_args()


def load_cfg(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    args = parse_args()
    cfg = load_cfg(args.config)

    model = CodeGenWrapper(
        model_name=cfg.get("model", {}).get("name", "Salesforce/codegen-350M-mono"),
        secure=True,
        prefix_length=cfg.get("model", {}).get("prefix_length", 20),
        lazy_load=True,
    )

    trainer = Trainer(
        model=model,
        config=TrainerConfig(
            num_epochs=cfg.get("training", {}).get("num_epochs", 1),
            dry_run=args.dry_run,
            steps=args.steps,
            timing_only=args.timing_only,
            learning_rate=cfg.get("training", {}).get("learning_rate", 5e-3),
            batch_size=cfg.get("training", {}).get("batch_size", 8),
            amp_enabled=cfg.get("training", {}).get("amp_enabled", True),
            seed=cfg.get("model", {}).get("seed", 42),
            loss_weights=cfg.get("loss_weights"),
        ),
    )
    trainer.train()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

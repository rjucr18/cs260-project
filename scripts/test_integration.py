"""
Quick integration test (safe to run without heavy dependencies):
- Imports model wrapper and runs a dry-run generation
- Verifies Trainer can be constructed
Run: python scripts/test_integration.py
"""
from pathlib import Path
import sys

# Ensure project root is on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.codegen_wrapper import CodeGenWrapper
from training.train import Trainer, TrainerConfig


def main():
    model = CodeGenWrapper(lazy_load=True)  # transformers import is optional
    trainer = Trainer(model=model, config=TrainerConfig(dry_run=True))
    trainer.train()


if __name__ == "__main__":
    main()

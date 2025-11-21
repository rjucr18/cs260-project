"""Quick integration test."""
from models.codegen_wrapper import CodeGenWrapper
from training.train import Trainer, TrainerConfig


def main():
    model = CodeGenWrapper(lazy_load=True)
    trainer = Trainer(model=model, config=TrainerConfig(dry_run=True))
    trainer.train()


if __name__ == "__main__":
    main()

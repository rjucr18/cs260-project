# training

Training loop logic for optimizing prefix parameters under the three-loss SVEN objective.

Contents:
- `train.py`: Implements `Trainer` class handling batching, optimizer setup (AdamW over prefix params only), AMP mixed precision, loss logging, gradient clipping.
- `__init__.py`: Exposes Trainer for external imports.

Core Responsibilities:
- Freezes all base model parameters and filters optimizer parameter list to prefix module.
- Applies composite loss from model wrapper: conditional LM + contrastive + KL preservation.
- Handles device placement, seeding, and optional AMP for GPU efficiency.

Workflow:
1. Load config (YAML in `configs/`).
2. Instantiate `CodeGenWrapper` (secure or vulnerable).
3. Iterate batches from dataset loader (pending full implementation in `sven_data`).
4. Backprop only through prefix tensors.

Extensibility:
- Add schedulers, gradient accumulation, or distributed training here.
- Ensure new features do not unfreeze backbone inadvertently.

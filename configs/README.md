# configs

YAML configuration files specifying training hyperparameters and experiment settings per language or run type.

Example (`python.yaml`):
- `learning_rate`: Optimizer step size for prefix parameters.
- `batch_size`: Training batch size.
- `prefix_hidden_dim`: Must match backbone embedding dim (1024 for CodeGen-350M) to avoid projection overhead.
- `amp_enabled`: Toggle mixed precision for GPU efficiency.
- `seed`: Ensures reproducibility across runs.

Usage:
```
python train.py --config configs/python.yaml
```

Add new configs for other languages (e.g., `java.yaml`, `cpp.yaml`) using consistent keys.

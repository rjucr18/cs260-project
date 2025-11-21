# checkpoints

Stores trained prefix parameter snapshots and minimal metadata.

Contents:
- Prefix-only weights (tiny compared to backbone) saved periodically or at end of training.
- Optional training metadata JSON (epoch, loss metrics, config hash).

Guidelines:
- Do NOT save full base model (frozen backbone is pulled from Hugging Face on demand).
- Name convention: `prefix-secure-<timestamp>.pt`, `prefix-vulnerable-<timestamp>.pt`.
- Use `.gitignore` to exclude large or numerous files; commit only intentionally shared reference checkpoints.

Restoring:
```python
wrapper.load_checkpoint("checkpoints/prefix-secure-20231121.pt")
```

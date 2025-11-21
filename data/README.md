# data

Raw or processed dataset artifacts, intermediate caches, and manifests. This directory is intentionally kept light in source control:

Guidelines:
- Store small metadata (manifests, sample subsets) here.
- Large raw corpora (BigVul, CrossVul, VUDENC) should be downloaded via `scripts/download_datasets.py` and excluded by `.gitignore`.
- Use `.gitkeep` to retain the folder when empty.

Typical Workflow:
1. Run `python scripts/download_datasets.py --datasets big-vul crossvul vudenc`.
2. Perform cleaning + diff masking (implementation pending in `sven_data`).
3. Cache tokenized samples for faster training restarts.

Do NOT commit proprietary or large dataset dumps.

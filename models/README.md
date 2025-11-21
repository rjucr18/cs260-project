# models

Core model wrappers integrating prefix-tuning with the frozen CodeGen base models.

Contents:
- `codegen_wrapper.py`: Main wrapper implementing secure/vulnerable prefix injection, generate path, and three-loss computation (conditional LM, contrastive, KL preservation). Uses lazy loading to avoid large downloads until first use.
- `interfaces.py`: Abstract base classes (`BasePrefixModel`, `ModelConfig`) defining required API surface (generate, compute_loss, load_checkpoint).
- `__init__.py`: Exposes public symbols for cleaner imports.

Key Concepts:
- Prefix modules are the ONLY trainable parameters (parameter-efficient). Base model weights remain frozen.
- Secure vs Vulnerable modes toggle which learned prefix is injected before the prompt tokens.
- Generation path: builds `inputs_embeds` by concatenating prefix embeddings + word token embeddings; extends attention mask accordingly.
- Loss path: Accepts batch dict with `input_ids`, `labels`, `diff_mask` plus optional `vulnerable_logits` / `baseline_logits` for contrastive & KL components.

Runtime Notes:
- Uses SDPA attention when available for memory efficiency. Falls back gracefully.
- Dry-run mode returns placeholder output if transformers/torch are unavailable (enables lightweight testing environments).

When Extending:
- Add new model wrappers here (e.g., different backbone) and conform to `BasePrefixModel`.
- Keep heavy imports lazy to maintain fast CLI and test startup.

# prefix_tuning

Learnable prefix modules that inject control vectors into the frozen model. Implements the SVEN approach to steering security characteristics without modifying backbone weights.

Contents:
- `secure_prefix.py`: Defines `SecurePrefixTuning`, `VulnerablePrefixTuning`, and shared `PrefixConfig`. Each allocates a small sequence of virtual tokens (prefix_length × hidden_dim) optionally with a projection layer if mismatch.
- `__init__.py`: Re-exports classes for concise imports.

Key Concepts:
- Prefix shape matches target model embedding dimension (1024 for CodeGen-350M). Projection is only used if mismatch occurs.
- Stored as tiny parameter set (~0.1% of model size) enabling rapid training and switching modes.
- Persistence: `save()` / `load()` handles only prefix weights, not the base model.

Usage:
- Construct via `PrefixConfig(prefix_length=20, hidden_dim=1024)`.
- Call `get_prefix_embeddings()` during generation or loss computation to prepend to real tokens.

Testing:
- Unit tests in `tests/test_prefix_tuning.py` verify dimensions, gradient flow, save/load integrity, independence between secure/vulnerable variants.

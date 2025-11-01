"""
CodeGen model wrapper implementing BasePrefixModel (Week 1 scaffolding).
- Lazy loads tokenizer/model on first use to avoid heavy downloads during setup.
- Uses prefix_tuning modules to provide learnable prefixes.
- Provides a safe 'generate' path that works in dry-run mode if model isn't available.
"""
from __future__ import annotations

from typing import Dict, Any, Optional

try:
    import torch
except Exception:  # pragma: no cover - allow import without torch installed
    torch = None  # type: ignore[assignment]

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception:  # pragma: no cover
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]

from data.schemas import GeneratedCode
from models.interfaces import BasePrefixModel, ModelConfig
from prefix_tuning.secure_prefix import SecurePrefixTuning, VulnerablePrefixTuning, PrefixConfig


class CodeGenWrapper(BasePrefixModel):
    def __init__(
        self,
        model_name: str = ModelConfig.CODEGEN_350M,
        secure: bool = True,
        prefix_length: int = 20,
        prefix_hidden_dim: int = 512,
        device: Optional[str] = None,
        lazy_load: bool = True,
    ) -> None:
        self.model_name = model_name
        self.secure = secure
        self._device = device or ("cuda" if torch and hasattr(torch, "cuda") and torch.cuda.is_available() else "cpu")
        self._lazy = lazy_load
        self._model = None
        self._tokenizer = None
        cfg = PrefixConfig(prefix_length=prefix_length, hidden_dim=prefix_hidden_dim)
        self.prefix_module = SecurePrefixTuning(cfg) if secure else VulnerablePrefixTuning(cfg)

        if not self._lazy:
            self._ensure_loaded()

    # ----- BasePrefixModel API -----
    def load_checkpoint(self, checkpoint_path: str) -> None:
        # Only loads prefix (parameters are tiny). Base model stays frozen.
        self.prefix_module = SecurePrefixTuning.load(checkpoint_path) if self.secure else VulnerablePrefixTuning.load(checkpoint_path)

    def generate(
        self,
        prompt: str,
        max_length: int = 128,
        temperature: float = 0.8,
        top_p: float = 0.95,
        language: str = "python",
        **kwargs,
    ) -> GeneratedCode:
        # Dry-run path if transformers/torch not installed yet
        if AutoModelForCausalLM is None or AutoTokenizer is None or torch is None:
            return GeneratedCode(
                code=f"# [DRY RUN] Generated placeholder for: {prompt}\npass\n",
                is_secure_mode=self.secure,
                prompt=prompt,
                language=language,
            )

        self._ensure_loaded()
        assert self._model is not None and self._tokenizer is not None

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)
        # NOTE: Week 1: we are not actually injecting prefixes into attention layers yet.
        # We'll just run vanilla generation so plumbing works end-to-end.
        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id,
            )[0]
        text = self._tokenizer.decode(output_ids, skip_special_tokens=True)
        return GeneratedCode(code=text, is_secure_mode=self.secure, prompt=prompt, language=language)

    def get_prefix_embeddings(self):
        return self.prefix_module.get_prefix_embeddings()

    def compute_loss(self, input_ids, labels, diff_mask) -> Dict[str, Any]:
        # Week 1 placeholder: return zeros so Trainer can run without model wiring
        if torch is None:
            return {"lm_loss": 0.0, "contrastive_loss": 0.0, "kl_loss": 0.0, "total_loss": 0.0}
        zero = torch.tensor(0.0)
        return {"lm_loss": zero, "contrastive_loss": zero, "kl_loss": zero, "total_loss": zero}

    # ----- internals -----
    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        if AutoModelForCausalLM is None or AutoTokenizer is None:
            raise RuntimeError("transformers is not installed. Install training requirements to use the model.")
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(self.model_name)
        if torch is not None:
            self._model.to(self._device)
        self._model.eval()

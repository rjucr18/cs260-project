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

# Ensure local project packages are importable even when invoked from subdirs
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sven_data.schemas import GeneratedCode
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
        enable_prefix: bool = True,
    ) -> None:
        self.model_name = model_name
        self.secure = secure
        self.enable_prefix = enable_prefix
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

        tokenized = self._tokenizer(prompt, return_tensors="pt")
        input_ids = tokenized["input_ids"].to(self._device)
        attention_mask = tokenized["attention_mask"].to(self._device)

        # Soft prefix injection: prepend learned prefix as additional "virtual" tokens.
        if self.enable_prefix:
            prefix_embeds = self.prefix_module.get_prefix_embeddings().to(self._device)  # [P, H]
            # Expand batch dimension.
            prefix_embeds = prefix_embeds.unsqueeze(0)  # [1, P, H]
            inputs_embeds = self._model.transformer.wte(input_ids)  # CodeGen embedding layer name
            full_embeds = torch.cat([prefix_embeds, inputs_embeds], dim=1)  # [B, P+T, H]
            # Adjust attention mask: prefix tokens should be attended (set to 1)
            prefix_mask = torch.ones((attention_mask.size(0), prefix_embeds.size(1)), device=self._device, dtype=attention_mask.dtype)
            full_attention = torch.cat([prefix_mask, attention_mask], dim=1)
            generate_kwargs = {
                "inputs_embeds": full_embeds,
                "attention_mask": full_attention,
            }
        else:
            generate_kwargs = {"input_ids": input_ids, "attention_mask": attention_mask}

        with torch.no_grad():
            output_ids = self._model.generate(
                **generate_kwargs,
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

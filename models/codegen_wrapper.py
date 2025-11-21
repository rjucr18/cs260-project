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
        use_sdpa: bool = True,  # Enable SDPA for better memory efficiency
    ) -> None:
        self.model_name = model_name
        self.secure = secure
        self.enable_prefix = enable_prefix
        self.use_sdpa = use_sdpa
        self._device = device or ("cuda" if torch and hasattr(torch, "cuda") and torch.cuda.is_available() else "cpu")
        self._lazy = lazy_load
        self._model = None
        self._tokenizer = None
        # CodeGen-350M uses 1024-dim embeddings, so set prefix to match
        cfg = PrefixConfig(prefix_length=prefix_length, hidden_dim=1024)
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
        metadata = {
            "max_length": max_length,
            "temperature": temperature,
            "top_p": top_p,
            "model_name": self.model_name,
            "prefix_enabled": self.enable_prefix,
        }
        return GeneratedCode(code=text, is_secure_mode=self.secure, prompt=prompt, language=language, metadata=metadata)

    def get_prefix_embeddings(self):
        return self.prefix_module.get_prefix_embeddings()

    def compute_loss(self, batch: Dict[str, Any], loss_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Compute three-loss SVEN objective:
        1. Conditional LM loss: push model toward secure tokens on changed regions
        2. Contrastive loss: maximize difference between secure/vulnerable logits
        3. KL preservation loss: maintain behavior on unchanged regions
        
        Args:
            batch: Dict with keys 'input_ids', 'labels', 'diff_mask', 'vulnerable_ids' (optional)
            loss_weights: Optional dict with keys 'conditional_lm', 'contrastive', 'kl_divergence'
        
        Returns:
            Dict with individual losses and total_loss
        """
        if torch is None or self._model is None:
            return {"lm_loss": 0.0, "contrastive_loss": 0.0, "kl_loss": 0.0, "total_loss": 0.0}
        
        # Default weights
        weights = loss_weights or {"conditional_lm": 1.0, "contrastive": 0.5, "kl_divergence": 0.1}
        
        input_ids = batch["input_ids"].to(self._device)
        labels = batch["labels"].to(self._device)
        diff_mask = batch["diff_mask"].to(self._device)  # 1 = changed, 0 = unchanged
        
        # Ensure model is loaded
        self._ensure_loaded()
        
        # Get prefix embeddings and inject
        if self.enable_prefix:
            prefix_embeds = self.prefix_module.get_prefix_embeddings().to(self._device).unsqueeze(0)
            inputs_embeds = self._model.transformer.wte(input_ids)
            full_embeds = torch.cat([prefix_embeds, inputs_embeds], dim=1)
            
            # Extend labels and mask for prefix
            prefix_labels = torch.full((labels.size(0), prefix_embeds.size(1)), -100, 
                                      dtype=labels.dtype, device=labels.device)
            labels_with_prefix = torch.cat([prefix_labels, labels], dim=1)
            
            prefix_mask = torch.zeros((diff_mask.size(0), prefix_embeds.size(1)), 
                                     dtype=diff_mask.dtype, device=diff_mask.device)
            diff_mask_with_prefix = torch.cat([prefix_mask, diff_mask], dim=1)
        else:
            full_embeds = self._model.transformer.wte(input_ids)
            labels_with_prefix = labels
            diff_mask_with_prefix = diff_mask
        
        # Forward pass
        outputs = self._model(inputs_embeds=full_embeds, labels=labels_with_prefix)
        logits = outputs.logits
        
        # 1. Conditional LM loss on changed regions (diff_mask == 1)
        # Focus training on security-critical tokens
        lm_loss_full = torch.nn.functional.cross_entropy(
            logits[:, :-1, :].reshape(-1, logits.size(-1)),
            labels_with_prefix[:, 1:].reshape(-1),
            reduction='none'
        )
        lm_loss_full = lm_loss_full.view(labels_with_prefix.size(0), -1)
        
        # Apply diff mask (only count changed tokens)
        changed_mask = diff_mask_with_prefix[:, 1:].float()
        lm_loss = (lm_loss_full * changed_mask).sum() / (changed_mask.sum() + 1e-8)
        
        # 2. Contrastive loss (optional, requires vulnerable logits)
        # Maximize difference between secure and vulnerable predictions
        contrastive_loss = torch.tensor(0.0, device=self._device)
        if "vulnerable_logits" in batch:
            vulnerable_logits = batch["vulnerable_logits"].to(self._device)
            # Margin-based: push secure logits away from vulnerable
            margin = 1.0
            diff = torch.nn.functional.cosine_similarity(
                logits.view(-1, logits.size(-1)),
                vulnerable_logits.view(-1, vulnerable_logits.size(-1)),
                dim=-1
            )
            contrastive_loss = torch.relu(margin - diff).mean()
        
        # 3. KL preservation loss on unchanged regions (diff_mask == 0)
        # Maintain functional correctness on non-security code
        kl_loss = torch.tensor(0.0, device=self._device)
        if "baseline_logits" in batch:
            baseline_logits = batch["baseline_logits"].to(self._device)
            unchanged_mask = (1 - diff_mask_with_prefix[:, 1:]).float()
            
            # KL divergence on unchanged tokens
            kl_per_token = torch.nn.functional.kl_div(
                torch.nn.functional.log_softmax(logits[:, :-1, :], dim=-1),
                torch.nn.functional.softmax(baseline_logits[:, :-1, :], dim=-1),
                reduction='none'
            ).sum(dim=-1)
            kl_loss = (kl_per_token * unchanged_mask).sum() / (unchanged_mask.sum() + 1e-8)
        
        # Total weighted loss
        total_loss = (
            weights["conditional_lm"] * lm_loss +
            weights["contrastive"] * contrastive_loss +
            weights["kl_divergence"] * kl_loss
        )
        
        return {
            "lm_loss": lm_loss.item(),
            "contrastive_loss": contrastive_loss.item(),
            "kl_loss": kl_loss.item(),
            "total_loss": total_loss.item(),
            "total_loss_tensor": total_loss  # For backward
        }

    # ----- internals -----
    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        if AutoModelForCausalLM is None or AutoTokenizer is None:
            raise RuntimeError("transformers is not installed. Install training requirements to use the model.")
        
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Enable SDPA (memory-efficient attention) for T4 GPUs
        # Falls back to math kernel if flash not available
        model_kwargs = {}
        if self.use_sdpa and torch is not None:
            # Try to use SDPA - will use memory_efficient on T4 (Turing)
            try:
                model_kwargs["attn_implementation"] = "sdpa"
                print("[MODEL] Enabling SDPA (memory-efficient attention for T4)")
            except Exception:
                print("[MODEL] SDPA not available, using default attention")
        
        self._model = AutoModelForCausalLM.from_pretrained(self.model_name, **model_kwargs)
        
        if torch is not None:
            self._model.to(self._device)
            # Enable SDPA backend hints (prefers memory_efficient on T4)
            if self.use_sdpa and hasattr(torch.backends.cuda, 'sdp_kernel'):
                torch.backends.cuda.sdp_kernel(
                    enable_flash=True,      # Will be skipped on SM75 (T4)
                    enable_mem_efficient=True,  # Works on T4
                    enable_math=False       # Slower fallback
                )
        
        self._model.eval()

# SVEN: Secure Code Generation via Prefix‑Tuning (5‑minute talk)

## Slide 1 — Title & Team (0:30)
- Project: SVEN (Security Verification and Enhancement Network)
- Goal: Steer CodeGen to produce secure code with tiny learned prefixes
- Team: [Your names]

## Slide 2 — Problem & Motivation (0:40)
- LLMs generate code, but often with CWEs (e.g., SQLi, path traversal)
- Full fine‑tuning (350M+ params) is costly and risks forgetting
- We want parameter‑efficient steering toward secure patterns

## Slide 3 — Approach: Prefix‑Tuning (0:45)
- Train small prefix vectors (e.g., 16 tokens × 1024 dims = 16,384 params)
- Prepend to token embeddings as “virtual tokens” → steer decoding
- Keep base CodeGen frozen; swap prefixes to change modes (secure vs vulnerable)
- Why this vs LoRA: ultra‑small, fast to swap, aligns with SVEN paper

## Slide 4 — Architecture (1:00)
- Input prompt → Tokenize → Embeddings
- Concatenate: [Prefix P×H] + [Prompt T×H] → Frozen CodeGen → Output
- Two modes:
  - SecurePrefixTuning → encourages secure completions
  - VulnerablePrefixTuning → baseline/contrastive behavior

```
[SecurePrefix (16×H)] + [Prompt] → CodeGen (frozen) → Secure code
[VulnPrefix  (16×H)] + [Prompt] → CodeGen (frozen) → Risky code (for contrast)
```

## Slide 5 — Demo Result (0:45)
- Prompt: `def connect(user_input):\n    pass`
- Secure (excerpt): suggests validation/structured handling
- Vulnerable (excerpt): prints/uses raw input
- Artifact: `logs/secure_compare.json` (from Colab run)

## Slide 6 — Quick Live Demo (0:40)
- Option A (CLI):
```
python scripts/interactive_cli.py --max-length 64 --temperature 0.8
# Then type a prompt, e.g.:
# Prompt> def connect(user_input):\n    pass
```
- Option B (Web):
```
python webapp/app.py
# Open http://127.0.0.1:5000 and click Generate
```

## Slide 7 — Efficiency & Timing (0:35)
- Trainable params: ~16K (0.005% of 350M)
- Timing scaffold: `logs/metrics.json` (avg step time, parameter counts)
- Base model stays frozen → fast, safe iterations

## Slide 8 — Roadmap (0:30)
- Week 2: Integrate Big‑Vul/CrossVul; implement 3 losses:
  - Conditional LM (secure tokens on diff mask)
  - Contrastive separation (secure vs vulnerable)
  - KL preservation (don’t break functionality)
- Week 3: Train prefixes (GPU), checkpoint
- Week 4: Evaluate: CodeQL Security Rate, HumanEval Pass@k

## Slide 9 — Q&A (0:25)
- Why prefixes? Parameter‑efficient, swappable, controllable
- How measured? CodeQL CWEs↓, Pass@k ≈ baseline
- What’s trained? Only prefixes; base LLM frozen
- LoRA vs Prefix? Both PEFT; prefixes are smaller & mode‑swappable

---

## Speaker Notes / Script

1) Title (0:30)
- “We built SVEN, a parameter‑efficient way to steer a frozen CodeGen model toward secure code using tiny learned prefixes.”

2) Problem (0:40)
- “LLMs can emit vulnerable code. We want a lightweight control layer to reduce CWEs without retraining 350M+ parameters.”

3) Approach (0:45)
- “Prefix‑tuning learns a handful of vectors added as ‘virtual tokens’ before the prompt. We keep the base model frozen and just optimize these prefixes.”

4) Architecture (1:00)
- “We concatenate the learned prefix embeddings with prompt embeddings, extend attention masks, and generate. Secure vs vulnerable is just which prefix we attach.”

5) Demo Result (0:45)
- “Here’s a JSON from our Colab run: secure output shows defensive patterns; vulnerable shows raw input usage. This proves controllability end‑to‑end.”

6) Live Demo (0:40)
- “I’ll run the CLI or the small Flask app and type a prompt to show both modes in real‑time.”

7) Efficiency (0:35)
- “We train ~16K params vs 350M. Timing scaffold logs step time and counts. It’s fast and safe to iterate.”

8) Roadmap (0:30)
- “Next we plug in Big‑Vul and implement the three‑loss objective to make ‘secure’ behavior systematic, then verify via CodeQL and HumanEval.”

9) Q&A (0:25)
- “Happy to dive into why prefix over LoRA, or how CodeQL scoring works.”

---

## Slide Assets (grab quickly)
- `logs/secure_compare.json` — copy secure/vulnerable excerpts
- `logs/metrics.json` — avg_step_time, prefix_params
- Optional: screenshot `nvidia-smi` from Colab

## Backup Plan
- If model download is slow, show the JSON artifacts and run the CLI with a tiny `--max-length 32`.

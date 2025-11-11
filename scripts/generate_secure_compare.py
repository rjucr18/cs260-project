"""
Generate side-by-side code for secure vs vulnerable modes.
Usage (dry-run safe):
  python scripts/generate_secure_compare.py --prompt "def connect(user_input):" --max-length 64
"""
import argparse
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models.codegen_wrapper import CodeGenWrapper


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", type=str, required=True)
    p.add_argument("--max-length", type=int, default=64)
    p.add_argument("--output", type=str, default="logs/secure_compare.json")
    return p.parse_args()


def main():
    args = parse_args()
    # Secure
    secure = CodeGenWrapper(secure=True, lazy_load=True)
    # Vulnerable (uses a separate prefix instance)
    vulnerable = CodeGenWrapper(secure=False, lazy_load=True)

    sec = secure.generate(args.prompt, max_length=args.max_length)
    vul = vulnerable.generate(args.prompt, max_length=args.max_length)

    out = {"prompt": args.prompt, "secure": sec.code, "vulnerable": vul.code}
    Path("logs").mkdir(exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"Saved comparison to {args.output}")


if __name__ == "__main__":
    main()

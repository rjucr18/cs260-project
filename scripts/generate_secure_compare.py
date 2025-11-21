"""Generate side-by-side code for secure vs vulnerable modes."""
import argparse
from pathlib import Path
import json

from models.codegen_wrapper import CodeGenWrapper


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", type=str, required=True)
    p.add_argument("--max-length", type=int, default=64)
    p.add_argument("--output", type=str, default="logs/secure_compare.json")
    return p.parse_args()


def main():
    args = parse_args()
    
    secure = CodeGenWrapper(secure=True, lazy_load=True)
    vulnerable = CodeGenWrapper(secure=False, lazy_load=True)

    sec = secure.generate(args.prompt, max_length=args.max_length)
    vul = vulnerable.generate(args.prompt, max_length=args.max_length)

    out = {"prompt": args.prompt, "secure": sec.code, "vulnerable": vul.code}
    Path("logs").mkdir(exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2))
    print(f"Saved comparison to {args.output}")


if __name__ == "__main__":
    main()

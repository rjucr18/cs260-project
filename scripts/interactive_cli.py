"""Interactive CLI to demo SVEN secure vs vulnerable generation."""
import argparse

from models.codegen_wrapper import CodeGenWrapper


def main() -> int:
    ap = argparse.ArgumentParser(description="SVEN interactive CLI")
    ap.add_argument("--max-length", type=int, default=64)
    ap.add_argument("--temperature", type=float, default=0.8)
    args = ap.parse_args()

    print("Loading models...")
    secure = CodeGenWrapper(secure=True)
    vulnerable = CodeGenWrapper(secure=False)
    print("Ready. Type 'q' to quit.\n")

    while True:
        try:
            prompt = input("Prompt> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        
        if not prompt or prompt.strip().lower() in {"q", "quit", "exit"}:
            print("Bye.")
            break

        print("\n[Secure]")
        sec = secure.generate(prompt, max_length=args.max_length, temperature=args.temperature)
        print(sec.code.strip())

        print("\n[Vulnerable]")
        vul = vulnerable.generate(prompt, max_length=args.max_length, temperature=args.temperature)
        print(vul.code.strip())
        print("-" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

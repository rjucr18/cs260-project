"""Flask web app to demo SVEN secure vs vulnerable generation."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request

from models.codegen_wrapper import CodeGenWrapper


def create_app() -> Flask:
    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

    # Lazy load the wrappers on first request to avoid long startup time
    app.config["_SECURE_WRAPPER"] = None
    app.config["_VULNERABLE_WRAPPER"] = None

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/")
    def index():
        return render_template("index.html")

    def _get_wrappers():
        if app.config["_SECURE_WRAPPER"] is None:
            app.logger.info("Loading secure CodeGenWrapper...")
            app.config["_SECURE_WRAPPER"] = CodeGenWrapper(secure=True)
        if app.config["_VULNERABLE_WRAPPER"] is None:
            app.logger.info("Loading vulnerable CodeGenWrapper...")
            app.config["_VULNERABLE_WRAPPER"] = CodeGenWrapper(secure=False)
        return app.config["_SECURE_WRAPPER"], app.config["_VULNERABLE_WRAPPER"]

    @app.route("/generate", methods=["POST"]) 
    def generate():
        try:
            payload: Dict[str, Any] = request.get_json(silent=True) or request.form.to_dict()  # type: ignore
            prompt = str(payload.get("prompt", "")).strip()
            if not prompt:
                return jsonify({"error": "prompt is required"}), 400

            max_length = int(payload.get("max_length", 64))
            temperature = float(payload.get("temperature", 0.8))
            mode = str(payload.get("mode", "both")).lower()

            secure, vulnerable = _get_wrappers()

            result: Dict[str, Any] = {}
            if mode in ("secure", "both"):
                sec = secure.generate(prompt, max_length=max_length, temperature=temperature)
                result["secure"] = sec.code
                result["secure_meta"] = sec.metadata
            if mode in ("vulnerable", "both"):
                vul = vulnerable.generate(prompt, max_length=max_length, temperature=temperature)
                result["vulnerable"] = vul.code
                result["vulnerable_meta"] = vul.metadata

            return jsonify(result)
        except Exception as e:  # pragma: no cover
            return jsonify({"error": str(e)}), 500

    return app


def main() -> int:
    app = create_app()
    port = int(os.environ.get("PORT", "5000"))
    # Use debug only if explicitly enabled
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

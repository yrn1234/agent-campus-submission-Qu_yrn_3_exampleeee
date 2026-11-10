"""Generate live model traces through the authenticated Codex CLI.

Run from repository root: python examples/generate_codex.py
If the computer uses a proxy, set HTTPS_PROXY before running.
No account tokens or CLI stderr are written to examples/.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "codex-normal": ("年假需要提前多久申请？", [], "answered"),
    "codex-conflict": ("报销期限是多久？", [], "needs_clarification"),
    "codex-missing": ("火星办公室的停车费是多少？", [], "insufficient_information"),
    "codex-failure": ("年假需要提前多久申请？", ["--fail-tool", "read"], "tool_error"),
}
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
for name, (question, options, expected) in CASES.items():
    argv = [question, "--mode", "codex"] + options
    (ROOT / "examples" / (name + ".input.json")).write_text(
        json.dumps({"argv": argv}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "-X", "utf8", "-m", "src.cli"] + argv,
                            cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            encoding="utf-8", env=env, timeout=1200)
    if result.returncode:
        raise RuntimeError(name + " CLI exit " + str(result.returncode))
    output = json.loads(result.stdout)
    (ROOT / "examples" / (name + ".output.json")).write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(name, output["status"], "steps=" + str(len(output["trace"])), flush=True)
    if output["status"] != expected:
        raise RuntimeError(name + " expected " + expected + ", got " + output["status"])

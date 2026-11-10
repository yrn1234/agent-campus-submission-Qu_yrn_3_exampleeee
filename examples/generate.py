"""Regenerate real CLI observations and test log from repository root."""
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "normal": ["休年假要早几天提？", "--mode", "mock"],
    "conflict": ["报销期限是多久？", "--mode", "mock"],
    "missing": ["火星办公室的停车费是多少？", "--mode", "mock"],
    "failure": ["年假需要提前多久申请？", "--mode", "mock", "--fail-tool", "read"],
    "followup": ["还需要主管批准吗？", "--mode", "mock", "--history-file", "examples/history.json"],
}
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
for name, args in CASES.items():
    (ROOT / "examples" / (name + ".input.json")).write_text(
        json.dumps({"argv": args}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    process = subprocess.run([sys.executable, "-m", "src.cli"] + args, cwd=str(ROOT),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, encoding="utf-8")
    if process.returncode:
        raise RuntimeError(process.stderr)
    (ROOT / "examples" / (name + ".output.json")).write_text(process.stdout, encoding="utf-8")
test = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                      cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                      env=env, encoding="utf-8")
(ROOT / "examples" / "test-results.txt").write_text(test.stdout, encoding="utf-8")
if test.returncode:
    raise RuntimeError(test.stdout)
print("generated", len(CASES), "cases and test-results.txt")

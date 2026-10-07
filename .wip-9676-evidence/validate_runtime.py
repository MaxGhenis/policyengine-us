"""Record and validate the checkout and pinned core actually imported by CI."""

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import policyengine_us

root = Path.cwd().resolve()
module = Path(policyengine_us.__file__).resolve()
assert module.is_relative_to(root), (root, module)
core = importlib.metadata.version("policyengine-core")
assert core == "3.32.15", core
expected_sha = os.environ.get("EXPECTED_CODE_SHA")
sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
if expected_sha:
    assert sha == expected_sha, (sha, expected_sha)
source = (
    root
    / "policyengine_us/variables/gov/states/mo/dss/tanf/assistance_unit/mo_tanf_is_assistance_unit_member.py"
)
out = {
    "code_sha": sha,
    "policyengine_core": core,
    "policyengine_us_version": importlib.metadata.version("policyengine-us"),
    "policyengine_us_file": str(module),
    "python": platform.python_version(),
    "membership_formula_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
}
print(json.dumps(out, indent=2), flush=True)
Path(sys.argv[1]).write_text(json.dumps(out, indent=2))

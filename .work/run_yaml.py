"""Run one YAML file with core's runner and one fresh country system."""

import argparse
import os
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("path", type=Path)
parser.add_argument("--source", type=Path, default=Path.cwd())
args = parser.parse_args()
source = args.source.resolve()
sys.path.insert(0, str(source))
print(f"Loading {source}, process {os.getpid()}", flush=True)
import policyengine_us
from policyengine_us.system import system
from policyengine_core.tools.test_runner import run_tests

assert Path(policyengine_us.__file__).resolve().is_relative_to(source)
print(f"Model: {policyengine_us.__file__}", flush=True)
result = run_tests(system, [str(args.path.resolve())], {})
sys.stdout.flush()
sys.stderr.flush()
# Testing is finished; avoid collecting the entire parameter tree at exit.
os._exit(int(result))

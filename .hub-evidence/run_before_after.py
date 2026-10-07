import os
import pytest

path = ".hub-evidence/regression_before_after.py"
os.environ["FORM4952_BEFORE"] = "1"
print("BEFORE: prior saved formulas; cap case uses pre-build main formula", flush=True)
before = pytest.main([path, "-q", "--tb=short", "-p", "no:cacheprovider"])
assert before == 1, f"Expected prior-model regression failures, got {before}"
os.environ["FORM4952_BEFORE"] = "0"
print("AFTER: final branch formulas, same cases", flush=True)
after = pytest.main([path, "-q", "--tb=short", "-p", "no:cacheprovider"])
raise SystemExit(after)

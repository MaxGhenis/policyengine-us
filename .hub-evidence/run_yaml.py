import os
import sys
import time
import resource

start = time.perf_counter()
from policyengine_us.system import system
from policyengine_core.tools.test_runner import run_tests

assert len(sys.argv) == 2 and os.path.isfile(sys.argv[1]), "Single test file required"
result = run_tests(system, [os.path.abspath(sys.argv[1])], {"verbose": True})
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"LOCAL_RESOURCE wall_seconds={time.perf_counter()-start:.2f} max_rss_bytes={usage.ru_maxrss} user_seconds={usage.ru_utime:.2f} sys_seconds={usage.ru_stime:.2f}", flush=True)
sys.exit(result)

import os
import sys
import time
import resource

start = time.perf_counter()
import pytest

assert len(sys.argv) == 2 and os.path.isfile(sys.argv[1]), "Single test file required"
result = pytest.main([sys.argv[1], "-q", "--tb=short", "-p", "no:cacheprovider"])
usage = resource.getrusage(resource.RUSAGE_SELF)
print(f"LOCAL_RESOURCE wall_seconds={time.perf_counter()-start:.2f} max_rss_bytes={usage.ru_maxrss} user_seconds={usage.ru_utime:.2f} sys_seconds={usage.ru_stime:.2f}", flush=True)
sys.exit(result)

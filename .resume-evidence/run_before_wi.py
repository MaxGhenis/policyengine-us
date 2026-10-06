"""Read-only before run using the recovered pre-fix model and current regression cases."""
import sys
from pathlib import Path
before = Path('/Users/maxghenis/.subfleet/worktrees/20261006-083854-hub-fix-9621')
sys.path.insert(0, str(before))
import policyengine_us
from policyengine_core.scripts.policyengine_command import main
print('BEFORE MODEL:', policyengine_us.__file__, flush=True)
assert Path(policyengine_us.__file__).is_relative_to(before)
sys.argv = ['policyengine-core', 'test', str(Path.cwd() / '.resume-evidence/wi_standard_deduction_before.yaml'), '-c', 'policyengine_us']
raise SystemExit(main())

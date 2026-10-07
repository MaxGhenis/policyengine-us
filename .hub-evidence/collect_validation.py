import json
import re
from pathlib import Path

root = Path('.hub-evidence')
files = {
    'form4952-final.log': 'Federal Form 4952',
    'properties-final.log': 'Vectorized properties',
    'montana-separate.log': 'Montana separate limits and federal alias',
    'montana-allocation.log': 'Montana allocation',
    'virginia.log': 'Virginia allowed-interest exclusion',
    'new-york-fees.log': 'New York dependent fees',
    'arkansas-fees-fixed.log': 'Arkansas dependent fees',
    'california.log': 'California interest replacement',
    'new-york-phase-out.log': 'New York allowed-interest exclusion',
    'election.log': 'Schedule D election',
    'section911-dividends.log': 'Section 911 dividends',
    'section911-gain.log': 'Section 911 adjusted gain',
}
results = []
for name, description in files.items():
    path = root / name
    text = path.read_text() if path.exists() else ''
    passed = re.findall(r'(\d+) passed', text)
    failed = re.findall(r'(\d+) failed', text)
    metrics = re.findall(r'LOCAL_RESOURCE wall_seconds=([\d.]+) max_rss_bytes=(\d+)', text)
    results.append({
        'description': description, 'log': name,
        'passed': int(passed[-1]) if passed else None,
        'failed': int(failed[-1]) if failed else 0,
        'wall_seconds': float(metrics[-1][0]) if metrics else None,
        'max_rss_bytes': int(metrics[-1][1]) if metrics else None,
    })
(root / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))

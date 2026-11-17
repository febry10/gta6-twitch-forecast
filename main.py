import json, math, os
from pathlib import Path

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
Z = (-1.644853627, -0.67448975, 0.0, 0.67448975, 1.644853627)
IN = Path(os.getenv('MAKEFUN_INPUT_DIR', '/input'))
OUT = Path(os.getenv('MAKEFUN_OUTPUT_DIR', '/output'))

def percentile(values, p):
    if not values: return 1.0
    a = sorted(max(1.0, float(x)) for x in values)
    k = (len(a)-1)*p; lo = int(k); hi = min(lo+1, len(a)-1)
    return a[lo] + (a[hi]-a[lo])*(k-lo)

def estimate(case):
    first = max(1.0, float(case['known'][0]['viewers']))
    hist = [max(1.0, float(x['viewers'])) for x in case.get('history_hourly', [])]
    recent = hist[-24:] if hist else [first]
    logs = [math.log(x) for x in recent]
    drift = 0.0
    if len(logs) >= 4:
        drift = max(-0.08, min(0.08, (logs[-1]-logs[0])/max(1, len(logs)-1)))
    vol = 0.15
    if len(logs) > 3:
        mean = sum(logs)/len(logs)
        vol = max(0.10, min(0.32, math.sqrt(sum((x-mean)**2 for x in logs)/len(logs))))
    rows=[]
    for item in case['forecast']:
        h=item['hour']; distance=h-1
        center=math.log(first) + drift*distance
        spread=vol*math.sqrt(distance)*0.85
        qs=[max(1.0, min(1e9, math.exp(center+z*spread))) for z in Z]
        rows.append({'hour':h,'q':qs})
    return {'hours':rows}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in sorted(IN.glob('*.in')):
        case=json.loads(p.read_text())
        (OUT/(p.stem+'.out')).write_text(json.dumps(estimate(case), separators=(',',':'))+'\n')
if __name__=='__main__': main()

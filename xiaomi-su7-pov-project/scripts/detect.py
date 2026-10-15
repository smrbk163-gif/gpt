from pathlib import Path
import json,subprocess,os
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).resolve().parent.parent;files=json.loads((R/'inputs.json').read_text())
def one(i):
 tr=R/'analysis'/f'transforms-{i+1}.trf'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',files[i],'-map','0:v:0','-an','-filter_threads','1','-vf',f'format=yuv420p,vidstabdetect=shakiness=5:accuracy=9:stepsize=12:mincontrast=0.12:result={tr}','-f','null','-'],check=True,env={**os.environ,'OMP_NUM_THREADS':'1'});print('motion analysed',i+1,flush=True)
with ThreadPoolExecutor(max_workers=2) as p:list(p.map(one,[0,1]))

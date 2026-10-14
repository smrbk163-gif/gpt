from pathlib import Path
import json,random,math,wave,struct,subprocess
R=Path(__file__).resolve().parent.parent;sc=json.loads((R/'scenes.json').read_text());sr=44100;dur=(sc[-1]['start']+sc[-1]['frames'])/60;N=round(sr*dur);left=[0.0]*N;right=[0.0]*N;rng=random.Random(7308)
def add(start,length,fun,pan=0):
 for i in range(round(length*sr)):
  t=i/sr;n=round(start*sr)+i
  if 0<=n<N:
   v=fun(t,i/max(1,round(length*sr)-1));left[n]+=v*(1-pan);right[n]+=v*(1+pan)
for s in sc:
 st=s['start']/60;state=0
 for i in range(round(.33*sr)):
  p=i/(.33*sr);noise=rng.uniform(-1,1);state+=.28*(noise-state);n=round((st-.04)*sr)+i
  if 0<=n<N:
   v=state*.34*math.sin(math.pi*p)**2;pan=.2*(p*2-1);left[n]+=v*(1-pan);right[n]+=v*(1+pan)
 if any(c.isdigit() for c in s['value']):
  for j,t0 in enumerate([.10,.18,.26,.34,.43,.52,.62]):add(st+t0,.036,lambda t,p,j=j:.115*(math.sin(2*math.pi*(1600+j*85)*t)+.2*rng.uniform(-1,1))*math.exp(-130*t)*(1-math.exp(-1300*t)),pan=(-.06 if j%2 else .06))
 if s['kind']=='battery':
  for j in range(8):add(st+.32+j*.065,.045,lambda t,p,j=j:.13*math.sin(2*math.pi*(650+j*95)*t)*math.exp(-85*t)*(1-math.exp(-1000*t)))
 if s['kind'] in ['power','accel','speed']:add(st+.71,.30,lambda t,p:.27*math.sin(2*math.pi*(94-35*p)*t)*math.exp(-17*t)*(1-math.exp(-180*t)))
 elif s['kind'] in ['charge','panel','display']:add(st+.71,.22,lambda t,p:.13*(math.sin(2*math.pi*850*t)+.35*math.sin(2*math.pi*1700*t))*math.exp(-22*t)*(1-math.exp(-150*t)))
 else:add(st+.60,.20,lambda t,p:.18*math.sin(2*math.pi*125*t)*math.exp(-28*t)*(1-math.exp(-180*t)))
with wave.open(str(R/'public/sfx.wav'),'wb') as w:
 w.setparams((2,2,sr,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<hh',int(max(-.98,min(.98,l))*32767),int(max(-.98,min(.98,r))*32767)) for l,r in zip(left,right)))
vol='.76'+''.join(f'-.30*exp(-pow((t-{s["start"]/60+.42})/.32,2))' for s in sc)
m='/workspace/attachments/dc46c783-6ece-4f8c-bcb5-97560fdf5948/SXLLX_-_MAMA_MA_INSTRUMENTAL_Slowed_80038296.mp3'
fil=f"[0:a]atrim=duration={dur},asetpts=PTS-STARTPTS,volume='{vol}':eval=frame,afade=t=in:d=0.035,afade=t=out:st={dur-.25}:d=0.25[m];[1:a]volume=1.65[s];[m][s]amix=inputs=2:normalize=0,alimiter=limit=.93:level=false:latency=true[a]"
subprocess.run(['ffmpeg','-v','error','-y','-ss','4.55','-i',m,'-i',str(R/'public/sfx.wav'),'-filter_complex',fil,'-map','[a]','-c:a','aac','-b:a','256k',str(R/'public/soundtrack.m4a')],check=True)
(R/'sfx-timing.json').write_text(json.dumps({'rollClicksAfter':[.10,.18,.26,.34,.43,.52,.62],'counterSettleAfter':.71,'batteryCellClicksAfter':[.32+j*.065 for j in range(8)],'musicDipCenterAfter':.42,'musicDipWidth':.32,'musicBaseline':.76,'musicDipDepth':.30,'sfxGain':1.65,'seed':7308},indent=2))
print('audio ready',dur)

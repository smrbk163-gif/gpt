"""Original deterministic sound design. No third-party sound assets."""
from pathlib import Path
import math,random,struct,wave,json
SR=44100
ROOT=Path(__file__).resolve().parent.parent
rng=random.Random(3303)

def create(kind):
 data=[0.0]*SR
 def add(start,duration,fun):
  for i in range(int(duration*SR)):
   n=int(start*SR)+i
   if n>=SR:break
   data[n]+=fun(i/SR,i/max(1,int(duration*SR)-1))
 # Filtered moving air, with a smooth rise and tail.
 state=0.0;previous=0.0
 length=.34 if kind!='acceleration' else .64
 offset=0 if kind!='acceleration' else .12
 for i in range(int(length*SR)):
  t=i/SR;p=t/length;noise=rng.uniform(-1,1)
  cutoff=400+5600*(math.sin(math.pi*p)**1.5)
  alpha=1-math.exp(-2*math.pi*cutoff/SR)
  state+=alpha*(noise-state)
  high=state-previous*.93;previous=state
  data[int(offset*SR)+i]+=high*.20*math.sin(math.pi*p)**2
 def hit(t,p):
  f=90-35*p
  return .26*math.sin(2*math.pi*f*t)*math.exp(-20*t)*(1-math.exp(-150*t))
 if kind=='mass':
  add(.32,.42,hit)
  add(.60,.07,lambda t,p:.055*math.sin(2*math.pi*1800*t)*math.exp(-65*t))
 elif kind=='motors':
  for j,start in enumerate([5/30,8/30,11/30]):
   add(start,.12,lambda t,p,j=j:(.08*math.sin(2*math.pi*(1250+j*200)*t)+.035*rng.uniform(-1,1))*math.exp(-42*t)*(1-math.exp(-400*t)))
  add(.43,.24,lambda t,p:.10*math.sin(2*math.pi*125*t)*math.exp(-20*t)*(1-math.exp(-180*t)))
 elif kind=='telegram':
  add(.32,.22,lambda t,p:.10*math.sin(2*math.pi*110*t)*math.exp(-23*t)*(1-math.exp(-180*t)))
  add(.50,.08,lambda t,p:.045*math.sin(2*math.pi*1400*t)*math.exp(-48*t))
 else:
  add(.16,.58,lambda t,p:.06*math.sin(2*math.pi*(300*t+1100*t*t))*math.sin(math.pi*p)**2)
  add(.70,.25,hit)
 # Stereo width on air; arrival and impacts remain centered.
 with wave.open(str(ROOT/'public'/('sfx-'+kind+'.wav')),'wb') as w:
  w.setparams((2,2,SR,0,'NONE','not compressed'))
  frames=[]
  for i,v in enumerate(data):
   pan=.08*math.sin(i/SR*math.pi*3)
   frames.append(struct.pack('<hh',int(max(-.95,min(.95,v*(1-pan)))*32767),int(max(-.95,min(.95,v*(1+pan)))*32767)))
  w.writeframes(b''.join(frames))
for kind in ['mass','emotion','telegram']:create(kind)
(ROOT/'sfx-timing.json').write_text(json.dumps({'seed':3303,'mass':{'start':2.99,'impactAfter':.32},'emotion':{'start':8.87,'sweepAfter':.16},'telegram':{'start':16.95,'arrivalAfter':.32,'clickAfter':.5}},indent=2))

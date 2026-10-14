from pathlib import Path
import json,random,math,wave,struct,subprocess
r=Path(__file__).resolve().parent.parent;scenes=json.loads((r/'scenes.json').read_text());sr=44100;duration=(scenes[-1]['start']+scenes[-1]['frames'])/60;N=round(sr*duration);a=[0.0]*N;rng=random.Random(7307)
for j,s in enumerate(scenes):
 cut=s['start']/60;state=0
 for i in range(round(.22*sr)):
  p=i/(.22*sr);state+=.35*(rng.uniform(-1,1)-state);n=round((cut-.1)*sr)+i
  if 0<=n<N:a[n]+=.075*state*math.sin(math.pi*p)**2
 # Text settles 0.3 seconds after entrance, with a matched subtle tone.
 freq=95 if s['kind'] in ['power','accel','speed'] else 750 if s['kind'] in ['mirror','light','battery','charge'] else 170
 for i in range(round(.16*sr)):
  t=i/sr;n=round((cut+.30)*sr)+i
  if n<N:a[n]+=.075*math.sin(2*math.pi*freq*t)*math.exp(-32*t)*(1-math.exp(-250*t))
with wave.open(str(r/'public/sfx.wav'),'wb') as w:
 w.setparams((2,2,sr,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<hh',int(v*32767),int(v*32767)) for v in a))
m='/workspace/attachments/dc46c783-6ece-4f8c-bcb5-97560fdf5948/SXLLX_-_MAMA_MA_INSTRUMENTAL_Slowed_80038296.mp3'
subprocess.run(['ffmpeg','-v','error','-y','-ss','4.55','-i',m,'-i',str(r/'public/sfx.wav'),'-filter_complex',f'[0:a]atrim=duration={duration},asetpts=PTS-STARTPTS,volume=.76,afade=t=in:d=0.04,afade=t=out:st={duration-.25}:d=0.25[m];[m][1:a]amix=inputs=2:normalize=0,alimiter=limit=.93:level=false:latency=true[a]','-map','[a]','-c:a','aac','-b:a','192k',str(r/'public/soundtrack.m4a')],check=True)
print('duration',duration)

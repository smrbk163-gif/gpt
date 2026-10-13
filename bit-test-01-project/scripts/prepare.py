from pathlib import Path
import subprocess,json,math,wave,struct,random
root=Path(__file__).resolve().parent.parent
files=json.loads((root/'inputs.json').read_text())
shots=[('0019',.06,2.40,120),('0022',.05,2.24,120),('0021',.035,1.82,120),('0020',.05,2.10,119)]
plan=[]
for i,(name,start,end,n) in enumerate(shots):
 duration=n/60;span=end-start
 # Continuous monotonic source-to-output time mapping; speed is faster at both ends.
 pts=f'{duration}*((T-{start})/{span}-.70*sin(2*PI*(T-{start})/{span})/(2*PI))/TB'
 zoom=f'1.015+.012*sin(PI*on/{n-1})+.10*exp(-on/2.4)+.12*exp(-({n-1}-on)/2.4)'
 vf=f"trim=start={start}:end={end},setpts='{pts}',scale=1080:1920,framerate=fps=60:interp_start=15:interp_end=240:scene=100,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={n},zoompan=z='{zoom}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=60,eq=contrast=1.035:saturation=.94:brightness=.003,avgblur=sizeX=7:sizeY=1:enable='lt(t,.055)+gt(t,{duration-.055})',setsar=1"
 out=root/'public'/f'shot-{i+1}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',files[name],'-map','0:v:0','-an','-vf',vf,'-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
 plan.append(dict(source=name,startSourceSeconds=start,endSourceSeconds=end,outputFrames=n,speedProfile='Continuous sinusoidal time remap: rapid entry/exit, slow center',rampCoefficient=.70))
 print('prepared',name,flush=True)
(root/'edit-plan.json').write_text(json.dumps({'fps':60,'width':1080,'height':1920,'frames':479,'musicStartSeconds':4.514,'cutsFrames':[120,240,360],'shots':plan},indent=2))
# Original short stereo air swishes aligned to the approach and arrival of cuts.
sr=44100;N=round(479/60*sr);rng=random.Random(1210);sound=[0.0]*N
for cut in [2,4,6]:
 state=0
 for i in range(round(.22*sr)):
  t=i/sr;p=t/.22;noise=rng.uniform(-1,1);state+=.36*(noise-state)
  idx=round((cut-.14)*sr)+i
  sound[idx]+=state*.1*math.sin(math.pi*p)**2
 for i in range(round(.10*sr)):
  t=i/sr;idx=round(cut*sr)+i;sound[idx]+=.065*math.sin(2*math.pi*95*t)*math.exp(-45*t)*(1-math.exp(-400*t))
with wave.open(str(root/'public/transitions.wav'),'wb') as w:
 w.setparams((2,2,sr,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<hh',round(v*32767),round(v*32767)) for v in sound))
m=next(Path('/workspace/attachments/e8583e9f-7804-4993-a22c-874f67371d2e').glob('*.mp3'))
subprocess.run(['ffmpeg','-v','error','-y','-ss','4.514','-i',str(m),'-i',str(root/'public/transitions.wav'),'-filter_complex','[0:a]atrim=duration=7.983333,asetpts=PTS-STARTPTS,volume=.65,afade=t=in:d=0.015,afade=t=out:st=7.86:d=0.123333[m];[m][1:a]amix=inputs=2:normalize=0,alimiter=limit=.93:level=false:latency=true[a]','-map','[a]','-c:a','aac','-b:a','192k',str(root/'public/soundtrack.m4a')],check=True)

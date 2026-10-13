from pathlib import Path
import subprocess,json,math,wave,struct,random
root=Path(__file__).resolve().parent.parent
old=json.loads(Path('/workspace/work/beat/inputs.json').read_text())
shots=[('0019',old['0019'],.06,2.40,120,.70),('0022',old['0022'],.05,2.24,60,.55),('new-front',str(root/'public/stabilized-2.mp4'),.04,2.27,120,.60),('0021',old['0021'],.035,1.82,60,.55),('0020',old['0020'],.05,2.10,120,.70),('new-rear',str(root/'public/stabilized-1.mp4'),.05,4.20,240,.45),('new-exit',str(root/'public/stabilized-0.mp4'),.05,4.15,239,.30)]
plan=[];offset=0
for i,(name,path,start,end,n,k) in enumerate(shots):
 duration=n/60;span=end-start
 pts=f'{duration}*((T-{start})/{span}-{k}*sin(2*PI*(T-{start})/{span})/(2*PI))/TB'
 zoom=f'1.01+.010*sin(PI*on/{n-1})+.07*exp(-on/2.4)+.09*exp(-({n-1}-on)/2.4)'
 # Let the final moving exit breathe: no zoom punch or blur at its end.
 if i==6:zoom=f'1.01+.008*sin(PI*on/{n-1})+.07*exp(-on/2.4)'
 blur=f'lt(t,0.055)+gt(t,{duration-.055})' if i<6 else 'lt(t,0.055)'
 vf=f"trim=start={start}:end={end},setpts='{pts}',scale=1080:1920,framerate=fps=60:interp_start=15:interp_end=240:scene=100,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={n},zoompan=z='{zoom}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=60,eq=contrast=1.035:saturation=.94:brightness=.003,avgblur=sizeX=6:sizeY=1:enable='{blur}',setsar=1"
 out=root/'public'/f'shot-{i+1}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',path,'-map','0:v:0','-an','-vf',vf,'-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-map_metadata','-1','-write_tmcd','0','-movflags','+faststart',str(out)],check=True)
 plan.append(dict(name=name,startFrame=offset,outputFrames=n,startSourceSeconds=start,endSourceSeconds=end,rampCoefficient=k,stabilized=name.startswith('new-')));offset+=n;print('prepared',name,flush=True)
(root/'edit-plan.json').write_text(json.dumps({'fps':60,'width':1080,'height':1920,'frames':959,'musicStartSeconds':4.514,'cutsFrames':[120,180,300,360,480,720],'shots':plan,'stabilization':{'method':'two-pass vidstab','newClipsOnly':True,'smoothing':12,'maxShiftPx':20,'maxAngleRad':.012,'zoomPercent':4,'extraCrop':1.015}},indent=2))
sr=44100;N=round(959/60*sr);rng=random.Random(1210);sound=[0.0]*N
for cut in [2,3,5,6,8,12]:
 state=0
 for i in range(round(.22*sr)):
  t=i/sr;p=t/.22;noise=rng.uniform(-1,1);state+=.36*(noise-state);idx=round((cut-.14)*sr)+i;sound[idx]+=state*.10*math.sin(math.pi*p)**2
 for i in range(round(.10*sr)):
  t=i/sr;idx=round(cut*sr)+i;sound[idx]+=.06*math.sin(2*math.pi*95*t)*math.exp(-45*t)*(1-math.exp(-400*t))
with wave.open(str(root/'public/transitions.wav'),'wb') as w:
 w.setparams((2,2,sr,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<hh',round(v*32767),round(v*32767)) for v in sound))
m=next(Path('/workspace/attachments/e8583e9f-7804-4993-a22c-874f67371d2e').glob('*.mp3'))
subprocess.run(['ffmpeg','-v','error','-y','-ss','4.514','-i',str(m),'-i',str(root/'public/transitions.wav'),'-filter_complex','[0:a]atrim=duration=15.983333,asetpts=PTS-STARTPTS,volume=.65,afade=t=in:d=0.015,afade=t=out:st=15.79:d=0.193333[m];[m][1:a]amix=inputs=2:normalize=0,alimiter=limit=.93:level=false:latency=true[a]','-map','[a]','-c:a','aac','-b:a','192k',str(root/'public/soundtrack.m4a')],check=True)
(root/'concat.txt').write_text(''.join(f"file '{(root/'public'/f'shot-{i+1}.mp4').resolve()}'\n" for i in range(7)))

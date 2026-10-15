from pathlib import Path
import numpy as np,json,subprocess
from scipy.io.wavfile import write
R=Path(__file__).resolve().parent.parent;sr=48000;N={2:1717,1:1727};rng=np.random.default_rng(71)
for source in [2,1]:
 dur=N[source]/60;sfx=np.zeros((round(sr*dur),2),np.float32)
 def put(at,sound,gain=.1):
  i=round(at*sr);n=min(len(sound),len(sfx)-i)
  if i>=0 and n>0:sfx[i:i+n]+=sound[:n]*gain
 for j,c in enumerate(json.loads((R/f'cards-source-{source}.json').read_text())):
  t=np.arange(round(.32*sr))/sr;env=np.sin(np.pi*t/.32)**2;noise=rng.normal(0,1,len(t));noise=np.convolve(noise,np.ones(7)/7,'same');sw=(noise*.6+np.sin(2*np.pi*(360*t+620*t*t))*.17)*env
  pan=np.linspace(.85,.15,len(t)) if j%2 else np.linspace(.15,.85,len(t));put(c['start'],np.stack([sw*np.sqrt(pan),sw*np.sqrt(1-pan)],1),.12)
  t=np.arange(round(.23*sr))/sr;ping=(np.sin(2*np.pi*1320*t)+.4*np.sin(2*np.pi*1980*t))*np.exp(-t*24)*np.minimum(t/.008,1);put(c['start']+.42,np.stack([ping,ping],1),.035)
  if any(x.isdigit() for x in c['value']):
   for k in range(5):
    t=np.arange(round(.025*sr))/sr;tick=rng.normal(0,1,len(t))*np.exp(-t*190);put(c['start']+.1+k*.065,np.stack([tick,tick],1),.025)
 # Reduce graphic sound under speech without pumping the original voice.
 words=json.loads((R/f'captions-source-{source}.json').read_text());duck=np.ones(len(sfx),np.float32)
 for w in words:
  a=max(0,round((w['startMs']/1000-.08)*sr));b=min(len(duck),round((w['endMs']/1000+.10)*sr));duck[a:b]=.55
 sfx*=duck[:,None];write(R/f'analysis/sfx-{source}.wav',sr,sfx)
 files=json.loads((R/'inputs.json').read_text())
 subprocess.run(['ffmpeg','-v','error','-y','-i',files[source-1],'-i',str(R/f'analysis/sfx-{source}.wav'),'-filter_complex',f'[0:a]highpass=f=65,loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,apad,atrim=duration={dur}[v];[v][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=0[a]','-map','[a]','-c:a','pcm_s24le',str(R/f'analysis/mix-{source}.wav')],check=True)
(R/'analysis/audio-concat.txt').write_text(''.join(f"file '{R}/analysis/mix-{i}.wav'\n" for i in [2,1]))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(R/'analysis/audio-concat.txt'),'-c:a','aac','-b:a','256k',str(R/'public/soundtrack.m4a')],check=True)
print('Audio ready')
